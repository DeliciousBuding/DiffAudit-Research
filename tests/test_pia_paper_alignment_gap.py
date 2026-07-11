from pathlib import Path

import yaml

from diffaudit.attacks.pia import build_pia_plan
from diffaudit.config import load_audit_config


def test_canonical_pia_config_is_an_executable_single_timestep_contract() -> None:
    config_path = Path("configs/attacks/pia-mainline-canonical.yaml")
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    plan = build_pia_plan(load_audit_config(config_path))

    assert plan.variant == "canonical-ddpm-eq9"
    assert plan.attacker_name == "PIA"
    assert plan.timestep == 200
    assert plan.lp_order == 4
    assert payload["attack"]["parameters"]["query_timesteps"] == [0, 200]
    assert payload["attack"]["parameters"]["query_count"] == 2
    assert "attack_num" not in payload["attack"]["parameters"]
    assert "interval" not in payload["attack"]["parameters"]
