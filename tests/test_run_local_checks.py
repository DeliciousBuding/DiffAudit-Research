import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.util import run_local_checks


class RunLocalChecksTests(unittest.TestCase):
    def test_main_uses_explicit_python_for_all_commands(self) -> None:
        recorded: list[tuple[list[str], Path]] = []

        def fake_run(cmd: list[str], cwd: Path) -> None:
            recorded.append((cmd, cwd))

        with patch.object(run_local_checks, "run", side_effect=fake_run):
            run_local_checks.main(["--fast", "--python", "/portable/python"])

        self.assertGreaterEqual(len(recorded), 5)
        for cmd, _ in recorded:
            self.assertEqual(cmd[0], "/portable/python")
        commands = [cmd for cmd, _ in recorded]
        self.assertIn(["/portable/python", "scripts/util/bootstrap_research_env.py"], commands)
        self.assertIn(["/portable/python", "scripts/util/check_public_surface.py"], commands)
        self.assertIn(["/portable/python", "scripts/util/check_markdown_links.py"], commands)
        self.assertIn(["/portable/python", "scripts/paper/validate_attack_defense_table.py"], commands)
        self.assertIn(["/portable/python", "scripts/paper/export_recon_product_evidence_card.py", "--check"], commands)
        self.assertIn(["/portable/python", "scripts/paper/export_admitted_evidence_bundle.py", "--check"], commands)
        self.assertTrue(
            any(
                cmd[:4] == ["/portable/python", "-m", "unittest", "tests.test_attack_registry"]
                for cmd in commands
            )
        )

    def test_main_uses_environment_python_when_not_explicit(self) -> None:
        recorded: list[tuple[list[str], Path]] = []

        def fake_run(cmd: list[str], cwd: Path) -> None:
            recorded.append((cmd, cwd))

        with patch.object(run_local_checks, "run", side_effect=fake_run):
            with patch.dict("os.environ", {"DIFFAUDIT_RESEARCH_PYTHON": "/env/python"}, clear=False):
                run_local_checks.main(["--fast"])

        self.assertGreaterEqual(len(recorded), 5)
        for cmd, _ in recorded:
            self.assertEqual(cmd[0], "/env/python")
        commands = [cmd for cmd, _ in recorded]
        self.assertIn(["/env/python", "scripts/util/bootstrap_research_env.py"], commands)
        self.assertIn(["/env/python", "scripts/util/check_public_surface.py"], commands)
        self.assertIn(["/env/python", "scripts/util/check_markdown_links.py"], commands)
        self.assertIn(["/env/python", "scripts/paper/validate_attack_defense_table.py"], commands)
        self.assertIn(["/env/python", "scripts/paper/export_recon_product_evidence_card.py", "--check"], commands)
        self.assertIn(["/env/python", "scripts/paper/export_admitted_evidence_bundle.py", "--check"], commands)
        self.assertTrue(
            any(
                cmd[:4] == ["/env/python", "-m", "unittest", "tests.test_attack_registry"]
                for cmd in commands
            )
        )

    def test_main_uses_repo_root_from_script_location(self) -> None:
        recorded: list[tuple[list[str], Path]] = []

        def fake_run(cmd: list[str], cwd: Path) -> None:
            recorded.append((cmd, cwd))

        with patch.object(run_local_checks, "run", side_effect=fake_run):
            run_local_checks.main(["--fast"])

        expected_root = Path(run_local_checks.__file__).resolve().parents[2]
        self.assertTrue(recorded)
        for _, cwd in recorded:
            self.assertEqual(cwd, expected_root)


if __name__ == "__main__":
    unittest.main()
