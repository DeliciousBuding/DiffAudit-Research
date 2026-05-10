"""CPU-only scout for ReDiffuse collaborator ResNet scoring-contract parity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from diffaudit.attacks.rediffuse import default_bundle_root, write_json


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _snippet_present(text: str, snippet: str) -> bool:
    return snippet.replace(" ", "") in text.replace(" ", "")


def review_resnet_contract_scout(*, bundle_root: Path, output: Path) -> dict[str, Any]:
    attack_py = bundle_root / "attack.py"
    if not attack_py.is_file():
        result = {
            "status": "blocked",
            "track": "gray-box",
            "method": "rediffuse",
            "mode": "resnet-contract-scout",
            "verdict": "needs-assets",
            "error": f"missing collaborator attack.py at {attack_py.as_posix()}",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        write_json(output, result)
        return result

    attack_text = _read(attack_py)
    current_adapter = _read(Path(__file__).resolve().parents[1] / "src" / "diffaudit" / "attacks" / "rediffuse_adapter.py")
    collaborator_features = {
        "uses_resnet18_single_logit": "resnet.ResNet18(num_channels=3 * 1, num_classes=1)" in attack_text,
        "uses_sgd_mse": "torch.optim.SGD" in attack_text and "((logit - label) ** 2).mean()" in attack_text,
        "uses_train_prefix_test_suffix": all(
            token in attack_text
            for token in (
                "train_member_concat = member_concat[:num_train]",
                "test_member_concat = member_concat[num_train:]",
                "train_nonmember_concat = nonmember_concat[:num_train]",
                "test_nonmember_concat = nonmember_concat[num_train:]",
            )
        ),
        "negates_scores_before_roc": "member *= -1" in attack_text and "nonmember *= -1" in attack_text,
        "roc_uses_member_lower": "TP = (member_scores <= threshold).sum()" in attack_text,
        "best_checkpoint_counter_not_updated": (
            "test_acc_best = 0" in attack_text
            and "if test_acc > test_acc_best:" in attack_text
            and "test_acc_best = test_acc" not in attack_text
        ),
    }
    adapter_features = {
        "uses_resnet18_single_logit": "resnet_module.ResNet18(num_channels=3, num_classes=1)" in current_adapter,
        "uses_sgd_mse": "torch.optim.SGD" in current_adapter and "((logits - label) ** 2).mean()" in current_adapter,
        "uses_train_prefix_test_suffix": all(
            token in current_adapter
            for token in (
                "member_features[:train_count]",
                "member_features[train_count:]",
                "nonmember_features[:train_count]",
                "nonmember_features[train_count:]",
            )
        ),
        "stores_best_checkpoint_by_test_acc": (
            "if test_acc > best_acc:" in current_adapter
            and _snippet_present(current_adapter, "best_acc = test_acc")
        ),
        "returns_unnegated_logits": "member_scores.detach().cpu()" in current_adapter,
    }
    semantic_mismatches = []
    if collaborator_features["best_checkpoint_counter_not_updated"] and adapter_features["stores_best_checkpoint_by_test_acc"]:
        semantic_mismatches.append(
            "collaborator nns_attack does not update test_acc_best, while Research adapter selects true best held-out epoch"
        )
    if collaborator_features["negates_scores_before_roc"] and adapter_features["returns_unnegated_logits"]:
        semantic_mismatches.append(
            "collaborator negates logits before member-lower ROC, while Research adapter feeds unnegated logits into higher-is-member metrics"
        )
    release_gate = {
        "collaborator_contract_detected": all(collaborator_features.values()),
        "adapter_contract_detected": all(adapter_features.values()),
        "semantic_mismatch_count": len(semantic_mismatches),
        "exact_replay_ready": len(semantic_mismatches) == 0,
        "passed": False,
    }
    result = {
        "status": "blocked",
        "track": "gray-box",
        "method": "rediffuse",
        "mode": "resnet-contract-scout",
        "verdict": "blocked-by-contract-mismatch",
        "hypothesis": "A ReDiffuse ResNet replay can release GPU only if the adapter matches collaborator nns_attack semantics.",
        "falsifier": "Any scorer-training, checkpoint-selection, sign, or ROC-direction mismatch blocks GPU release.",
        "release_gate": release_gate,
        "collaborator_features": collaborator_features,
        "adapter_features": adapter_features,
        "semantic_mismatches": semantic_mismatches,
        "next_action": "implement an exact replay mode or explicitly decide to test a Research-specific ResNet variant before any GPU packet",
        "notes": [
            "This scout is CPU-only and does not score samples.",
            "The detected checkpoint-selection mismatch can explain why the existing ResNet parity packet is not exact collaborator replay.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, default=default_bundle_root())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("workspaces/gray-box/runs/rediffuse-resnet-contract-scout-20260510-cpu/summary.json"),
    )
    args = parser.parse_args()
    result = review_resnet_contract_scout(bundle_root=args.bundle_root, output=args.output)
    print(json.dumps({"status": result["status"], "verdict": result["verdict"], "output": args.output.as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
