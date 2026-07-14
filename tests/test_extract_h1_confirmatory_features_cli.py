from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_script() -> object:
    path = Path(__file__).parents[1] / "scripts" / "h1" / "extract_h1_confirmatory_features.py"
    spec = importlib.util.spec_from_file_location("extract_h1_confirmatory_features", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_prints_only_outcome_blind_benchmark_summary(monkeypatch, capsys) -> None:
    module = _load_script()
    expected = {
        "rows": 2048,
        "queries": 6144,
        "end_to_end_seconds": 20.0,
        "extraction_seconds": 10.0,
        "phase_timings": {
            "identity_protocol": 1.0,
            "checkpoint_hash_load": 2.0,
            "model_to_device": 3.0,
            "dataset_load": 1.0,
            "extraction": 10.0,
            "packet_write_hash": 2.0,
        },
        "rows_per_second": 204.8,
        "peak_cuda_allocated_bytes": 1,
        "peak_cuda_reserved_bytes": 2,
        "packet_path": "packet",
        "packet_sha256": "a" * 64,
    }
    monkeypatch.setattr(module, "_execute", lambda _args: expected)

    exit_code = module.main(
        [
            "--protocol-manifest",
            "protocol.json",
            "--expected-protocol-hash",
            "b" * 64,
            "--checkpoint",
            "checkpoint.pt",
            "--training-manifest",
            "manifest.json",
            "--dataset-root",
            "cifar10",
            "--output",
            "packet",
            "--packet-purpose",
            "preflight_benchmark",
            "--scorer-code-commit",
            "c" * 40,
            "--preflight",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out) == expected
    assert captured.err == ""
    assert all(
        token not in captured.out.lower()
        for token in ("auc", "tpr", "accuracy", "metric", "outcome")
    )
