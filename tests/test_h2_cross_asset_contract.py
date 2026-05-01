import tempfile
import unittest
from pathlib import Path


class H2CrossAssetContractTests(unittest.TestCase):
    def _make_assets(self, root: Path) -> tuple[Path, Path, Path]:
        sd15 = root / "sd15"
        for name in ("unet", "vae", "text_encoder", "tokenizer", "scheduler"):
            (sd15 / name).mkdir(parents=True)
        (sd15 / "model_index.json").write_text("{}", encoding="utf-8")

        celeba = root / "celeba"
        celeba.mkdir()
        for name in ("img_align_celeba.zip", "identity_CelebA.txt", "list_eval_partition.txt"):
            (celeba / name).write_text("x", encoding="utf-8")

        recon = root / "recon"
        split = recon / "derived-public-10"
        split.mkdir(parents=True)
        (split / "target_member.pt").write_bytes(b"member")
        (split / "target_non_member.pt").write_bytes(b"nonmember")
        lora = recon / "model-checkpoints" / "celeba_partial_target" / "checkpoint-25000"
        lora.mkdir(parents=True)
        (lora / "pytorch_lora_weights.bin").write_bytes(b"weights")
        return sd15, celeba, recon

    def test_text_to_image_is_protocol_blocked_even_when_assets_ready(self) -> None:
        from diffaudit.attacks.h2_cross_asset import (
            evaluate_h2_cross_asset_contract,
            inspect_celeba_assets,
            inspect_recon_celeba_assets,
            inspect_sd15_assets,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            sd15, celeba, recon = self._make_assets(Path(tmpdir))
            payload = evaluate_h2_cross_asset_contract(
                endpoint_mode="text_to_image",
                sd15_assets=inspect_sd15_assets(sd15),
                celeba_assets=inspect_celeba_assets(celeba),
                recon_assets=inspect_recon_celeba_assets(recon),
                controlled_repeats=True,
                response_images_observable=True,
            )

        self.assertTrue(payload["asset_ready"])
        self.assertFalse(payload["protocol_ready"])
        self.assertEqual(payload["status"], "blocked_protocol_mismatch")

    def test_image_to_image_with_repeats_is_eligible_contract(self) -> None:
        from diffaudit.attacks.h2_cross_asset import (
            evaluate_h2_cross_asset_contract,
            inspect_celeba_assets,
            inspect_recon_celeba_assets,
            inspect_sd15_assets,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            sd15, celeba, recon = self._make_assets(Path(tmpdir))
            payload = evaluate_h2_cross_asset_contract(
                endpoint_mode="image_to_image",
                sd15_assets=inspect_sd15_assets(sd15),
                celeba_assets=inspect_celeba_assets(celeba),
                recon_assets=inspect_recon_celeba_assets(recon),
                controlled_repeats=True,
                response_images_observable=True,
            )

        self.assertEqual(payload["status"], "eligible_cpu_contract")


if __name__ == "__main__":
    unittest.main()
