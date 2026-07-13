from __future__ import annotations

import hashlib
import io
import json
import subprocess
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from diffaudit.attacks import pia_adapter
from diffaudit.attacks.pia_canonical import (
    load_pia_protocol_context,
    load_pia_training_identity,
    validate_pia_score_packet_pair,
)
from diffaudit.cli import main
from diffaudit.cli._parser import build_parser
from diffaudit.config import load_audit_config
from diffaudit.evidence.corrected_protocol import (
    build_paper1_corrected_contract,
    build_protocol_envelope,
)
from diffaudit.training.corrected_ddpm import build_training_config, canonical_training_config_hash

RESEARCH_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = RESEARCH_ROOT / "configs" / "attacks" / "pia-mainline-canonical.yaml"
CODE_COMMIT = "c" * 40
SPLIT_SHA256 = "d" * 64
CHECKPOINT_SHA256 = "e" * 64
INVALID_PREFLIGHT_IDENTITY_CASES = (
    ("corrected_evaluation", 0, 2_000),
    ("preflight_benchmark", 1, 2_000),
    ("preflight_benchmark", 0, 2_001),
    ("preflight_benchmark", 0, 100_000),
)


def _training_manifest_payload(
    envelope: dict[str, object],
    checkpoint_sha256: str = CHECKPOINT_SHA256,
    *,
    seed: int | None = None,
    step: int = 100_000,
) -> dict[str, object]:
    contract = envelope["contract"]
    roster = contract["h1"]["cross_target_rosters"]["stage1"]
    run_seed = roster["seeds"][0] if seed is None else seed
    run_label = f"corrected-preflight-s{run_seed}" if step == 2_000 else f"corrected-s{run_seed}"
    config_hash = canonical_training_config_hash(build_training_config())
    checkpoint_name = f"checkpoint-step{step:06d}.pt"
    return {
        "protocol_hash": envelope["protocol_hash"],
        "split_sha256": SPLIT_SHA256,
        "code_commit": CODE_COMMIT,
        "seed": run_seed,
        "run_label": run_label,
        "step": step,
        "checkpoint": checkpoint_name,
        "training_config_hash": config_hash,
        "checkpoint_receipts": {
            checkpoint_name: {
                "checkpoint_sha256": checkpoint_sha256,
                "protocol_hash": envelope["protocol_hash"],
                "code_commit": CODE_COMMIT,
                "run_seed": run_seed,
                "step": step,
                "run_label": run_label,
                "training_config_hash": config_hash,
            }
        },
    }


def _training_manifest_bytes(
    envelope: dict[str, object],
    checkpoint_sha256: str = CHECKPOINT_SHA256,
    *,
    seed: int | None = None,
    step: int = 100_000,
) -> bytes:
    return json.dumps(
        _training_manifest_payload(
            envelope,
            checkpoint_sha256,
            seed=seed,
            step=step,
        )
    ).encode("utf-8")


def _canonical_noise_id(protocol_hash: str, dataset_index: int) -> str:
    payload = json.dumps(
        [protocol_hash, dataset_index, 200, "pia-e0"],
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@pytest.fixture(scope="module")
def protocol_envelope() -> dict[str, object]:
    contract = build_paper1_corrected_contract(
        split_filename="CIFAR10_train_ratio0.5.npz",
        split_sha256=SPLIT_SHA256,
        member_indices=tuple(range(25_000)),
        nonmember_indices=tuple(range(25_000, 50_000)),
        class_labels=np.arange(50_000, dtype=np.int64) % 10,
        code_commit=CODE_COMMIT,
    )
    return build_protocol_envelope(contract)


@pytest.fixture
def protocol_manifest(tmp_path: Path, protocol_envelope: dict[str, object]) -> Path:
    path = tmp_path / "protocol.json"
    path.write_text(json.dumps(protocol_envelope), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def sealed_repository_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pia_adapter,
        "read_pia_repository_state",
        lambda _root: (CODE_COMMIT, "", ()),
    )


def _packet(
    envelope: dict[str, object],
    *,
    role: str,
    purpose: str = "corrected_evaluation",
    run_seed: int | None = None,
    step: int = 100_000,
    checkpoint_sha256: str = CHECKPOINT_SHA256,
) -> dict[str, object]:
    contract = envelope["contract"]
    assert isinstance(contract, dict)
    h1 = contract["h1"]
    assert isinstance(h1, dict)
    rosters = h1["cross_target_rosters"]
    assert isinstance(rosters, dict)
    stage1 = rosters["stage1"]
    assert isinstance(stage1, dict)
    seeds = stage1["seeds"]
    assert isinstance(seeds, list)
    protocol_hash = envelope["protocol_hash"]
    assert isinstance(protocol_hash, str)
    manifest = contract["evaluation"]
    assert isinstance(manifest, dict)
    manifest_rows = manifest["rows"]
    assert isinstance(manifest_rows, list)
    rows = []
    for raw_row in manifest_rows:
        assert isinstance(raw_row, dict)
        if raw_row["split"] != role:
            continue
        label = raw_row["label"]
        assert isinstance(label, int)
        dataset_index = raw_row["dataset_index"]
        assert isinstance(dataset_index, int)
        rows.append(
            {
                "dataset_id": "CIFAR10",
                "dataset_index": dataset_index,
                "label": label,
                "class": raw_row["class_id"],
                "calibration_or_evaluation": role,
                "score": 0.9 if label == 1 else 0.1,
                "noise_id": _canonical_noise_id(protocol_hash, dataset_index),
            }
        )
    packet_seed = seeds[0] if run_seed is None else run_seed
    pia_contract = contract["pia"]
    extraction_contract = pia_contract["extraction"]
    upstream_contract = pia_contract["upstream"]
    config_hash = canonical_training_config_hash(build_training_config())
    checkpoint_filename = f"checkpoint-step{step:06d}.pt"
    run_label = (
        f"corrected-preflight-s{packet_seed}"
        if purpose == "preflight_benchmark"
        else f"corrected-s{packet_seed}"
    )
    return {
        "schema_version": 2,
        "attack": "pia",
        "variant": "pia",
        "timestep": 200,
        "lp_order": 4,
        "score_form": "negative_lp_norm",
        "score_direction": "higher_is_member",
        "input_range": [-1.0, 1.0],
        "packet_purpose": purpose,
        "run_seed": packet_seed,
        "step": step,
        "checkpoint_sha256": checkpoint_sha256,
        "training_manifest_sha256": hashlib.sha256(
            _training_manifest_bytes(
                envelope,
                checkpoint_sha256,
                seed=int(packet_seed),
                step=step,
            )
        ).hexdigest(),
        "target_code_commit": CODE_COMMIT,
        "scorer_code_commit": CODE_COMMIT,
        "split_sha256": SPLIT_SHA256,
        "protocol_hash": protocol_hash,
        "extraction": {
            "packet_purpose": purpose,
            "device": extraction_contract["device"],
            "batch_size": extraction_contract["batch_size"],
            "weights_key": extraction_contract["weights_key"],
            "evaluator_environment": extraction_contract["evaluator_environment"],
            "upstream": {
                **upstream_contract,
                "git_clean": True,
            },
            "checkpoint_filename": checkpoint_filename,
            "run_label": run_label,
            "training_config_hash": config_hash,
        },
        "rows": rows,
    }


def _write_packet(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _write_packet_pair(
    tmp_path: Path,
    envelope: dict[str, object],
    *,
    purpose: str = "corrected_evaluation",
    run_seed: int | None = None,
    step: int = 100_000,
) -> tuple[Path, Path]:
    return (
        _write_packet(
            tmp_path / "calibration.json",
            _packet(
                envelope,
                role="calibration",
                purpose=purpose,
                run_seed=run_seed,
                step=step,
            ),
        ),
        _write_packet(
            tmp_path / "evaluation.json",
            _packet(
                envelope,
                role="evaluation",
                purpose=purpose,
                run_seed=run_seed,
                step=step,
            ),
        ),
    )


def _write_corrected_checkpoint_and_manifest(
    tmp_path: Path,
    envelope: dict[str, object],
    *,
    step: int = 100_000,
    seed: int | None = None,
    model_state_dict: dict[str, torch.Tensor] | None = None,
    ema_state_dict: dict[str, torch.Tensor] | None = None,
) -> tuple[Path, Path, str, str]:
    contract = envelope["contract"]
    assert isinstance(contract, dict)
    roster = contract["h1"]["cross_target_rosters"]["stage1"]
    run_seed = roster["seeds"][0] if seed is None else seed
    run_label = f"corrected-preflight-s{run_seed}" if step == 2_000 else f"corrected-s{run_seed}"
    config_hash = canonical_training_config_hash(build_training_config())
    checkpoint = tmp_path / f"checkpoint-step{step:06d}.pt"
    corrected_model_weights = {} if model_state_dict is None else model_state_dict
    corrected_ema_weights = corrected_model_weights if ema_state_dict is None else ema_state_dict
    torch.save(
        {
            "model": corrected_model_weights,
            "ema": corrected_ema_weights,
            "optim": {"state": {}, "param_groups": []},
            "sched": {},
            "step": step,
            "metadata": {
                "run_label": run_label,
                "seed": run_seed,
                "protocol_hash": envelope["protocol_hash"],
                "checkpoint_step": step,
                "split_sha256": SPLIT_SHA256,
                "code_commit": CODE_COMMIT,
                "training_config": build_training_config().to_dict(),
                "training_config_hash": config_hash,
                "environment": {},
            },
            "rng_state": {},
        },
        checkpoint,
    )
    checkpoint_sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    manifest = tmp_path / "training-manifest.json"
    manifest.write_bytes(
        _training_manifest_bytes(
            envelope,
            checkpoint_sha,
            seed=int(run_seed),
            step=step,
        )
    )
    return checkpoint, manifest, checkpoint_sha, hashlib.sha256(manifest.read_bytes()).hexdigest()


def _canonical_config_for_model_dir(model_dir: Path):
    config = load_audit_config(CANONICAL_CONFIG)
    return replace(config, assets=replace(config.assets, model_dir=str(model_dir)))


def _sealed_upstream_verification(envelope: dict[str, object]) -> dict[str, object]:
    contract = envelope["contract"]
    assert isinstance(contract, dict)
    return {**contract["pia"]["upstream"], "git_clean": True}


def _assert_metric_free_export_receipt(receipt: dict[str, object], *, expected_stage: str) -> None:
    assert receipt["status"] == "score_packet_exported"
    assert receipt["stage"] == expected_stage
    assert receipt["packet_sha256"]
    assert receipt["raw_score_packet_status"] == "embargoed"
    assert "metrics" not in receipt and "scores" not in receipt
    assert (
        "did not compute/display/inspect aggregate metrics or score contents"
        in receipt["outcome_boundary"]
    )


def _stub_canonical_export_assets(
    monkeypatch: pytest.MonkeyPatch,
    envelope: dict[str, object],
    tmp_path: Path,
    checkpoint: Path,
    *,
    modules: tuple[object, object] | None = None,
) -> None:
    monkeypatch.setattr(pia_adapter, "validate_pia_workspace", lambda _path: {"status": "ready"})
    monkeypatch.setattr(
        pia_adapter,
        "validate_canonical_pia_workspace",
        lambda *_args: _sealed_upstream_verification(envelope),
        raising=False,
    )
    monkeypatch.setattr(
        pia_adapter,
        "probe_pia_assets",
        lambda **_kwargs: {
            "status": "ready",
            "paths": {
                "checkpoint": str(checkpoint),
                "dataset_dir": str(tmp_path / "dataset"),
                "member_split": str(tmp_path / "unused.npz"),
            },
            "checks": {"checkpoint": True},
        },
    )
    if modules is not None:

        def load_verified_modules(
            _root: str | Path, *, required_file_sha256: object = None
        ) -> tuple[object, object]:
            contract = envelope["contract"]
            assert isinstance(contract, dict)
            assert required_file_sha256 == contract["pia"]["upstream"]["required_file_sha256"]
            return modules

        monkeypatch.setattr(pia_adapter, "load_pia_ddpm_modules", load_verified_modules)


def _stub_canonical_packet_loader(
    monkeypatch: pytest.MonkeyPatch,
    envelope: dict[str, object],
    *,
    member_value: float = 0.0,
    nonmember_value: float = 0.0,
) -> None:
    contract = envelope["contract"]
    assert isinstance(contract, dict)
    by_index = {int(row["dataset_index"]): row for row in contract["evaluation"]["rows"]}

    def fake_loader(
        dataset: str,
        dataset_dir: str | Path,
        packet_indices: list[int],
        batch_size: int,
    ) -> DataLoader:
        del dataset, dataset_dir
        values = torch.zeros(len(packet_indices), 3, 2, 2)
        values[:, 0, 0, 0] = torch.tensor(
            [
                member_value if by_index[index]["label"] == 1 else nonmember_value
                for index in packet_indices
            ]
        )
        labels = torch.tensor([by_index[index]["class_id"] for index in packet_indices])
        return DataLoader(TensorDataset(values, labels), batch_size=batch_size, shuffle=False)

    monkeypatch.setattr(pia_adapter, "_build_pia_packet_loader", fake_loader)


def _run_canonical_cli(
    workspace: Path,
    *,
    protocol_manifest: Path,
    protocol_hash: str,
    calibration_packet: Path | None,
    evaluation_packet: Path | None,
    checkpoint_sha256: str = CHECKPOINT_SHA256,
    training_output_manifest: Path | None = None,
    extra_args: list[str] | None = None,
) -> int:
    if training_output_manifest is None:
        envelope = json.loads(protocol_manifest.read_text(encoding="utf-8"))
        training_output_manifest = workspace.parent / "training-manifest.json"
        training_output_manifest.write_bytes(_training_manifest_bytes(envelope, checkpoint_sha256))
    argv = [
        "run-pia-runtime-mainline",
        "--config",
        str(CANONICAL_CONFIG),
        "--workspace",
        str(workspace),
        "--protocol-manifest",
        str(protocol_manifest),
        "--expected-protocol-hash",
        protocol_hash,
        "--training-output-manifest",
        str(training_output_manifest),
    ]
    if calibration_packet is not None:
        argv.extend(["--calibration-score-packet", str(calibration_packet)])
    if evaluation_packet is not None:
        argv.extend(["--evaluation-score-packet", str(evaluation_packet)])
    argv.extend(extra_args or [])
    return main(argv)


def test_corrected_packets_are_rejected_before_single_pair_metrics(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    workspace = tmp_path / "success"

    with pytest.raises(ValueError, match="corrected_evaluation.*complete-roster"):
        _run_canonical_cli(
            workspace,
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )

    assert capsys.readouterr().out == ""
    assert not workspace.exists()


def test_preflight_packets_validate_but_runtime_evaluator_never_computes_or_emits_metrics(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    identity = contract["pia"]["preflight_identity"]
    seed = int(identity["run_seed"])
    step = int(identity["step"])
    checkpoint_sha256 = CHECKPOINT_SHA256
    training_manifest = tmp_path / "preflight-training-manifest.json"
    training_manifest.write_bytes(
        _training_manifest_bytes(
            protocol_envelope,
            checkpoint_sha256,
            seed=seed,
            step=step,
        )
    )
    calibration, evaluation = _write_packet_pair(
        tmp_path,
        protocol_envelope,
        purpose="preflight_benchmark",
        run_seed=seed,
        step=step,
    )
    context = load_pia_protocol_context(
        protocol_manifest,
        expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
    )
    validated, _ = validate_pia_score_packet_pair(
        calibration,
        evaluation,
        context=context,
        training_output_manifest=training_manifest,
    )
    assert validated.provenance["packet_purpose"] == "preflight_benchmark"
    workspace = tmp_path / "preflight-evaluator-must-not-exist"

    with pytest.raises(ValueError, match="preflight_benchmark.*export-only"):
        _run_canonical_cli(
            workspace,
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
            training_output_manifest=training_manifest,
        )

    assert capsys.readouterr().out == ""
    assert not workspace.exists()


@pytest.mark.parametrize(
    ("purpose", "seed_offset", "step"),
    INVALID_PREFLIGHT_IDENTITY_CASES,
)
def test_preflight_packet_identity_rejects_wrong_purpose_seed_step_and_relabeling(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    purpose: str,
    seed_offset: int,
    step: int,
) -> None:
    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    seeds = contract["training"]["seeds"]
    seed = int(seeds[seed_offset])
    training_manifest = tmp_path / "identity-training-manifest.json"
    training_manifest.write_bytes(
        _training_manifest_bytes(
            protocol_envelope,
            seed=seed,
            step=step,
        )
    )
    calibration, evaluation = _write_packet_pair(
        tmp_path,
        protocol_envelope,
        purpose=purpose,
        run_seed=seed,
        step=step,
    )

    with pytest.raises(ValueError, match="preflight|sealed|stage|identity"):
        _run_canonical_cli(
            tmp_path / "identity-must-not-exist",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
            training_output_manifest=training_manifest,
        )


def test_canonical_upstream_validation_checks_origin_head_cleanliness_and_file_hashes(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
) -> None:
    repo = tmp_path / "PIA"
    required_files = (
        "DDPM/attack.py",
        "DDPM/components.py",
        "DDPM/dataset_utils.py",
        "DDPM/model.py",
    )
    hashes: dict[str, str] = {}
    for index, relative in enumerate(required_files):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"UPSTREAM_VALUE = {index}\n".encode("ascii"))
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "PIA Test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "pia@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "add", "DDPM"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
    repository_url = "https://github.com/kong13661/PIA.git"
    subprocess.run(["git", "remote", "add", "origin", repository_url], cwd=repo, check=True)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    pia_contract = deepcopy(protocol_envelope["contract"]["pia"])
    pia_contract["upstream"] = {
        "repository_url": repository_url,
        "commit": commit,
        "required_file_sha256": hashes,
    }

    verified = pia_adapter.validate_canonical_pia_workspace(repo, pia_contract)
    assert verified["git_clean"] is True
    assert verified["commit"] == commit

    (repo / "untracked.py").write_text("drift\n", encoding="utf-8")
    with pytest.raises(ValueError, match="clean"):
        pia_adapter.validate_canonical_pia_workspace(repo, pia_contract)
    (repo / "untracked.py").unlink()

    wrong_origin = deepcopy(pia_contract)
    wrong_origin["upstream"]["repository_url"] = "https://example.invalid/PIA.git"
    with pytest.raises(ValueError, match="origin"):
        pia_adapter.validate_canonical_pia_workspace(repo, wrong_origin)

    wrong_head = deepcopy(pia_contract)
    wrong_head["upstream"]["commit"] = "f" * 40
    with pytest.raises(ValueError, match="HEAD"):
        pia_adapter.validate_canonical_pia_workspace(repo, wrong_head)

    wrong_hash = deepcopy(pia_contract)
    wrong_hash["upstream"]["required_file_sha256"]["DDPM/model.py"] = "f" * 64
    with pytest.raises(ValueError, match="SHA256"):
        pia_adapter.validate_canonical_pia_workspace(repo, wrong_hash)

    (repo / "DDPM/model.py").write_text(
        "raise AssertionError('unverified source executed')\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="verified source SHA256"):
        pia_adapter.load_pia_ddpm_modules(
            repo,
            required_file_sha256=hashes,
        )


@pytest.mark.parametrize("missing", ["calibration", "evaluation"])
def test_cli_rejects_a_missing_canonical_score_packet(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    missing: str,
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    with pytest.raises(ValueError, match="requires both calibration and evaluation"):
        _run_canonical_cli(
            tmp_path / f"missing-{missing}",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=None if missing == "calibration" else calibration,
            evaluation_packet=None if missing == "evaluation" else evaluation,
        )


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda packet: packet.update(schema_version=True), "schema_version"),
        (lambda packet: packet.update(attack="PIA"), "attack"),
        (lambda packet: packet.update(run_seed=True), "run_seed"),
        (lambda packet: packet.update(step=123), "step"),
        (lambda packet: packet.update(checkpoint_sha256="f" * 64), "checkpoint"),
        (
            lambda packet: packet.update(training_manifest_sha256="f" * 64),
            "training_manifest_sha256",
        ),
        (lambda packet: packet.update(target_code_commit="f" * 40), "target_code_commit"),
        (lambda packet: packet.update(scorer_code_commit="f" * 40), "scorer_code_commit"),
        (lambda packet: packet.update(split_sha256="f" * 64), "split_sha256"),
        (lambda packet: packet.update(protocol_hash="f" * 64), "protocol_hash"),
        (lambda packet: packet["extraction"].update(batch_size=7), "extraction.batch_size"),
        (lambda packet: packet["extraction"].update(device="cuda"), "extraction.device"),
        (lambda packet: packet["extraction"].update(weights_key="model"), "weights_key"),
        (
            lambda packet: packet["extraction"].update(packet_purpose="cpu_positive_control"),
            "extraction.packet_purpose",
        ),
        (
            lambda packet: packet["extraction"]["upstream"].update(git_clean=False),
            "git_clean",
        ),
        (lambda packet: packet.update(extra="forbidden"), "fields"),
        (lambda packet: packet.pop("score_form"), "fields"),
        (lambda packet: packet["rows"][0].update(noise_id="arbitrary"), "noise_id"),
        (lambda packet: packet["rows"][0].update(label=True), "label"),
        (lambda packet: packet["rows"][0].update(score=float("nan")), "finite"),
        (lambda packet: packet["rows"][0].update(extra="forbidden"), "row fields"),
        (lambda packet: packet["rows"].pop(), "locked rows"),
    ],
)
def test_cli_rejects_schema_provenance_and_row_drift(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    mutation: Any,
    match: str,
) -> None:
    calibration_payload = _packet(protocol_envelope, role="calibration")
    evaluation_payload = _packet(protocol_envelope, role="evaluation")
    mutation(evaluation_payload)
    calibration = _write_packet(tmp_path / "calibration.json", calibration_payload)
    evaluation = _write_packet(tmp_path / "evaluation.json", evaluation_payload)

    with pytest.raises(ValueError, match=match):
        _run_canonical_cli(
            tmp_path / "drift",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )


def test_cli_rejects_duplicate_json_keys_and_duplicate_rows(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    text = evaluation.read_text(encoding="utf-8")
    evaluation.write_text(
        text.replace('"attack": "pia"', '"attack": "pia", "attack": "pia"', 1),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate JSON key"):
        _run_canonical_cli(
            tmp_path / "duplicate-key",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )

    duplicated_payload = _packet(protocol_envelope, role="evaluation")
    rows = duplicated_payload["rows"]
    assert isinstance(rows, list)
    rows[1] = deepcopy(rows[0])
    evaluation = _write_packet(tmp_path / "duplicated-row.json", duplicated_payload)
    with pytest.raises(ValueError, match="duplicate|locked rows"):
        _run_canonical_cli(
            tmp_path / "duplicate-row",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )


def test_cli_rejects_cross_packet_overlap_and_provenance_drift(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
) -> None:
    calibration_payload = _packet(protocol_envelope, role="calibration")
    evaluation_payload = _packet(protocol_envelope, role="evaluation")
    cal_rows = calibration_payload["rows"]
    eval_rows = evaluation_payload["rows"]
    assert isinstance(cal_rows, list) and isinstance(eval_rows, list)
    eval_rows[0]["dataset_index"] = cal_rows[0]["dataset_index"]
    eval_rows[0]["noise_id"] = cal_rows[0]["noise_id"]
    calibration = _write_packet(tmp_path / "calibration.json", calibration_payload)
    evaluation = _write_packet(tmp_path / "evaluation.json", evaluation_payload)
    with pytest.raises(ValueError, match="overlap|locked manifest"):
        _run_canonical_cli(
            tmp_path / "overlap",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )

    h1 = protocol_envelope["contract"]["h1"]
    second_seed = h1["cross_target_rosters"]["stage1"]["seeds"][1]
    evaluation_payload = _packet(
        protocol_envelope,
        role="evaluation",
        run_seed=second_seed,
    )
    evaluation = _write_packet(tmp_path / "provenance-drift.json", evaluation_payload)
    with pytest.raises(ValueError, match="provenance|training_manifest_sha256"):
        _run_canonical_cli(
            tmp_path / "provenance",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )


def test_cli_rejects_a_self_signed_protocol_hash(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    with pytest.raises(ValueError, match="trusted expected_protocol_hash"):
        _run_canonical_cli(
            tmp_path / "self-signed",
            protocol_manifest=protocol_manifest,
            protocol_hash="f" * 64,
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )


def test_cli_rejects_legacy_single_pair_positive_control_packets(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calibration, evaluation = _write_packet_pair(
        tmp_path,
        protocol_envelope,
        purpose="cpu_positive_control",
    )
    workspace = tmp_path / "positive-control"
    with pytest.raises(ValueError, match="packet_purpose"):
        _run_canonical_cli(
            workspace,
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )

    assert capsys.readouterr().out == ""
    assert not workspace.exists()


@pytest.mark.parametrize(
    "legacy_flags",
    [
        ["--repo-root", "external/PIA"],
        ["--member-split-root", "external/PIA/DDPM"],
        ["--device", "cpu"],
        ["--max-samples", "8"],
        ["--batch-size", "8"],
        ["--stochastic-dropout-defense"],
        ["--dropout-activation-schedule", "off"],
        ["--adaptive-query-repeats", "1"],
        ["--epsilon-precision-bins", "32"],
        ["--late-step-threshold", "200"],
        ["--provenance-status", "workspace-verified"],
    ],
)
def test_canonical_cli_explicitly_rejects_every_legacy_runtime_flag(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    legacy_flags: list[str],
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    with pytest.raises(ValueError, match="legacy runtime flag"):
        _run_canonical_cli(
            tmp_path / "legacy-flag",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
            extra_args=legacy_flags,
        )


def test_corrected_exporter_packets_require_formal_complete_roster_analysis(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    checkpoint, training_manifest, checkpoint_sha256, training_manifest_sha256 = (
        _write_corrected_checkpoint_and_manifest(tmp_path, protocol_envelope)
    )

    _stub_canonical_export_assets(
        monkeypatch,
        protocol_envelope,
        tmp_path,
        checkpoint,
        modules=(object(), object()),
    )
    monkeypatch.setattr(
        pia_adapter,
        "read_pia_repository_state",
        lambda _root: (CODE_COMMIT, "", ()),
    )
    monkeypatch.setattr(
        pia_adapter,
        "load_pia_model",
        lambda *_args, **_kwargs: (torch.nn.Identity(), "ema"),
    )
    monkeypatch.setattr(
        pia_adapter,
        "_build_pia_attacker",
        lambda **_kwargs: lambda batch: batch[:, 0, 0, 0],
    )
    _stub_canonical_packet_loader(
        monkeypatch, protocol_envelope, member_value=0.9, nonmember_value=0.1
    )
    config = _canonical_config_for_model_dir(tmp_path)
    common = {
        "repo_root": tmp_path / "repo",
        "member_split_root": tmp_path / "unused",
        "device": "cpu",
        "batch_size": 8,
        "protocol_manifest": protocol_manifest,
        "expected_protocol_hash": str(protocol_envelope["protocol_hash"]),
        "training_output_manifest": training_manifest,
        "packet_purpose": "corrected_evaluation",
    }
    calibration_result = pia_adapter.export_pia_packet_scores(
        config,
        tmp_path / "export-calibration",
        calibration_or_evaluation="calibration",
        **common,
    )
    evaluation_result = pia_adapter.export_pia_packet_scores(
        config,
        tmp_path / "export-evaluation",
        calibration_or_evaluation="evaluation",
        **common,
    )
    calibration_packet = Path(calibration_result["artifact_paths"]["score_packet"])
    evaluation_packet = Path(evaluation_result["artifact_paths"]["score_packet"])
    exported = json.loads(calibration_packet.read_text(encoding="utf-8"))
    assert exported["training_manifest_sha256"] == training_manifest_sha256

    evaluation_workspace = tmp_path / "evaluate-export"
    with pytest.raises(ValueError, match="corrected_evaluation.*complete-roster"):
        _run_canonical_cli(
            evaluation_workspace,
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration_packet,
            evaluation_packet=evaluation_packet,
            training_output_manifest=training_manifest,
        )

    assert capsys.readouterr().out == ""
    assert not evaluation_workspace.exists()


@pytest.mark.parametrize(
    ("packet_purpose", "step", "expected_stage"),
    [
        ("corrected_evaluation", 100_000, "stage1"),
        ("preflight_benchmark", 2_000, "preflight"),
    ],
)
def test_canonical_exporter_uses_manifest_checkpoint_and_corrected_ema_weights(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    packet_purpose: str,
    step: int,
    expected_stage: str,
) -> None:
    online_model = torch.nn.Linear(1, 1)
    with torch.no_grad():
        online_model.weight.fill_(-2.0)
        online_model.bias.fill_(-3.0)
    expected_model = torch.nn.Linear(1, 1)
    with torch.no_grad():
        expected_model.weight.fill_(2.0)
        expected_model.bias.fill_(3.0)
    checkpoint, training_manifest, _, _ = _write_corrected_checkpoint_and_manifest(
        tmp_path,
        protocol_envelope,
        step=step,
        model_state_dict=online_model.state_dict(),
        ema_state_dict=expected_model.state_dict(),
    )
    decoy_checkpoint = tmp_path / "checkpoint.pt"
    decoy_checkpoint.write_bytes(b"must-never-be-loaded")

    class TinyModelModule:
        @staticmethod
        def UNet(**_kwargs: object) -> torch.nn.Module:
            return torch.nn.Linear(1, 1)

    _stub_canonical_export_assets(
        monkeypatch,
        protocol_envelope,
        tmp_path,
        decoy_checkpoint,
        modules=(object(), TinyModelModule),
    )

    real_load_pia_model = pia_adapter.load_pia_model
    loaded_weight_keys: list[str] = []
    transient_model = torch.nn.Linear(1, 1)
    with torch.no_grad():
        transient_model.weight.fill_(9.0)
        transient_model.bias.fill_(9.0)
    transient_buffer = io.BytesIO()
    torch.save({"ema": transient_model.state_dict()}, transient_buffer)
    transient_checkpoint = transient_buffer.getvalue()

    def capture_load_pia_model(*args: Any, **kwargs: Any) -> tuple[torch.nn.Module, str]:
        assert kwargs["weights_only"] is True
        original_checkpoint = checkpoint.read_bytes()
        checkpoint.write_bytes(transient_checkpoint)
        try:
            model, weights_key = real_load_pia_model(*args, **kwargs)
        finally:
            checkpoint.write_bytes(original_checkpoint)
        loaded_weight_keys.append(weights_key)
        return model, weights_key

    monkeypatch.setattr(pia_adapter, "load_pia_model", capture_load_pia_model)

    loaded_models: list[torch.nn.Module] = []

    def fake_attacker(**kwargs: object):
        model = kwargs["model"]
        assert isinstance(model, torch.nn.Linear)
        loaded_models.append(model)
        return lambda batch: batch[:, 0, 0, 0]

    monkeypatch.setattr(pia_adapter, "_build_pia_attacker", fake_attacker)
    _stub_canonical_packet_loader(monkeypatch, protocol_envelope)

    result = pia_adapter.export_pia_packet_scores(
        _canonical_config_for_model_dir(tmp_path),
        tmp_path / "export-corrected-checkpoint",
        repo_root=tmp_path / "repo",
        member_split_root=tmp_path / "unused",
        device="cpu",
        batch_size=8,
        protocol_manifest=protocol_manifest,
        expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
        training_output_manifest=training_manifest,
        packet_purpose=packet_purpose,
        calibration_or_evaluation="calibration",
    )

    _assert_metric_free_export_receipt(result, expected_stage=expected_stage)
    assert (
        result["packet_sha256"]
        == hashlib.sha256(Path(result["artifact_paths"]["score_packet"]).read_bytes()).hexdigest()
    )
    assert result["elapsed_seconds"] > 0
    persisted = json.loads(Path(result["artifact_paths"]["summary"]).read_text(encoding="utf-8"))
    assert persisted == result
    assert loaded_weight_keys == ["ema"]
    assert len(loaded_models) == 1
    assert torch.equal(loaded_models[0].weight, expected_model.weight)
    assert torch.equal(loaded_models[0].bias, expected_model.bias)
    assert not torch.equal(loaded_models[0].weight, online_model.weight)
    assert not torch.equal(loaded_models[0].bias, online_model.bias)


def test_preflight_cli_emits_the_persisted_metric_free_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    receipt = {
        "status": "score_packet_exported",
        "stage": "preflight",
        "packet_sha256": "a" * 64,
        "raw_score_packet_status": "embargoed",
        "outcome_boundary": (
            "generated and sealed raw score packet, but did not compute/display/inspect "
            "aggregate metrics or score contents"
        ),
    }

    def fake_export(_config: object, workspace: str | Path, **kwargs: object) -> dict[str, object]:
        assert kwargs["batch_size"] == 8
        assert kwargs["packet_purpose"] == "preflight_benchmark"
        destination = Path(workspace)
        destination.mkdir(parents=True)
        (destination / "summary.json").write_text(json.dumps(receipt), encoding="utf-8")
        return receipt

    monkeypatch.setattr(pia_adapter, "export_pia_packet_scores", fake_export)
    workspace = tmp_path / "preflight-cli-export"
    assert (
        main(
            [
                "export-pia-packet-scores",
                "--config",
                str(CANONICAL_CONFIG),
                "--workspace",
                str(workspace),
                "--protocol-manifest",
                str(tmp_path / "protocol.json"),
                "--expected-protocol-hash",
                "b" * 64,
                "--training-output-manifest",
                str(tmp_path / "training-manifest.json"),
                "--packet-purpose",
                "preflight_benchmark",
                "--calibration-or-evaluation",
                "evaluation",
            ]
        )
        == 0
    )
    emitted = json.loads(capsys.readouterr().out)
    persisted = json.loads((workspace / "summary.json").read_text(encoding="utf-8"))
    assert emitted == persisted
    _assert_metric_free_export_receipt(emitted, expected_stage="preflight")


@pytest.mark.parametrize(
    ("packet_purpose", "seed_offset", "step"),
    INVALID_PREFLIGHT_IDENTITY_CASES,
)
def test_preflight_exporter_rejects_identity_relabeling_before_upstream_import_or_model_load(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    packet_purpose: str,
    seed_offset: int,
    step: int,
) -> None:
    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    seed = int(contract["training"]["seeds"][seed_offset])
    checkpoint, training_manifest, _, _ = _write_corrected_checkpoint_and_manifest(
        tmp_path,
        protocol_envelope,
        seed=seed,
        step=step,
    )
    _stub_canonical_export_assets(monkeypatch, protocol_envelope, tmp_path, checkpoint)

    def fail_if_import_starts(*_args: object, **_kwargs: object):
        raise AssertionError("identity validation must finish before upstream import")

    monkeypatch.setattr(pia_adapter, "load_pia_ddpm_modules", fail_if_import_starts)
    with pytest.raises(ValueError, match="preflight|stage|identity"):
        pia_adapter.export_pia_packet_scores(
            _canonical_config_for_model_dir(tmp_path),
            tmp_path / "must-not-exist",
            repo_root=tmp_path / "repo",
            member_split_root=tmp_path / "unused",
            device="cpu",
            batch_size=8,
            protocol_manifest=protocol_manifest,
            expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
            training_output_manifest=training_manifest,
            packet_purpose=packet_purpose,
            calibration_or_evaluation="calibration",
        )


def test_canonical_exporter_rejects_batch_upstream_and_model_dir_drift_before_import(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkpoint, training_manifest, _, _ = _write_corrected_checkpoint_and_manifest(
        tmp_path, protocol_envelope
    )
    _stub_canonical_export_assets(monkeypatch, protocol_envelope, tmp_path, checkpoint)

    def fail_if_import_starts(*_args: object, **_kwargs: object):
        raise AssertionError("pre-import contract gate was bypassed")

    monkeypatch.setattr(pia_adapter, "load_pia_ddpm_modules", fail_if_import_starts)
    common = {
        "workspace": tmp_path / "must-not-exist",
        "repo_root": tmp_path / "repo",
        "member_split_root": tmp_path / "unused",
        "device": "cpu",
        "protocol_manifest": protocol_manifest,
        "expected_protocol_hash": str(protocol_envelope["protocol_hash"]),
        "training_output_manifest": training_manifest,
        "packet_purpose": "corrected_evaluation",
        "calibration_or_evaluation": "calibration",
    }

    with pytest.raises(ValueError, match="batch_size"):
        pia_adapter.export_pia_packet_scores(
            _canonical_config_for_model_dir(tmp_path), batch_size=7, **common
        )

    monkeypatch.setattr(
        pia_adapter,
        "validate_canonical_pia_workspace",
        lambda *_args: (_ for _ in ()).throw(ValueError("canonical PIA upstream HEAD mismatch")),
        raising=False,
    )
    with pytest.raises(ValueError, match="upstream HEAD"):
        pia_adapter.export_pia_packet_scores(
            _canonical_config_for_model_dir(tmp_path), batch_size=8, **common
        )

    monkeypatch.setattr(
        pia_adapter,
        "validate_canonical_pia_workspace",
        lambda *_args: _sealed_upstream_verification(protocol_envelope),
        raising=False,
    )
    with pytest.raises(ValueError, match="model_dir"):
        pia_adapter.export_pia_packet_scores(
            _canonical_config_for_model_dir(tmp_path / "other-model-dir"),
            batch_size=8,
            **common,
        )


@pytest.mark.parametrize("drift", ["checkpoint", "upstream"])
def test_canonical_exporter_revalidates_live_inputs_after_scoring_before_writing(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    drift: str,
) -> None:
    checkpoint, training_manifest, _, _ = _write_corrected_checkpoint_and_manifest(
        tmp_path, protocol_envelope, step=2_000
    )
    _stub_canonical_export_assets(
        monkeypatch,
        protocol_envelope,
        tmp_path,
        checkpoint,
        modules=(object(), object()),
    )
    monkeypatch.setattr(
        pia_adapter,
        "load_pia_model",
        lambda *_args, **_kwargs: (torch.nn.Identity(), "ema"),
    )
    monkeypatch.setattr(
        pia_adapter,
        "_build_pia_attacker",
        lambda **_kwargs: lambda batch: batch[:, 0, 0, 0],
    )
    _stub_canonical_packet_loader(monkeypatch, protocol_envelope)
    real_score_loader = pia_adapter._score_loader

    def score_then_drift(*args: object, **kwargs: object):
        result = real_score_loader(*args, **kwargs)
        if drift == "checkpoint":
            checkpoint.write_bytes(b"changed-during-score-export")
        return result

    monkeypatch.setattr(pia_adapter, "_score_loader", score_then_drift)
    validation_calls = 0

    def validate_live_upstream(*_args: object) -> dict[str, object]:
        nonlocal validation_calls
        validation_calls += 1
        if drift == "upstream" and validation_calls == 2:
            raise ValueError("canonical PIA upstream changed during score export")
        return _sealed_upstream_verification(protocol_envelope)

    monkeypatch.setattr(pia_adapter, "validate_canonical_pia_workspace", validate_live_upstream)
    workspace = tmp_path / "must-not-exist"
    with pytest.raises(ValueError, match=f"{drift} changed during score export"):
        pia_adapter.export_pia_packet_scores(
            _canonical_config_for_model_dir(tmp_path),
            workspace,
            repo_root=tmp_path / "repo",
            member_split_root=tmp_path / "unused",
            device="cpu",
            batch_size=8,
            protocol_manifest=protocol_manifest,
            expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
            training_output_manifest=training_manifest,
            packet_purpose="preflight_benchmark",
            calibration_or_evaluation="evaluation",
        )

    assert validation_calls == (1 if drift == "checkpoint" else 2)
    assert not workspace.exists()


def test_canonical_exporter_rejects_manifest_checkpoint_traversal_before_import(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, training_manifest, _, _ = _write_corrected_checkpoint_and_manifest(
        tmp_path, protocol_envelope
    )
    payload = json.loads(training_manifest.read_text(encoding="utf-8"))
    payload["checkpoint"] = "../checkpoint-step100000.pt"
    training_manifest.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(
        pia_adapter,
        "validate_canonical_pia_workspace",
        lambda *_args: _sealed_upstream_verification(protocol_envelope),
        raising=False,
    )

    def fail_if_import_starts(*_args: object, **_kwargs: object):
        raise AssertionError("unsafe checkpoint path must reject before import")

    monkeypatch.setattr(pia_adapter, "load_pia_ddpm_modules", fail_if_import_starts)
    with pytest.raises(ValueError, match="safe basename"):
        pia_adapter.export_pia_packet_scores(
            _canonical_config_for_model_dir(tmp_path),
            tmp_path / "must-not-exist",
            repo_root=tmp_path / "repo",
            device="cpu",
            batch_size=8,
            protocol_manifest=protocol_manifest,
            expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
            training_output_manifest=training_manifest,
            packet_purpose="corrected_evaluation",
            calibration_or_evaluation="calibration",
        )


def test_canonical_cli_parser_accepts_training_manifest_without_identity_labels() -> None:
    args = build_parser().parse_args(
        [
            "export-pia-packet-scores",
            "--config",
            str(CANONICAL_CONFIG),
            "--workspace",
            "out",
            "--protocol-manifest",
            "protocol.json",
            "--expected-protocol-hash",
            "a" * 64,
            "--training-output-manifest",
            "manifest.json",
            "--packet-purpose",
            "corrected_evaluation",
            "--calibration-or-evaluation",
            "calibration",
        ]
    )

    assert args.training_output_manifest == "manifest.json"
    assert args.batch_size == 8
    assert args.stage is None
    assert args.run_seed is None
    assert args.step is None


@pytest.mark.parametrize(
    ("repository_state", "match"),
    [
        (("f" * 40, "", ()), "HEAD"),
        ((CODE_COMMIT, " M src/diffaudit/attacks/pia.py", ()), "tracked worktree"),
        ((CODE_COMMIT, "", ("src/injected.py",)), "untracked scorer code"),
    ],
)
def test_canonical_exporter_rejects_repository_identity_before_writing_output(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    repository_state: tuple[str, str, tuple[str, ...]],
    match: str,
) -> None:
    monkeypatch.setattr(pia_adapter, "read_pia_repository_state", lambda _root: repository_state)
    workspace = tmp_path / "must-not-exist"

    with pytest.raises(ValueError, match=match):
        pia_adapter.export_pia_packet_scores(
            load_audit_config(CANONICAL_CONFIG),
            workspace,
            protocol_manifest=protocol_manifest,
            expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
            training_output_manifest=tmp_path / "unused-manifest.json",
            batch_size=8,
            packet_purpose="corrected_evaluation",
            calibration_or_evaluation="calibration",
        )

    assert not workspace.exists()


@pytest.mark.parametrize(
    ("repository_state", "match"),
    [
        (("f" * 40, "", ()), "HEAD"),
        ((CODE_COMMIT, " M src/diffaudit/attacks/pia.py", ()), "tracked worktree"),
        ((CODE_COMMIT, "", ("configs/injected.yaml",)), "untracked scorer code"),
    ],
)
def test_canonical_evaluator_rejects_repository_identity_before_writing_output(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    repository_state: tuple[str, str, tuple[str, ...]],
    match: str,
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    calls: list[Path] = []

    def fake_repository_state(root: Path) -> tuple[str, str, tuple[str, ...]]:
        calls.append(root)
        return repository_state

    monkeypatch.setattr(pia_adapter, "read_pia_repository_state", fake_repository_state)
    workspace = tmp_path / "evaluator-must-not-exist"

    with pytest.raises(ValueError, match=match):
        _run_canonical_cli(
            workspace,
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )

    assert calls == [pia_adapter.RESEARCH_ROOT]
    assert not workspace.exists()


@pytest.mark.parametrize(
    "identity_args",
    [
        {"expected_checkpoint_sha256": CHECKPOINT_SHA256},
        {"stage": "stage1"},
        {"run_seed": 1},
        {"step": 100_000},
    ],
)
def test_canonical_exporter_rejects_cli_supplied_checkpoint_identity(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    identity_args: dict[str, object],
) -> None:
    with pytest.raises(ValueError, match="rejects CLI identity fields"):
        pia_adapter.export_pia_packet_scores(
            load_audit_config(CANONICAL_CONFIG),
            tmp_path / "must-not-exist",
            protocol_manifest=protocol_manifest,
            expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
            training_output_manifest=tmp_path / "unused-manifest.json",
            packet_purpose="corrected_evaluation",
            calibration_or_evaluation="calibration",
            **identity_args,
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "arbitrary-bytes",
        "receipt-sha",
        "checkpoint-relabel",
        "seed-relabel",
        "step-relabel",
    ],
)
def test_checkpoint_and_training_receipt_identity_tampering_is_rejected(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    mutation: str,
) -> None:
    checkpoint, manifest, _, _ = _write_corrected_checkpoint_and_manifest(
        tmp_path, protocol_envelope
    )
    if mutation == "arbitrary-bytes":
        checkpoint.write_bytes(b"not-a-corrected-checkpoint")
    elif mutation == "receipt-sha":
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        receipt = next(iter(payload["checkpoint_receipts"].values()))
        receipt["checkpoint_sha256"] = "f" * 64
        manifest.write_text(json.dumps(payload), encoding="utf-8")
    elif mutation == "checkpoint-relabel":
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["checkpoint"] = "decoy.pt"
        manifest.write_text(json.dumps(payload), encoding="utf-8")
    else:
        payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
        if mutation == "seed-relabel":
            payload["metadata"]["seed"] = protocol_envelope["contract"]["h1"][
                "cross_target_rosters"
            ]["stage1"]["seeds"][1]
        else:
            payload["metadata"]["checkpoint_step"] = 200_000
            payload["step"] = 200_000
        torch.save(payload, checkpoint)

    context = load_pia_protocol_context(
        protocol_manifest,
        expected_protocol_hash=str(protocol_envelope["protocol_hash"]),
    )
    with pytest.raises(ValueError):
        load_pia_training_identity(
            context,
            checkpoint_path=checkpoint,
            training_output_manifest=manifest,
            scorer_code_commit=CODE_COMMIT,
        )
