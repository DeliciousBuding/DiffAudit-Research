import json
import tempfile
import unittest
from pathlib import Path


class ClidBridgeContractTests(unittest.TestCase):
    def _make_bridge_run(self, root: Path) -> None:
        member_dir = root / "datasets" / "member"
        nonmember_dir = root / "datasets" / "nonmember"
        member_dir.mkdir(parents=True)
        nonmember_dir.mkdir(parents=True)
        for split_dir, prefix in ((member_dir, "m"), (nonmember_dir, "n")):
            rows = []
            for index in range(2):
                filename = f"{index:03d}.png"
                (split_dir / filename).write_bytes(prefix.encode("ascii"))
                rows.append(json.dumps({"file_name": filename, "text": f"{prefix}-{index}"}))
            (split_dir / "metadata.jsonl").write_text("\n".join(rows), encoding="utf-8")
        (root / "analysis.md").write_text("# analysis\n", encoding="utf-8")
        (root / "mia_CLiD_clip_local.py").write_text(
            "unet.load_attn_procs('x')\nload_dataset('imagefolder')\nflags.attack = 'clid_clip'\n",
            encoding="utf-8",
        )
        config = {
            "run_id": root.name,
            "track": "black-box",
            "method": "clid",
            "status": "prepared",
            "mode": "paper-alignment-local-bridge",
            "assets": {
                "member_dataset": (root / "datasets" / "member").as_posix(),
                "nonmember_dataset": (root / "datasets" / "nonmember").as_posix(),
            },
            "export": {
                "member": {"count": 2},
                "nonmember": {"count": 2},
            },
        }
        (root / "config.json").write_text(json.dumps(config), encoding="utf-8")

    def test_validate_ready_bridge_run(self) -> None:
        from diffaudit.attacks.clid_bridge_contract import validate_clid_bridge_run

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bridge"
            root.mkdir()
            self._make_bridge_run(root)
            payload = validate_clid_bridge_run(root)

        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["checks"]["nonempty_balanced_export"])

    def test_missing_metadata_blocks_contract(self) -> None:
        from diffaudit.attacks.clid_bridge_contract import validate_clid_bridge_run

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "bridge"
            root.mkdir()
            self._make_bridge_run(root)
            (root / "datasets" / "member" / "metadata.jsonl").unlink()
            payload = validate_clid_bridge_run(root)

        self.assertEqual(payload["status"], "blocked")
        self.assertIn("member_dataset_contract", payload["missing"])


if __name__ == "__main__":
    unittest.main()
