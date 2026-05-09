import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from diffaudit.attacks.rediffuse import (
    EXPECTED_CIFAR10_SPLIT_SHA256,
    default_bundle_root,
    default_checkpoint_path,
    probe_rediffuse_assets,
)


def local_rediffuse_assets_ready() -> bool:
    return default_bundle_root().exists() and default_checkpoint_path().exists()


@unittest.skipUnless(local_rediffuse_assets_ready(), "local ReDiffuse collaborator assets are not present")
class ReDiffuseAssetTests(unittest.TestCase):
    def test_probe_rediffuse_assets_reports_ready(self) -> None:
        payload = probe_rediffuse_assets()

        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["checks"]["required_files"])
        self.assertTrue(payload["checks"]["split_hash"])
        self.assertEqual(payload["split"]["sha256"], EXPECTED_CIFAR10_SPLIT_SHA256)
        self.assertEqual(payload["checkpoint"]["step"], 750000)
        self.assertTrue(payload["checkpoint"]["has_ema_model"])
        self.assertEqual(payload["provenance"]["seed"], 42)
        self.assertEqual(payload["provenance"]["seed_evidence"], "collaborator-statement")

    def test_cli_probe_rediffuse_assets_reports_ready(self) -> None:
        from diffaudit.cli import main

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["probe-rediffuse-assets"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(Path(payload["paths"]["bundle_root"]), default_bundle_root())


if __name__ == "__main__":
    unittest.main()
