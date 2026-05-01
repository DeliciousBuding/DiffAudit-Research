from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class AuditVariationQueryContractTests(unittest.TestCase):
    def test_blocks_missing_real_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "variation-query-set"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/audit_variation_query_contract.py",
                    "--query-root",
                    str(root),
                    "--endpoint",
                    "",
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
        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["checks"]["query_image_root"])
        self.assertFalse(payload["checks"]["endpoint"])

    def test_accepts_minimum_member_nonmember_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "variation-query-set"
            member = root / "member"
            nonmember = root / "nonmember"
            member.mkdir(parents=True)
            nonmember.mkdir(parents=True)
            for index in range(2):
                (member / f"m{index}.png").write_bytes(b"png")
                (nonmember / f"n{index}.png").write_bytes(b"png")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/audit_variation_query_contract.py",
                    "--query-root",
                    str(root),
                    "--endpoint",
                    "https://example.invalid/variation",
                    "--min-split-count",
                    "2",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["checks"]["paper_eval_layout_min_count"])
        self.assertEqual(payload["layout"]["member_query_count"], 2)
        self.assertEqual(payload["layout"]["nonmember_query_count"], 2)


if __name__ == "__main__":
    unittest.main()
