from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from diffaudit.attacks.response_contract import (
    discover_response_contract_packages,
    inspect_response_contract_package,
    scaffold_response_contract_package,
)


class ResponseContractPackageTests(unittest.TestCase):
    def _make_ready_package(self, root: Path, asset_id: str, *, count: int = 2, repeats: int = 3) -> tuple[Path, Path]:
        dataset = root / "black-box" / "datasets" / asset_id
        supplementary = root / "black-box" / "supplementary" / asset_id
        for split in ("member", "nonmember"):
            query_dir = dataset / "query" / split
            response_dir = supplementary / "responses" / split
            query_dir.mkdir(parents=True)
            response_dir.mkdir(parents=True)
            for query_index in range(count):
                (query_dir / f"{split}-{query_index}.png").write_bytes(b"png")
                for repeat_index in range(repeats):
                    (response_dir / f"{split}-{query_index}-r{repeat_index}.png").write_bytes(b"png")

        splits = dataset / "splits"
        splits.mkdir(parents=True)
        (splits / "member_ids.json").write_text(json.dumps([f"m{index}" for index in range(count)]), encoding="utf-8")
        (splits / "nonmember_ids.json").write_text(
            json.dumps([f"n{index}" for index in range(count)]),
            encoding="utf-8",
        )
        (dataset / "manifest.json").write_text(
            json.dumps({"dataset_name": "synthetic-response-contract", "member_count": count, "nonmember_count": count}),
            encoding="utf-8",
        )
        (supplementary / "endpoint_contract.json").write_text(
            json.dumps(
                {
                    "endpoint_mode": "image_to_image",
                    "model_identity": "synthetic-model",
                    "repeat_count": repeats,
                    "response_observability": "image",
                }
            ),
            encoding="utf-8",
        )
        (supplementary / "response_manifest.json").write_text(
            json.dumps({"repeat_count": repeats, "response_count": count * repeats * 2}),
            encoding="utf-8",
        )
        return dataset, supplementary

    def test_ready_package_passes_cpu_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset, supplementary = self._make_ready_package(Path(tmpdir), "response-contract-synthetic")
            payload = inspect_response_contract_package(
                asset_id="response-contract-synthetic",
                dataset_root=dataset,
                supplementary_root=supplementary,
                min_split_count=2,
            )

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["counts"]["query"]["member"], 2)
        self.assertEqual(payload["counts"]["responses"]["nonmember"], 6)
        self.assertTrue(payload["checks"]["controlled_repeats_or_seed_policy"])

    def test_missing_responses_is_blocked_after_query_and_protocol_are_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset, supplementary = self._make_ready_package(Path(tmpdir), "response-contract-synthetic")
            for path in (supplementary / "responses" / "member").glob("*.png"):
                path.unlink()
            payload = inspect_response_contract_package(
                asset_id="response-contract-synthetic",
                dataset_root=dataset,
                supplementary_root=supplementary,
                min_split_count=2,
            )

        self.assertEqual(payload["status"], "needs_responses")
        self.assertIn("response_member_count", payload["missing"])

    def test_duplicate_unrelated_responses_do_not_pass_per_query_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset, supplementary = self._make_ready_package(Path(tmpdir), "response-contract-synthetic")
            member_response = supplementary / "responses" / "member"
            for path in member_response.glob("*.png"):
                path.unlink()
            for index in range(6):
                (member_response / f"unrelated-{index}.png").write_bytes(b"png")
            payload = inspect_response_contract_package(
                asset_id="response-contract-synthetic",
                dataset_root=dataset,
                supplementary_root=supplementary,
                min_split_count=2,
            )

        self.assertEqual(payload["status"], "needs_responses")
        self.assertFalse(payload["counts"]["response_coverage"]["member"]["ready"])

    def test_malformed_manifest_returns_blocked_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset, supplementary = self._make_ready_package(Path(tmpdir), "response-contract-synthetic")
            (supplementary / "endpoint_contract.json").write_text("{not-json", encoding="utf-8")
            payload = inspect_response_contract_package(
                asset_id="response-contract-synthetic",
                dataset_root=dataset,
                supplementary_root=supplementary,
                min_split_count=2,
            )

        self.assertEqual(payload["status"], "blocked")
        self.assertIn("endpoint_contract_json_valid", payload["missing"])
        self.assertIn("invalid JSON", payload["parse_errors"]["endpoint_contract"])

    def test_invalid_repeat_count_returns_blocked_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset, supplementary = self._make_ready_package(Path(tmpdir), "response-contract-synthetic")
            endpoint = supplementary / "endpoint_contract.json"
            payload = json.loads(endpoint.read_text(encoding="utf-8"))
            payload["repeat_count"] = "three"
            endpoint.write_text(json.dumps(payload), encoding="utf-8")
            result = inspect_response_contract_package(
                asset_id="response-contract-synthetic",
                dataset_root=dataset,
                supplementary_root=supplementary,
                min_split_count=2,
            )

        self.assertEqual(result["status"], "blocked")
        self.assertIn("repeat_count_valid", result["missing"])

    def test_script_reports_needs_assets_for_missing_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/probe_response_contract_package.py",
                    "--asset-id",
                    "response-contract-missing",
                    "--download-root",
                    tmpdir,
                    "--min-split-count",
                    "2",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "needs_assets")

    def test_script_accepts_ready_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self._make_ready_package(Path(tmpdir), "response-contract-synthetic")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/probe_response_contract_package.py",
                    "--asset-id",
                    "response-contract-synthetic",
                    "--download-root",
                    tmpdir,
                    "--min-split-count",
                    "2",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready")

    def test_discovery_reports_ready_and_orphan_packages(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_ready_package(root, "response-contract-ready")
            (root / "black-box" / "supplementary" / "response-contract-orphan").mkdir(parents=True)
            payload = discover_response_contract_packages(
                download_root=root,
                min_split_count=2,
                include_asset_ids=["response-contract-missing"],
            )

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["ready_asset_ids"], ["response-contract-ready"])
        self.assertEqual(payload["supplementary_only_asset_ids"], ["response-contract-orphan"])
        self.assertEqual(payload["missing_requested_asset_ids"], ["response-contract-missing"])
        self.assertEqual(payload["counts"]["candidate_ids"], 3)

    def test_discovery_script_returns_nonzero_without_ready_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "black-box" / "supplementary" / "response-contract-orphan").mkdir(parents=True)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/discover_response_contract_packages.py",
                    "--download-root",
                    tmpdir,
                    "--min-split-count",
                    "2",
                    "--include-asset-id",
                    "response-contract-missing",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "needs_assets")
        self.assertEqual(payload["supplementary_only_asset_ids"], ["response-contract-orphan"])
        self.assertEqual(payload["missing_requested_asset_ids"], ["response-contract-missing"])

    def test_scaffold_dry_run_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = scaffold_response_contract_package(
                asset_id="response-contract-synthetic",
                download_root=root,
                dataset_name="synthetic",
                model_identity="model",
                create=False,
            )

            self.assertEqual(payload["status"], "dry_run")
            self.assertFalse((root / "black-box").exists())
            self.assertIn("manifest.json", "\n".join(payload["template_files"]))

    def test_scaffold_rejects_unsupported_endpoint_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(ValueError, "endpoint_mode must be one of"):
                scaffold_response_contract_package(
                    asset_id="response-contract-synthetic",
                    download_root=Path(tmpdir),
                    endpoint_mode="typo_mode",
                )

    def test_scaffold_create_writes_templates_that_probe_as_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            payload = scaffold_response_contract_package(
                asset_id="response-contract-synthetic",
                download_root=root,
                dataset_name="synthetic",
                model_identity="model",
                endpoint_mode="image_to_image",
                repeat_count=2,
                create=True,
            )
            preflight = inspect_response_contract_package(
                asset_id="response-contract-synthetic",
                dataset_root=root / "black-box" / "datasets" / "response-contract-synthetic",
                supplementary_root=root / "black-box" / "supplementary" / "response-contract-synthetic",
                min_split_count=2,
            )

        self.assertEqual(payload["status"], "created")
        self.assertEqual(preflight["status"], "needs_query_split")
        self.assertTrue(preflight["checks"]["endpoint_mode_supported"])
        self.assertTrue(preflight["checks"]["controlled_repeats_or_seed_policy"])

    def test_scaffold_script_create_writes_expected_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/scaffold_response_contract_package.py",
                    "--asset-id",
                    "response-contract-synthetic",
                    "--download-root",
                    tmpdir,
                    "--dataset-name",
                    "synthetic",
                    "--model-identity",
                    "model",
                    "--repeat-count",
                    "2",
                    "--create",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "created")
            self.assertTrue(
                (Path(tmpdir) / "black-box" / "datasets" / "response-contract-synthetic" / "manifest.json").is_file()
            )

    def test_scaffold_script_rejects_bad_endpoint_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/scaffold_response_contract_package.py",
                    "--asset-id",
                    "response-contract-synthetic",
                    "--download-root",
                    tmpdir,
                    "--endpoint-mode",
                    "typo_mode",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("invalid choice", completed.stderr)


if __name__ == "__main__":
    unittest.main()
