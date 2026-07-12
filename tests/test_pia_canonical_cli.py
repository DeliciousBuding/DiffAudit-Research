from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from diffaudit.attacks import pia_adapter
from diffaudit.cli import main
from diffaudit.config import load_audit_config
from diffaudit.evidence.corrected_protocol import (
    build_paper1_corrected_contract,
    build_protocol_envelope,
)

RESEARCH_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = RESEARCH_ROOT / "configs" / "attacks" / "pia-mainline-canonical.yaml"
CODE_COMMIT = "c" * 40
SPLIT_SHA256 = "d" * 64
CHECKPOINT_SHA256 = "e" * 64


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
    return {
        "schema_version": 1,
        "attack": "pia",
        "variant": "pia",
        "timestep": 200,
        "lp_order": 4,
        "score_form": "negative_lp_norm",
        "score_direction": "higher_is_member",
        "input_range": [-1.0, 1.0],
        "packet_purpose": purpose,
        "run_seed": seeds[0] if run_seed is None else run_seed,
        "step": step,
        "checkpoint_sha256": checkpoint_sha256,
        "code_commit": CODE_COMMIT,
        "split_sha256": SPLIT_SHA256,
        "protocol_hash": protocol_hash,
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
) -> tuple[Path, Path]:
    return (
        _write_packet(
            tmp_path / "calibration.json",
            _packet(envelope, role="calibration", purpose=purpose),
        ),
        _write_packet(
            tmp_path / "evaluation.json",
            _packet(envelope, role="evaluation", purpose=purpose),
        ),
    )


def _run_canonical_cli(
    workspace: Path,
    *,
    protocol_manifest: Path,
    protocol_hash: str,
    calibration_packet: Path | None,
    evaluation_packet: Path | None,
    checkpoint_sha256: str = CHECKPOINT_SHA256,
    extra_args: list[str] | None = None,
) -> int:
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
        "--expected-checkpoint-sha256",
        checkpoint_sha256,
        "--stage",
        "stage1",
    ]
    if calibration_packet is not None:
        argv.extend(["--calibration-score-packet", str(calibration_packet)])
    if evaluation_packet is not None:
        argv.extend(["--evaluation-score-packet", str(evaluation_packet)])
    argv.extend(extra_args or [])
    return main(argv)


def test_cli_reports_complete_heldout_fixed_direction_metrics(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calibration, evaluation = _write_packet_pair(tmp_path, protocol_envelope)
    workspace = tmp_path / "success"

    exit_code = _run_canonical_cli(
        workspace,
        protocol_manifest=protocol_manifest,
        protocol_hash=str(protocol_envelope["protocol_hash"]),
        calibration_packet=calibration,
        evaluation_packet=evaluation,
    )

    emitted = json.loads(capsys.readouterr().out)
    summary = json.loads((workspace / "summary.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert emitted == summary
    assert summary["status"] == "evaluation_complete"
    assert summary["mode"] == "canonical_pia_evaluation"
    assert summary["packet_purpose"] == "corrected_evaluation"
    assert summary["metrics"]["evaluation_auc"] == pytest.approx(1.0)
    assert summary["metrics"]["calibration_threshold"] == pytest.approx(0.9)
    assert summary["metrics"]["evaluation_balanced_accuracy"] == pytest.approx(1.0)
    assert summary["metrics"]["evaluation_fpr"] == pytest.approx(0.0)
    assert summary["metrics"]["tpr_at_1pct_fpr"] == pytest.approx(1.0)
    assert len(summary["metrics"]["tpr_at_1pct_fpr_wilson_95_ci"]) == 2
    assert all("0_1pct" not in key for key in summary["metrics"])


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
        (lambda packet: packet.update(code_commit="f" * 40), "code_commit"),
        (lambda packet: packet.update(split_sha256="f" * 64), "split_sha256"),
        (lambda packet: packet.update(protocol_hash="f" * 64), "protocol_hash"),
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
    with pytest.raises(ValueError, match="provenance"):
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


def test_cli_never_claims_a_full_positive_control_from_one_packet_pair(
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
    assert (
        _run_canonical_cli(
            tmp_path / "positive-control",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )
        == 0
    )
    summary = json.loads(capsys.readouterr().out)
    assert summary["status"] == "cpu_positive_control_partial"
    assert summary["complete_positive_control_gate"] is False

    failed_calibration = _packet(
        protocol_envelope, role="calibration", purpose="cpu_positive_control"
    )
    failed_evaluation = _packet(
        protocol_envelope, role="evaluation", purpose="cpu_positive_control"
    )
    for packet in (failed_calibration, failed_evaluation):
        rows = packet["rows"]
        assert isinstance(rows, list)
        for row in rows:
            row["score"] = 0.0
    calibration = _write_packet(tmp_path / "failed-calibration.json", failed_calibration)
    evaluation = _write_packet(tmp_path / "failed-evaluation.json", failed_evaluation)
    assert (
        _run_canonical_cli(
            tmp_path / "failed-positive-control",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            calibration_packet=calibration,
            evaluation_packet=evaluation,
        )
        == 1
    )
    failed = json.loads(capsys.readouterr().out)
    assert failed["status"] == "cpu_positive_control_failed"


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


def test_canonical_exporter_packet_is_consumed_without_translation(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    protocol_manifest: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"canonical-checkpoint")
    checkpoint_sha256 = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    manifest_rows = contract["evaluation"]["rows"]
    by_index = {int(row["dataset_index"]): row for row in manifest_rows}

    monkeypatch.setattr(pia_adapter, "validate_pia_workspace", lambda _path: {"status": "ready"})
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
    monkeypatch.setattr(pia_adapter, "load_pia_ddpm_modules", lambda _root: (object(), object()))
    monkeypatch.setattr(
        pia_adapter,
        "load_pia_model",
        lambda *_args, **_kwargs: (torch.nn.Identity(), "ema_model"),
    )
    monkeypatch.setattr(
        pia_adapter,
        "_build_pia_attacker",
        lambda **_kwargs: lambda batch: batch[:, 0, 0, 0],
    )

    def fake_loader(
        dataset: str,
        dataset_dir: str | Path,
        packet_indices: list[int],
        batch_size: int,
    ) -> DataLoader:
        del dataset, dataset_dir
        values = torch.zeros(len(packet_indices), 3, 2, 2)
        values[:, 0, 0, 0] = torch.tensor(
            [0.9 if by_index[index]["label"] == 1 else 0.1 for index in packet_indices]
        )
        labels = torch.tensor([by_index[index]["class_id"] for index in packet_indices])
        return DataLoader(TensorDataset(values, labels), batch_size=batch_size, shuffle=False)

    monkeypatch.setattr(pia_adapter, "_build_pia_packet_loader", fake_loader)
    config = load_audit_config(CANONICAL_CONFIG)
    common = {
        "repo_root": tmp_path / "repo",
        "member_split_root": tmp_path / "unused",
        "device": "cpu",
        "batch_size": 64,
        "protocol_manifest": protocol_manifest,
        "expected_protocol_hash": str(protocol_envelope["protocol_hash"]),
        "expected_checkpoint_sha256": checkpoint_sha256,
        "stage": "stage1",
        "run_seed": contract["h1"]["cross_target_rosters"]["stage1"]["seeds"][0],
        "step": 100_000,
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

    assert (
        _run_canonical_cli(
            tmp_path / "evaluate-export",
            protocol_manifest=protocol_manifest,
            protocol_hash=str(protocol_envelope["protocol_hash"]),
            checkpoint_sha256=checkpoint_sha256,
            calibration_packet=calibration_packet,
            evaluation_packet=evaluation_packet,
        )
        == 0
    )
    summary = json.loads(capsys.readouterr().out)
    assert summary["status"] == "evaluation_complete"
    assert summary["metrics"]["evaluation_auc"] == pytest.approx(1.0)
