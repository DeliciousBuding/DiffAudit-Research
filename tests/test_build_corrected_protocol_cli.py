from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from diffaudit.evidence.corrected_protocol import verify_paper1_contract

_SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "h1" / "build_corrected_protocol.py"
_CODE_COMMIT = "c" * 40


def _load_builder_module():
    assert _SCRIPT_PATH.is_file(), "corrected protocol builder CLI is missing"
    spec = importlib.util.spec_from_file_location("build_corrected_protocol", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_full_split(path: Path) -> None:
    np.savez(
        path,
        mia_train_idxs=np.arange(25_000, dtype=np.int64),
        mia_eval_idxs=np.arange(25_000, 50_000, dtype=np.int64),
    )


def _balanced_targets() -> list[int]:
    return (np.arange(50_000, dtype=np.int64) % 10).tolist()


def test_build_corrected_protocol_cli_help_lists_required_identity_arguments() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path("src").resolve())

    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH), "--help"],
        cwd=Path(__file__).parents[1],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--split-path" in result.stdout
    assert "--dataset-root" in result.stdout
    assert "--cifar10-root" in result.stdout
    assert "--code-commit" in result.stdout
    assert "--output" in result.stdout
    assert "--force" in result.stdout


def test_build_corrected_protocol_uses_fake_split_sha_and_synthetic_targets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_builder_module()
    split_path = tmp_path / "CIFAR10_train_ratio0.5.npz"
    _write_full_split(split_path)
    dataset_root = (tmp_path / "local-absolute-dataset-root").resolve()
    monkeypatch.setattr(module, "_load_cifar10_train_targets", lambda root: _balanced_targets())

    envelope = module.build_corrected_protocol(
        split_path=split_path,
        dataset_root=dataset_root,
        code_commit=_CODE_COMMIT,
    )
    contract = verify_paper1_contract(envelope)

    assert contract["dataset"]["split"] == {
        "filename": split_path.name,
        "sha256": hashlib.sha256(split_path.read_bytes()).hexdigest(),
        "member_count": 25_000,
        "nonmember_count": 25_000,
    }
    serialized = json.dumps(envelope)
    assert str(dataset_root) not in serialized
    assert str(split_path.parent) not in serialized


def test_build_corrected_protocol_rejects_incomplete_partition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_builder_module()
    split_path = tmp_path / "split.npz"
    np.savez(
        split_path,
        mia_train_idxs=np.arange(25_000, dtype=np.int64),
        mia_eval_idxs=np.arange(25_000, 49_999, dtype=np.int64),
    )
    monkeypatch.setattr(module, "_load_cifar10_train_targets", lambda root: _balanced_targets())

    with pytest.raises(ValueError, match="complete 25000/25000 partition"):
        module.build_corrected_protocol(
            split_path=split_path,
            dataset_root=tmp_path,
            code_commit=_CODE_COMMIT,
        )


def test_write_protocol_envelope_is_idempotent_and_force_protected(tmp_path: Path) -> None:
    module = _load_builder_module()
    output = (tmp_path / "nested" / "protocol.json").resolve()
    first = {"schema_version": 1, "protocol_hash": "a" * 64, "contract": {"value": 1}}
    changed = {"schema_version": 1, "protocol_hash": "b" * 64, "contract": {"value": 2}}

    assert module.write_protocol_envelope(output, first, force=False) is True
    first_payload = output.read_text(encoding="utf-8")
    assert first_payload.startswith('{\n  "schema_version"')
    assert module.write_protocol_envelope(output, first, force=False) is False
    assert output.read_text(encoding="utf-8") == first_payload

    with pytest.raises(FileExistsError, match="--force"):
        module.write_protocol_envelope(output, changed, force=False)
    assert module.write_protocol_envelope(output, changed, force=True) is True
    assert json.loads(output.read_text(encoding="utf-8")) == changed


def test_main_accepts_cifar10_root_alias_and_writes_verified_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_builder_module()
    split_path = tmp_path / "split.npz"
    output = (tmp_path / "absolute-output" / "protocol.json").resolve()
    _write_full_split(split_path)
    monkeypatch.setattr(module, "_load_cifar10_train_targets", lambda root: _balanced_targets())

    result = module.main(
        [
            "--split-path",
            str(split_path),
            "--cifar10-root",
            str(tmp_path.resolve()),
            "--code-commit",
            _CODE_COMMIT,
            "--output",
            str(output),
        ]
    )

    assert result == 0
    verified = verify_paper1_contract(output)
    assert verified["dataset"]["split"]["filename"] == "split.npz"
    assert str(output.parent) not in output.read_text(encoding="utf-8")
