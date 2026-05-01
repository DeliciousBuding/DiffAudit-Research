import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CollectH2Img2ImgResponseCacheScriptTests(unittest.TestCase):
    def test_dry_run_writes_frozen_schema_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "run"
            result = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/collect_h2_img2img_response_cache.py",
                    "--run-root",
                    str(run_root),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            plan = json.loads((run_root / "plan.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "planned")
        self.assertEqual(plan["mode"], "dry-run")
        self.assertEqual(plan["inputs"]["packet_size_per_class"], 10)
        self.assertEqual(plan["inputs"]["sample_offset_per_class"], 0)
        self.assertEqual(plan["inputs"]["strengths"], [0.35, 0.55, 0.75])
        self.assertEqual(plan["inputs"]["repeats"], 2)
        self.assertEqual(
            plan["cache_schema"]["required"],
            ["labels", "strengths", "inputs", "responses", "min_distances_rmse"],
        )
        self.assertIn("lowpass_min_distances_rmse", plan["cache_schema"]["optional"])

    def test_dry_run_schema_uses_packet_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "run"
            subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/collect_h2_img2img_response_cache.py",
                    "--run-root",
                    str(run_root),
                    "--packet-size",
                    "1",
                    "--strengths",
                    "0.35",
                    "--repeats",
                    "1",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            plan = json.loads((run_root / "plan.json").read_text(encoding="utf-8"))

        self.assertEqual(plan["cache_schema"]["shape"]["labels"], "[2]")
        self.assertEqual(plan["cache_schema"]["shape"]["responses"], "[2, 1, 1, 3, 512, 512]")

    def test_dry_run_records_sample_offset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "run"
            subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/collect_h2_img2img_response_cache.py",
                    "--run-root",
                    str(run_root),
                    "--packet-size",
                    "10",
                    "--sample-offset",
                    "10",
                    "--split-name",
                    "derived-public-25",
                    "--strengths",
                    "0.75",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            plan = json.loads((run_root / "plan.json").read_text(encoding="utf-8"))

        self.assertEqual(plan["inputs"]["split_name"], "derived-public-25")
        self.assertEqual(plan["inputs"]["sample_offset_per_class"], 10)
        self.assertEqual(plan["inputs"]["sample_position_range_per_class"], [10, 20])
        self.assertEqual(plan["inputs"]["packet_size_per_class"], 10)
        self.assertEqual(plan["inputs"]["strengths"], [0.75])

    def test_rejects_unsorted_strengths_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/collect_h2_img2img_response_cache.py",
                    "--run-root",
                    str(Path(tmpdir) / "run"),
                    "--strengths",
                    "0.7",
                    "0.3",
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("sorted unique", payload["error"])

    def test_rejects_negative_sample_offset(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/collect_h2_img2img_response_cache.py",
                    "--run-root",
                    str(Path(tmpdir) / "run"),
                    "--sample-offset",
                    "-1",
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("non-negative", payload["error"])


if __name__ == "__main__":
    unittest.main()
