from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from diffaudit.attacks.response_contract import inspect_response_contract_package


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
        (splits / "member_ids.json").write_text(json.dumps(["m0", "m1"]), encoding="utf-8")
        (splits / "nonmember_ids.json").write_text(json.dumps(["n0", "n1"]), encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
