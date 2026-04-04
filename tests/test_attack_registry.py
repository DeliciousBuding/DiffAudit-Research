import unittest
from pathlib import Path
import tempfile


class AttackRegistryTests(unittest.TestCase):
    def test_returns_secmi_planner(self) -> None:
        from diffaudit.attacks.registry import get_attack_planner

        planner = get_attack_planner("secmi")

        self.assertEqual(planner.__name__, "build_secmi_plan")

    def test_rejects_unknown_attack(self) -> None:
        from diffaudit.attacks.registry import get_attack_planner

        with self.assertRaisesRegex(ValueError, "Unsupported attack method"):
            get_attack_planner("unknown")

    def test_vendored_secmi_module_imports(self) -> None:
        from third_party.secmi.mia_evals import secmia

        self.assertTrue(hasattr(secmia, "get_FLAGS"))
        self.assertTrue(hasattr(secmia, "secmi_attack"))

    def test_validates_external_secmi_workspace(self) -> None:
        from diffaudit.attacks.secmi import validate_secmi_workspace

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "SecMI"
            (workspace / "mia_evals").mkdir(parents=True)
            (workspace / "mia_evals" / "secmia.py").write_text("# secmi", encoding="utf-8")
            (workspace / "mia_evals" / "dataset_utils.py").write_text("# util", encoding="utf-8")
            (workspace / "model.py").write_text("# model", encoding="utf-8")
            (workspace / "diffusion.py").write_text("# diffusion", encoding="utf-8")

            result = validate_secmi_workspace(workspace)

        self.assertEqual(result["status"], "ready")
        self.assertIn("mia_evals", result["entrypoint"])

    def test_prepares_secmi_adapter_context(self) -> None:
        from diffaudit.attacks.secmi_adapter import prepare_secmi_adapter
        from diffaudit.config import load_audit_config

        config_text = """
task:
  name: secmi-adapter
  model_family: diffusion
  access_level: black_box
assets:
  dataset_id: cifar10-half
  dataset_name: cifar10
  dataset_root: D:/datasets/cifar10
  model_id: cifar10-ddpm
  model_dir: PLACEHOLDER
attack:
  method: secmi
  num_samples: 8
  parameters:
    t_sec: 100
    k: 10
report:
  output_dir: experiments/secmi-adapter
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "model"
            model_dir.mkdir()
            (model_dir / "flagfile.txt").write_text("flags", encoding="utf-8")
            (model_dir / "checkpoint.pt").write_text("best", encoding="utf-8")

            config_path = Path(tmpdir) / "audit.yaml"
            config_path.write_text(
                config_text.replace("PLACEHOLDER", str(model_dir).replace("\\", "/")),
                encoding="utf-8",
            )

            config = load_audit_config(config_path)
            context = prepare_secmi_adapter(config, "external/SecMI")

        self.assertEqual(context.plan.dataset, "cifar10")
        self.assertTrue(context.runner.entrypoint_path.endswith("mia_evals\\secmia.py"))
        self.assertEqual(context.module.__name__, "third_party.secmi.mia_evals.secmia")


if __name__ == "__main__":
    unittest.main()
