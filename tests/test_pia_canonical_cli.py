from __future__ import annotations

import json
from pathlib import Path

import pytest

from diffaudit.cli import main

RESEARCH_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = RESEARCH_ROOT / "configs" / "attacks" / "pia-mainline-canonical.yaml"


def _write_score_packet(
    path: Path,
    *,
    split: str,
    rows: list[tuple[int, int, float]],
) -> Path:
    payload = {
        "schema": "diffaudit.pia-score-packet.v1",
        "variant": "canonical-ddpm-eq9",
        "timestep": 200,
        "lp_order": 4,
        "score_direction": "higher_is_member",
        "split": split,
        "rows": [
            {"dataset_index": dataset_index, "label": label, "score": score}
            for dataset_index, label, score in rows
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _run_canonical_cli(
    workspace: Path,
    *,
    calibration_packet: Path | None,
    evaluation_packet: Path | None,
) -> int:
    argv = [
        "run-pia-runtime-mainline",
        "--config",
        str(CANONICAL_CONFIG),
        "--workspace",
        str(workspace),
    ]
    if calibration_packet is not None:
        argv.extend(["--calibration-score-packet", str(calibration_packet)])
    if evaluation_packet is not None:
        argv.extend(["--evaluation-score-packet", str(evaluation_packet)])
    return main(argv)


@pytest.fixture
def calibration_packet(tmp_path: Path) -> Path:
    return _write_score_packet(
        tmp_path / "calibration.json",
        split="calibration",
        rows=[
            (1, 1, 0.9),
            (2, 1, 0.8),
            (3, 0, 0.2),
            (4, 0, 0.1),
        ],
    )


@pytest.fixture
def evaluation_packet(tmp_path: Path) -> Path:
    return _write_score_packet(
        tmp_path / "evaluation.json",
        split="evaluation",
        rows=[(10, 1, 0.85), (11, 0, 0.15)],
    )


def test_cli_calibrates_and_evaluates_two_disjoint_score_packets(
    tmp_path: Path,
    calibration_packet: Path,
    evaluation_packet: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    workspace = tmp_path / "success"

    exit_code = _run_canonical_cli(
        workspace,
        calibration_packet=calibration_packet,
        evaluation_packet=evaluation_packet,
    )

    emitted = json.loads(capsys.readouterr().out)
    summary = json.loads((workspace / "summary.json").read_text(encoding="utf-8"))
    assert exit_code == 0
    assert emitted == summary
    assert summary["status"] == "ready"
    assert summary["mode"] == "canonical-calibrated-evaluation"
    assert summary["variant"] == "canonical-ddpm-eq9"
    assert summary["metrics"]["threshold"] == pytest.approx(0.8)


@pytest.mark.parametrize("missing", ["calibration", "evaluation"])
def test_cli_rejects_a_missing_canonical_score_packet(
    tmp_path: Path,
    calibration_packet: Path,
    evaluation_packet: Path,
    missing: str,
) -> None:
    with pytest.raises(ValueError, match="requires both calibration and evaluation"):
        _run_canonical_cli(
            tmp_path / f"missing-{missing}",
            calibration_packet=None if missing == "calibration" else calibration_packet,
            evaluation_packet=None if missing == "evaluation" else evaluation_packet,
        )


def test_cli_rejects_calibration_evaluation_row_overlap(
    tmp_path: Path,
    calibration_packet: Path,
) -> None:
    overlapping_evaluation = _write_score_packet(
        tmp_path / "overlapping-evaluation.json",
        split="evaluation",
        rows=[(4, 1, 0.85), (10, 0, 0.15)],
    )

    with pytest.raises(ValueError, match="must be disjoint"):
        _run_canonical_cli(
            tmp_path / "overlap",
            calibration_packet=calibration_packet,
            evaluation_packet=overlapping_evaluation,
        )


def test_cli_evaluation_labels_do_not_change_calibration_threshold(
    tmp_path: Path,
    calibration_packet: Path,
    evaluation_packet: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    relabeled_evaluation = _write_score_packet(
        tmp_path / "relabeled-evaluation.json",
        split="evaluation",
        rows=[(10, 0, 0.85), (11, 1, 0.15)],
    )
    first_workspace = tmp_path / "first-labeling"
    second_workspace = tmp_path / "second-labeling"

    assert (
        _run_canonical_cli(
            first_workspace,
            calibration_packet=calibration_packet,
            evaluation_packet=evaluation_packet,
        )
        == 0
    )
    capsys.readouterr()
    assert (
        _run_canonical_cli(
            second_workspace,
            calibration_packet=calibration_packet,
            evaluation_packet=relabeled_evaluation,
        )
        == 0
    )
    capsys.readouterr()

    first_summary = json.loads((first_workspace / "summary.json").read_text(encoding="utf-8"))
    second_summary = json.loads((second_workspace / "summary.json").read_text(encoding="utf-8"))
    assert first_summary["metrics"]["threshold"] == second_summary["metrics"]["threshold"]
    assert (
        first_summary["metrics"]["balanced_accuracy"]
        != second_summary["metrics"]["balanced_accuracy"]
    )
