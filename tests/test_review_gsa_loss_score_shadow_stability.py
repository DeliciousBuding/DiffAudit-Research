from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import torch


class ReviewGsaLossScoreShadowStabilityTests(unittest.TestCase):
    def _write_scores(self, root: Path, name: str, values: list[float]) -> str:
        path = root / f"{name}.pt"
        torch.save(torch.tensor(values, dtype=torch.float32), path)
        return path.relative_to(Path(__file__).resolve().parents[1]).as_posix()

    def _write_packet(self, root: Path, *, status: str = "ready") -> Path:
        packet = root / "summary.json"
        exports: dict[str, dict[str, str]] = {}
        shadows = ["shadow-a", "shadow-b", "shadow-c"]
        for index, shadow in enumerate(shadows):
            prefix = shadow.replace("-", "_")
            exports[f"{prefix}_member"] = {
                "output_path": self._write_scores(root, f"{prefix}_member", [0.8 + index, 0.9 + index, 1.0 + index])
            }
            exports[f"{prefix}_non_member"] = {
                "output_path": self._write_scores(
                    root,
                    f"{prefix}_non_member",
                    [0.1 + index, 0.2 + index, 0.3 + index],
                )
            }
        exports["target_member"] = {"output_path": self._write_scores(root, "target_member", [0.7, 0.8, 0.9])}
        exports["target_non_member"] = {
            "output_path": self._write_scores(root, "target_non_member", [0.05, 0.15, 0.25])
        }
        packet.write_text(
            json.dumps(
                {
                    "status": status,
                    "mode": "loss-score-export",
                    "exports": exports,
                    "artifact_paths": {"shadow_specs": [{"name": name} for name in shadows]},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return packet

    def test_reviews_minimal_ready_packet(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmpdir:
            root = Path(tmpdir)
            packet = self._write_packet(root)
            output = root / "review.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_gsa_loss_score_shadow_stability.py",
                    "--packet-summary",
                    packet.relative_to(repo_root).as_posix(),
                    "--output",
                    output.relative_to(repo_root).as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ready")
        self.assertIn(payload["verdict"], {"cpu-preflight-positive", "negative-but-useful"})

    def test_blocks_non_ready_export_summary(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmpdir:
            root = Path(tmpdir)
            packet = self._write_packet(root, status="blocked")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_gsa_loss_score_shadow_stability.py",
                    "--packet-summary",
                    packet.relative_to(repo_root).as_posix(),
                    "--output",
                    (root / "review.json").relative_to(repo_root).as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("status=ready", completed.stderr)


if __name__ == "__main__":
    unittest.main()
