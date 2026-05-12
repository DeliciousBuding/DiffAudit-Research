import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_ib_defended_shadow_training_manifest


def _load_default_artifact() -> dict:
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / validate_ib_defended_shadow_training_manifest.DEFAULT_ARTIFACT).read_text(encoding="utf-8"))


class ValidateIBDefendedShadowTrainingManifestTests(unittest.TestCase):
    def test_default_artifact_is_valid(self) -> None:
        self.assertEqual(validate_ib_defended_shadow_training_manifest.main([]), 0)

    def test_rejects_single_shadow(self) -> None:
        artifact = _load_default_artifact()
        artifact["shadow_training"] = artifact["shadow_training"][:1]
        errors = validate_ib_defended_shadow_training_manifest.validate(artifact)
        self.assertIn("shadow_training must contain at least two shadows", errors)

    def test_rejects_target_role(self) -> None:
        artifact = _load_default_artifact()
        artifact["role"] = "target"
        artifact["shadow_training"][0]["training_role"] = "target"
        errors = validate_ib_defended_shadow_training_manifest.validate(artifact)
        self.assertIn("role must be defended-shadow", errors)
        self.assertIn("shadow_training[0].training_role must be defended-shadow", errors)

    def test_rejects_identity_count_mismatch(self) -> None:
        artifact = _load_default_artifact()
        artifact["identity_contract"] = copy.deepcopy(artifact["identity_contract"])
        artifact["identity_contract"]["matched_nonmember_count"] = 31
        errors = validate_ib_defended_shadow_training_manifest.validate(artifact)
        self.assertIn("forget_count must equal matched_nonmember_count", errors)

    def test_generated_manifest_matches_validator_contract(self) -> None:
        from diffaudit.defenses.risk_targeted_unlearning import build_defended_shadow_training_manifest

        repo_root = Path(__file__).resolve().parents[1]
        tmp_parent = repo_root / "tmp"
        tmp_parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp_parent) as tmpdir:
            root = Path(tmpdir)
            assets_root = root / "assets"
            for shadow_id in ("shadow-01", "shadow-02"):
                (assets_root / "datasets" / f"{shadow_id}-member").mkdir(parents=True, exist_ok=True)
                (assets_root / "checkpoints" / shadow_id).mkdir(parents=True, exist_ok=True)
            forget_index_file = root / "forget-members-k2.txt"
            matched_index_file = root / "matched-nonmembers-k2.txt"
            forget_index_file.write_text("10\n11\n", encoding="utf-8")
            matched_index_file.write_text("20\n21\n", encoding="utf-8")

            manifest = build_defended_shadow_training_manifest(
                workspace=(root / "artifacts" / "generated-manifest").relative_to(repo_root),
                assets_root=assets_root.relative_to(repo_root),
                forget_member_index_file=forget_index_file.relative_to(repo_root),
                matched_nonmember_index_file=matched_index_file.relative_to(repo_root),
                shadow_ids=["shadow-01", "shadow-02"],
                num_steps=3,
                batch_size=2,
                seed=42,
            )

        self.assertEqual(validate_ib_defended_shadow_training_manifest.validate(manifest, repo_root=repo_root), [])
        self.assertTrue(manifest["shadow_training"][0]["output_workspace"].endswith("runs/generated-manifest/shadow-01"))

    def test_cli_reports_missing_doc(self) -> None:
        artifact = _load_default_artifact()
        artifact["evidence_docs"] = [
            doc
            for doc in artifact["evidence_docs"]
            if doc != "docs/evidence/ib-defended-shadow-training-manifest-20260512.md"
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifact.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            exit_code = validate_ib_defended_shadow_training_manifest.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
