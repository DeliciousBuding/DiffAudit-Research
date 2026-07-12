from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

from diffaudit.evidence.h1_extraction import (
    ActivationHookCollector,
    CheckpointProvenance,
    build_benchmark_summary,
    build_common_noise,
    compute_activation_features,
    extract_locked_rows,
    load_h1_feature_packet,
    sha256_file,
    validate_checkpoint_bundle,
    validate_h1_extraction_runtime,
    validate_h1_repository_state,
    write_h1_feature_packet,
)
from diffaudit.evidence.training_config import build_training_config


def _feature_definition(channels: int = 2) -> dict[str, object]:
    sites = ["late_down", "mid_0", "mid_1", "early_up"]
    timesteps = [100, 400, 700]
    return {
        "name": "sample_level_channel_statistics_v1",
        "sites": sites,
        "timesteps": timesteps,
        "channels_per_site": {site: channels for site in sites},
        "per_channel_statistics": ["mu_abs", "var", "sparsity"],
        "scalar_statistics": ["mu_abs_mean", "var_mean", "sparsity_mean"],
        "sparsity_threshold": "0.01_times_population_std_per_channel",
        "pca_feature_order": "site_then_timestep_then_statistic_then_channel",
        "scalar_feature_order": "timestep_then_site_then_statistic",
        "lr_feature_order": ["scalar_features", "pca_components"],
        "pca_input_dimension": len(sites) * len(timesteps) * 3 * channels,
        "scalar_feature_dimension": len(sites) * len(timesteps) * 3,
        "lr_input_dimension": 42,
        "input_range": [-1.0, 1.0],
    }


class _SiteBlock(nn.Module):
    def __init__(self, offset: float) -> None:
        super().__init__()
        self.offset = offset

    def forward(self, x: torch.Tensor, _temb: torch.Tensor | None = None) -> torch.Tensor:
        return x + self.offset


class _FakeModel(nn.Module):
    def __init__(self, *, nan_site: str | None = None, duplicate_site: str | None = None) -> None:
        super().__init__()
        self.downblocks = nn.ModuleList([_SiteBlock(1.0)])
        self.middleblocks = nn.ModuleList([_SiteBlock(2.0), _SiteBlock(3.0)])
        self.upblocks = nn.ModuleList([_SiteBlock(4.0)])
        self.nan_site = nan_site
        self.duplicate_site = duplicate_site

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        del t
        values = {
            "late_down": self.downblocks[-1](x),
            "mid_0": self.middleblocks[0](x),
            "mid_1": self.middleblocks[1](x),
            "early_up": self.upblocks[0](x),
        }
        if self.nan_site is not None:
            values[self.nan_site].view(-1)[0] = float("nan")
        if self.duplicate_site is not None:
            block = {
                "late_down": self.downblocks[-1],
                "mid_0": self.middleblocks[0],
                "mid_1": self.middleblocks[1],
                "early_up": self.upblocks[0],
            }[self.duplicate_site]
            block(x)
        return sum(value.mean() for value in values.values()).reshape(1)


class _IndexedDataset:
    def __init__(self) -> None:
        self.seen: list[int] = []

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        self.seen.append(index)
        return torch.full((2, 2, 2), index / 100.0), index % 10

    def __len__(self) -> int:
        return 50_000


def test_compute_activation_features_reproduces_sample_level_scout_statistics() -> None:
    definition = _feature_definition(channels=2)
    activations: dict[tuple[str, int], torch.Tensor] = {}
    base = torch.tensor(
        [
            [[[1.0, -1.0]], [[2.0, 2.0]]],
            [[[0.0, 0.0]], [[-3.0, 1.0]]],
        ]
    )
    for site in definition["sites"]:
        for timestep in definition["timesteps"]:
            activations[(site, timestep)] = base

    pca_features, scalar_features = compute_activation_features(activations, definition)

    assert pca_features.shape == (2, 72)
    assert scalar_features.shape == (2, 36)
    assert pca_features[0, :6].tolist() == pytest.approx([1.0, 2.0, 1.0, 0.0, 0.0, 0.0])
    assert scalar_features[0, :3].tolist() == pytest.approx([1.5, 0.5, 0.0])
    assert pca_features[1, :6].tolist() == pytest.approx([0.0, 2.0, 0.0, 4.0, 0.0, 0.0])
    assert scalar_features[1, :3].tolist() == pytest.approx([1.0, 2.0, 0.0])


def test_activation_feature_columns_lock_legacy_pca_and_scalar_orders() -> None:
    definition = _feature_definition(channels=2)
    sites = definition["sites"]
    timesteps = definition["timesteps"]
    activations: dict[tuple[str, int], torch.Tensor] = {}
    markers: dict[tuple[str, int], float] = {}
    for timestep_index, timestep in enumerate(timesteps):
        for site_index, site in enumerate(sites):
            marker = float(10 * timestep_index + site_index + 1)
            markers[(site, timestep)] = marker
            activations[(site, timestep)] = torch.tensor(
                [[[[0.0, marker]], [[0.0, marker]]]], dtype=torch.float32
            )

    pca_features, scalar_features = compute_activation_features(activations, definition)

    expected_scalar: list[float] = []
    for timestep in timesteps:
        for site in sites:
            marker = markers[(site, timestep)]
            expected_scalar.extend([marker / 2.0, marker**2 / 4.0, 0.5])
    assert scalar_features[0].tolist() == pytest.approx(expected_scalar)

    pca_block_width = 3 * 2
    expected_pca_mu_sentinels = [
        markers[(site, timestep)] / 2.0 for site in sites for timestep in timesteps
    ]
    actual_pca_mu_sentinels = [
        float(pca_features[0, block * pca_block_width])
        for block in range(len(expected_pca_mu_sentinels))
    ]
    assert actual_pca_mu_sentinels == pytest.approx(expected_pca_mu_sentinels)


def test_common_noise_is_row_bound_across_batch_order_and_checkpoint() -> None:
    shape = (2, 2, 2)
    first = build_common_noise(shape, "paper1-corrected-v1", [7, 11], 400, 0)
    reversed_rows = build_common_noise(shape, "paper1-corrected-v1", [11, 7], 400, 0)
    single = build_common_noise(shape, "paper1-corrected-v1", [7], 400, 0)

    assert torch.equal(first[0], reversed_rows[1])
    assert torch.equal(first[1], reversed_rows[0])
    assert torch.equal(first[0], single[0])


@pytest.mark.parametrize(
    ("model", "message"),
    [
        (_FakeModel(duplicate_site="mid_0"), "exactly one activation"),
        (_FakeModel(nan_site="early_up"), "finite"),
    ],
)
def test_hook_collector_rejects_duplicate_or_nonfinite_activations(
    model: _FakeModel, message: str
) -> None:
    with ActivationHookCollector(model) as collector:
        collector.begin_query(expected_batch=1)
        model(torch.zeros((1, 2, 2, 2)), torch.tensor([100]))
        with pytest.raises(ValueError, match=message):
            collector.finish_query()


def test_extract_locked_rows_uses_dataset_indices_and_is_order_independent() -> None:
    definition = _feature_definition(channels=2)
    locked = [
        {"dataset_index": 11, "label": 1, "class_id": 1, "split": "evaluation"},
        {"dataset_index": 7, "label": 0, "class_id": 7, "split": "calibration"},
    ]
    dataset = _IndexedDataset()
    model = _FakeModel()
    model.alphas_cumprod = torch.linspace(0.99, 0.01, 1000)

    result = extract_locked_rows(
        model,
        dataset,
        locked,
        feature_definition=definition,
        protocol_namespace="paper1-corrected-v1",
        batch_size=1,
        device=torch.device("cpu"),
    )
    reordered_result = extract_locked_rows(
        model,
        _IndexedDataset(),
        list(reversed(locked)),
        feature_definition=definition,
        protocol_namespace="paper1-corrected-v1",
        batch_size=2,
        device=torch.device("cpu"),
    )

    rows = result.rows
    reordered = reordered_result.rows
    assert result.pca_features.dtype == np.float32
    assert result.scalar_features.dtype == np.float32
    assert dataset.seen == [11, 7]
    assert [row["dataset_index"] for row in rows] == [11, 7]
    assert rows[0]["class"] == 1
    assert rows[0]["label"] == 1
    assert rows[0]["calibration_or_evaluation"] == "evaluation"
    by_index = {row["dataset_index"]: row for row in rows}
    reordered_by_index = {row["dataset_index"]: row for row in reordered}
    assert by_index[7]["noise_id"] == reordered_by_index[7]["noise_id"]
    left_index = [row["dataset_index"] for row in rows].index(7)
    right_index = [row["dataset_index"] for row in reordered].index(7)
    np.testing.assert_array_equal(
        result.pca_features[left_index], reordered_result.pca_features[right_index]
    )


def test_extract_rejects_dataset_that_is_already_normalized() -> None:
    class PreNormalizedDataset(_IndexedDataset):
        def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
            return torch.full((2, 2, 2), -1.0), index % 10

    model = _FakeModel()
    model.alphas_cumprod = torch.linspace(0.99, 0.01, 1000)
    with pytest.raises(ValueError, match="source range"):
        extract_locked_rows(
            model,
            PreNormalizedDataset(),
            [{"dataset_index": 7, "label": 0, "class_id": 7, "split": "calibration"}],
            feature_definition=_feature_definition(channels=2),
            protocol_namespace="paper1-corrected-v1",
            batch_size=1,
            device=torch.device("cpu"),
        )


def _checkpoint_fixture(tmp_path: Path) -> tuple[Path, Path, dict[str, object]]:
    metadata = {
        "run_label": "corrected-preflight-s1746574482",
        "seed": 1746574482,
        "protocol_hash": "a" * 64,
        "checkpoint_step": 2000,
        "split_sha256": "b" * 64,
        "code_commit": "c" * 40,
        "training_config": {"batch_size": 32},
        "training_config_hash": hashlib.sha256(
            json.dumps({"batch_size": 32}, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "environment": {
            "python": "3.12",
            "pytorch": "2.7",
            "cuda": None,
            "cudnn": None,
            "gpu_name": None,
            "gpu_uuid": None,
        },
    }
    checkpoint = {
        "model": {"weight": torch.ones(1)},
        "ema": {"weight": torch.ones(1)},
        "optim": {},
        "sched": {},
        "step": 2000,
        "metadata": metadata,
        "rng_state": {},
    }
    checkpoint_path = tmp_path / "checkpoint-step002000.pt"
    torch.save(checkpoint, checkpoint_path)
    checkpoint_sha256 = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
    receipt = {
        "checkpoint_sha256": checkpoint_sha256,
        "protocol_hash": metadata["protocol_hash"],
        "code_commit": metadata["code_commit"],
        "run_seed": metadata["seed"],
        "step": 2000,
        "run_label": metadata["run_label"],
        "training_config_hash": metadata["training_config_hash"],
    }
    manifest = {
        "protocol_hash": metadata["protocol_hash"],
        "split_sha256": metadata["split_sha256"],
        "code_commit": metadata["code_commit"],
        "seed": metadata["seed"],
        "run_label": metadata["run_label"],
        "step": 2000,
        "checkpoint": checkpoint_path.name,
        "member_count": 25_000,
        "batch_size": 32,
        "training_config": metadata["training_config"],
        "training_config_hash": metadata["training_config_hash"],
        "environment": metadata["environment"],
        "checkpoint_receipts": {checkpoint_path.name: receipt},
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return checkpoint_path, manifest_path, metadata


def test_checkpoint_validation_cross_checks_weights_only_metadata_and_receipt(
    tmp_path: Path,
) -> None:
    checkpoint_path, manifest_path, metadata = _checkpoint_fixture(tmp_path)

    bundle = validate_checkpoint_bundle(
        checkpoint_path,
        manifest_path,
        expected_protocol_hash=str(metadata["protocol_hash"]),
        expected_split_sha256=str(metadata["split_sha256"]),
        expected_target_code_commit=str(metadata["code_commit"]),
        expected_training_config_hash=str(metadata["training_config_hash"]),
        packet_purpose="preflight_benchmark",
        preflight=True,
    )

    assert isinstance(bundle.provenance, CheckpointProvenance)
    assert bundle.provenance.step == 2000
    assert (
        bundle.provenance.training_manifest_sha256
        == hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    )


def test_checkpoint_tamper_is_rejected(tmp_path: Path) -> None:
    checkpoint_path, manifest_path, metadata = _checkpoint_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["checkpoint_receipts"][checkpoint_path.name]["step"] = 1999
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="receipt"):
        validate_checkpoint_bundle(
            checkpoint_path,
            manifest_path,
            expected_protocol_hash=str(metadata["protocol_hash"]),
            expected_split_sha256=str(metadata["split_sha256"]),
            expected_target_code_commit=str(metadata["code_commit"]),
            expected_training_config_hash=str(metadata["training_config_hash"]),
            packet_purpose="preflight_benchmark",
            preflight=True,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("environment", {"python": "tampered"}),
        ("member_count", 24_999),
        ("batch_size", 64),
        ("seed", 7),
        ("run_label", "corrected-preflight-s7"),
        ("step", 1999),
        ("protocol_hash", "f" * 64),
        ("split_sha256", "f" * 64),
        ("training_config", {"batch_size": 64}),
        ("training_config_hash", "f" * 64),
    ],
)
def test_checkpoint_validation_rejects_every_manifest_duplicate_field_tamper(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    checkpoint_path, manifest_path, metadata = _checkpoint_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[field] = value
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="manifest|checkpoint identity|config"):
        validate_checkpoint_bundle(
            checkpoint_path,
            manifest_path,
            expected_protocol_hash=str(metadata["protocol_hash"]),
            expected_split_sha256=str(metadata["split_sha256"]),
            expected_target_code_commit=str(metadata["code_commit"]),
            expected_training_config_hash=str(metadata["training_config_hash"]),
            packet_purpose="preflight_benchmark",
            preflight=True,
        )


def test_checkpoint_validation_rejects_extra_manifest_fields(tmp_path: Path) -> None:
    checkpoint_path, manifest_path, metadata = _checkpoint_fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["unexpected"] = True
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="manifest fields"):
        validate_checkpoint_bundle(
            checkpoint_path,
            manifest_path,
            expected_protocol_hash=str(metadata["protocol_hash"]),
            expected_split_sha256=str(metadata["split_sha256"]),
            expected_target_code_commit=str(metadata["code_commit"]),
            expected_training_config_hash=str(metadata["training_config_hash"]),
            packet_purpose="preflight_benchmark",
            preflight=True,
        )


@pytest.mark.parametrize(
    ("state", "message"),
    [
        (("d" * 40, "", ()), "HEAD"),
        (("e" * 40, " M src/diffaudit/evidence/h1_extraction.py", ()), "tracked"),
        (("e" * 40, "", ("scripts/h1/injected.py",)), "untracked"),
    ],
)
def test_repository_gate_rejects_head_dirty_or_relevant_untracked(
    state: tuple[str, str, tuple[str, ...]], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_h1_repository_state(*state, expected_scorer_commit="e" * 40)


def _small_packet() -> tuple[dict[str, object], list[dict[str, object]], np.ndarray, np.ndarray]:
    provenance = {
        "dataset_id": "CIFAR10",
        "run_seed": 1746574482,
        "step": 2000,
        "attack": "H1",
        "checkpoint_sha256": "a" * 64,
        "training_manifest_sha256": "b" * 64,
        "target_code_commit": "c" * 40,
        "scorer_code_commit": "d" * 40,
        "split_sha256": "e" * 64,
        "protocol_hash": "f" * 64,
        "run_label": "corrected-preflight-s1746574482",
    }
    rows = [
        {
            "dataset_index": 7,
            "label": 0,
            "class": 7,
            "calibration_or_evaluation": "calibration",
            "noise_id": {"namespace": "n", "dataset_index": 7, "entries": []},
        },
        {
            "dataset_index": 11,
            "label": 1,
            "class": 1,
            "calibration_or_evaluation": "evaluation",
            "noise_id": {"namespace": "n", "dataset_index": 11, "entries": []},
        },
    ]
    return (
        provenance,
        rows,
        np.arange(12, dtype=np.float32).reshape(2, 6),
        np.ones((2, 3), np.float32),
    )


def test_atomic_packet_write_leaves_no_output_on_validation_failure(tmp_path: Path) -> None:
    output = tmp_path / "packet"
    provenance, rows, pca_features, scalar_features = _small_packet()
    pca_features[0, 0] = np.nan

    with pytest.raises(ValueError, match="finite JSON"):
        write_h1_feature_packet(
            output,
            packet_purpose="preflight_benchmark",
            provenance=provenance,
            rows=rows,
            pca_features=pca_features,
            scalar_features=scalar_features,
        )

    assert not output.exists()
    assert not list(tmp_path.rglob("*.tmp"))


def test_benchmark_summary_is_outcome_blind() -> None:
    phase_timings = {
        "identity_protocol": 1.0,
        "checkpoint_hash_load": 2.0,
        "model_to_device": 3.0,
        "dataset_load": 4.0,
        "extraction": 12.5,
        "packet_write_hash": 5.0,
    }
    summary = build_benchmark_summary(
        rows=2048,
        queries=6144,
        end_to_end_seconds=27.5,
        extraction_seconds=12.5,
        phase_timings=phase_timings,
        peak_cuda_allocated_bytes=100,
        peak_cuda_reserved_bytes=200,
        packet_path="outputs/h1-preflight",
        packet_sha256="a" * 64,
    )

    assert set(summary) == {
        "rows",
        "queries",
        "end_to_end_seconds",
        "extraction_seconds",
        "phase_timings",
        "rows_per_second",
        "peak_cuda_allocated_bytes",
        "peak_cuda_reserved_bytes",
        "packet_path",
        "packet_sha256",
    }
    serialized = json.dumps(summary).lower()
    assert all(token not in serialized for token in ("auc", "tpr", "accuracy", "metric", "outcome"))
    assert summary["phase_timings"] == phase_timings


@pytest.mark.parametrize(
    ("batch_size", "device", "environment_mutation", "message"),
    [
        (1, "cuda", None, "batch_size"),
        (2, "cuda", None, "batch_size"),
        (16, "cpu", None, "device_policy"),
        (16, "cuda", ("python", "0.0"), "evaluator_environment"),
    ],
)
def test_extraction_runtime_rejects_batch_device_or_environment_drift(
    batch_size: int,
    device: str,
    environment_mutation: tuple[str, object] | None,
    message: str,
) -> None:
    environment = {
        "python": "3.12",
        "pytorch": "2.7",
        "cuda": "12.8",
        "cudnn": 90100,
        "gpu_name": "GPU",
        "gpu_uuid": "uuid",
    }
    extraction_config = {
        "batch_size": 16,
        "device_policy": "cuda_required_for_confirmatory",
        "determinism": dict(build_training_config().determinism),
        "evaluator_environment": deepcopy(environment),
    }
    if environment_mutation is not None:
        environment[environment_mutation[0]] = environment_mutation[1]

    with pytest.raises(ValueError, match=message):
        validate_h1_extraction_runtime(
            extraction_config,
            batch_size=batch_size,
            device=device,
            evaluator_environment=environment,
        )


def test_feature_packet_round_trip_binds_rows_to_float32_npz(tmp_path: Path) -> None:
    output = tmp_path / "packet"
    provenance, rows, pca_features, scalar_features = _small_packet()

    manifest = write_h1_feature_packet(
        output,
        packet_purpose="preflight_benchmark",
        provenance=provenance,
        rows=rows,
        pca_features=pca_features,
        scalar_features=scalar_features,
    )
    loaded = load_h1_feature_packet(output)

    assert manifest["packet_format"] == "h1-feature-packet-v2"
    assert loaded["packet_purpose"] == "preflight_benchmark"
    assert loaded["provenance"] == provenance
    assert loaded["rows"] == rows
    assert loaded["pca_features"].dtype == np.float32
    assert np.array_equal(loaded["pca_features"], pca_features)
    assert np.array_equal(loaded["scalar_features"], scalar_features)


def test_streaming_hash_handles_large_file_without_path_read_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = bytes(range(256)) * (17 * 1024 * 1024 // 256)
    path = tmp_path / "large.bin"
    path.write_bytes(payload)
    monkeypatch.setattr(
        Path,
        "read_bytes",
        lambda _self: (_ for _ in ()).throw(AssertionError("read_bytes is forbidden")),
    )

    assert sha256_file(path) == hashlib.sha256(payload).hexdigest()


def test_npz_loader_hashes_and_loads_through_one_seekable_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "packet"
    provenance, rows, pca_features, scalar_features = _small_packet()
    write_h1_feature_packet(
        output,
        packet_purpose="preflight_benchmark",
        provenance=provenance,
        rows=rows,
        pca_features=pca_features,
        scalar_features=scalar_features,
    )
    original_open = Path.open
    feature_opens = 0

    def count_open(path: Path, *args: object, **kwargs: object):
        nonlocal feature_opens
        if path == output / "features.npz":
            feature_opens += 1
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", count_open)
    load_h1_feature_packet(output)

    assert feature_opens == 1


@pytest.mark.parametrize("mutation", ["tamper", "truncate", "row_reorder", "swap"])
def test_feature_packet_loader_rejects_file_or_row_alignment_tamper(
    tmp_path: Path, mutation: str
) -> None:
    provenance, rows, pca_features, scalar_features = _small_packet()
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_h1_feature_packet(
        left,
        packet_purpose="preflight_benchmark",
        provenance=provenance,
        rows=rows,
        pca_features=pca_features,
        scalar_features=scalar_features,
    )
    changed_provenance = deepcopy(provenance)
    changed_provenance["checkpoint_sha256"] = "9" * 64
    write_h1_feature_packet(
        right,
        packet_purpose="preflight_benchmark",
        provenance=changed_provenance,
        rows=rows,
        pca_features=pca_features + 100,
        scalar_features=scalar_features,
    )
    if mutation == "tamper":
        with (left / "features.npz").open("ab") as handle:
            handle.write(b"tamper")
    elif mutation == "truncate":
        payload = (left / "features.npz").read_bytes()
        (left / "features.npz").write_bytes(payload[: len(payload) // 2])
    elif mutation == "row_reorder":
        manifest = json.loads((left / "manifest.json").read_text(encoding="utf-8"))
        manifest["rows"].reverse()
        (left / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    else:
        (left / "features.npz").write_bytes((right / "features.npz").read_bytes())

    with pytest.raises(ValueError, match="hash|row alignment|NPZ"):
        load_h1_feature_packet(left)
