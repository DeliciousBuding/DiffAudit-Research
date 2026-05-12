import os
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import run_pr_checks


class RunPrChecksTests(unittest.TestCase):
    def test_main_uses_current_python_and_repo_root(self) -> None:
        recorded: list[tuple[list[str], Path]] = []

        def fake_run(cmd: list[str], cwd: Path) -> None:
            recorded.append((cmd, cwd))

        with patch.object(run_pr_checks, "run", side_effect=fake_run):
            run_pr_checks.main()

        expected_root = Path(run_pr_checks.__file__).resolve().parents[1]
        self.assertEqual(len(recorded), 3)
        for cmd, cwd in recorded:
            self.assertEqual(cmd[0], run_pr_checks.sys.executable)
            self.assertEqual(cwd, expected_root)

        commands = [cmd[1:] for cmd, _ in recorded]
        self.assertIn(["scripts/run_docs_checks.py"], commands)
        self.assertIn(["-m", "compileall", "-q", "src", "scripts", "tests"], commands)
        self.assertTrue(any(cmd[:2] == ["-c", "from diffaudit.cli import build_parser; parser = build_parser(); assert parser.prog == 'diffaudit'"] for cmd in commands))

    def test_run_sets_pythonpath_and_utf8(self) -> None:
        captured: dict[str, object] = {}

        def fake_subprocess_run(cmd: list[str], cwd: str, env: dict[str, str], check: bool) -> object:
            captured["cmd"] = cmd
            captured["cwd"] = cwd
            captured["env"] = env
            captured["check"] = check

            class Completed:
                returncode = 0

            return Completed()

        with patch.object(run_pr_checks.subprocess, "run", side_effect=fake_subprocess_run):
            with patch.dict(os.environ, {"PYTHONPATH": "existing"}, clear=False):
                run_pr_checks.run(["python", "-V"], Path("repo"))

        env = captured["env"]
        self.assertIsInstance(env, dict)
        self.assertEqual(env["PYTHONUTF8"], "1")
        self.assertEqual(env["PYTHONPATH"], f"{Path('repo') / 'src'}{os.pathsep}existing")
        self.assertEqual(captured["cwd"], "repo")
        self.assertFalse(captured["check"])


if __name__ == "__main__":
    unittest.main()
