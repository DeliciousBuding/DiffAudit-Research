from __future__ import annotations

import json
from pathlib import Path

import pytest

from diffaudit.evidence import corrected_protocol as protocol


def _api(name: str):
    value = getattr(protocol, name, None)
    assert callable(value), f"missing protocol API: {name}"
    return value


def test_build_protocol_envelope_is_exact_hash_sealed_json_safe_deep_copy() -> None:
    contract = {"rows": ({"dataset_index": 7},), "metadata": {"name": "safe"}}

    envelope = _api("build_protocol_envelope")(contract)

    assert set(envelope) == {"schema_version", "protocol_hash", "contract"}
    assert envelope["schema_version"] == 1
    assert envelope["protocol_hash"] == protocol.canonical_protocol_hash(envelope["contract"])
    assert envelope["contract"] == {
        "rows": [{"dataset_index": 7}],
        "metadata": {"name": "safe"},
    }
    contract["metadata"]["name"] = "mutated"
    assert envelope["contract"]["metadata"]["name"] == "safe"


@pytest.mark.parametrize(
    ("contract", "message"),
    [
        ({"value": float("nan")}, "JSON"),
        ({"value": object()}, "JSON"),
        ({"path": "C:\\private\\split.npz"}, "absolute paths"),
    ],
)
def test_build_protocol_envelope_rejects_unsafe_contracts(
    contract: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _api("build_protocol_envelope")(contract)


def test_load_protocol_envelope_accepts_mapping_and_path_as_deep_copies(tmp_path: Path) -> None:
    envelope = _api("build_protocol_envelope")({"name": "paper1", "nested": {"value": 1}})
    manifest_path = tmp_path / "protocol.json"
    manifest_path.write_text(json.dumps(envelope), encoding="utf-8")

    loaded_mapping = _api("load_protocol_envelope")(envelope)
    loaded_path = _api("load_protocol_envelope")(manifest_path)

    assert loaded_mapping == envelope
    assert loaded_path == envelope
    envelope["contract"]["nested"]["value"] = 2
    assert loaded_mapping["contract"]["nested"]["value"] == 1
    assert loaded_path["contract"]["nested"]["value"] == 1


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda value: value.update(extra=True), "top-level fields"),
        (lambda value: value.update(schema_version=2), "schema_version"),
        (lambda value: value.update(protocol_hash="A" * 64), "protocol_hash"),
        (lambda value: value["contract"].update(name="tampered"), "does not match"),
    ],
)
def test_load_protocol_envelope_rejects_invalid_or_tampered_mappings(
    mutator,
    message: str,
) -> None:
    envelope = _api("build_protocol_envelope")({"name": "paper1"})
    mutator(envelope)

    with pytest.raises(ValueError, match=message):
        _api("load_protocol_envelope")(envelope)


def test_load_protocol_envelope_rejects_non_json_and_absolute_paths(tmp_path: Path) -> None:
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text('{"schema_version": 1, "contract": NaN}', encoding="utf-8")

    with pytest.raises(ValueError, match="JSON"):
        _api("load_protocol_envelope")(invalid_json)

    unsafe = {
        "schema_version": 1,
        "protocol_hash": "0" * 64,
        "contract": {"split": "/private/split.npz"},
    }
    with pytest.raises(ValueError, match="absolute paths"):
        _api("load_protocol_envelope")(unsafe)


def test_load_protocol_envelope_path_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    protocol_hash = protocol.canonical_protocol_hash({"name": "paper1"})
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        "{"
        '"schema_version":1,'
        '"schema_version":1,'
        f'"protocol_hash":"{protocol_hash}",'
        '"contract":{"name":"paper1"}'
        "}",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate JSON key"):
        _api("load_protocol_envelope")(duplicate)
