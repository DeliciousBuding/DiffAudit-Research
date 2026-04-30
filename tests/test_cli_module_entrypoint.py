import os
import subprocess
import sys
import unittest
from pathlib import Path


def _subcommands(parser):
    for action in parser._actions:
        if hasattr(action, "choices") and isinstance(action.choices, dict):
            return action.choices
    raise AssertionError("parser does not expose subcommands")


class CliModuleEntrypointTests(unittest.TestCase):
    def test_cli_package_exports_main_and_parser(self) -> None:
        from diffaudit.cli import build_parser, main

        self.assertTrue(callable(main))
        parser = build_parser()
        subcommands = _subcommands(parser)
        self.assertIn("plan-secmi", subcommands)
        self.assertIn("run-gsa-runtime-mainline", subcommands)
        self.assertIn("run-dpdm-w1-multi-shadow-comparator", subcommands)

    def test_dispatch_registry_matches_parser_subcommands(self) -> None:
        from diffaudit.cli import build_parser
        from diffaudit.cli._dispatch import _COMMAND_HANDLERS

        parser = build_parser()
        subcommands = _subcommands(parser)

        self.assertEqual(set(subcommands), set(_COMMAND_HANDLERS))
        for command, handler in _COMMAND_HANDLERS.items():
            self.assertTrue(callable(handler), command)

    def test_python_module_invocation_executes_main(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        env = dict(os.environ)
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(repo_root / "src") if not existing else f"{repo_root / 'src'}{os.pathsep}{existing}"

        completed = subprocess.run(
            [sys.executable, "-m", "diffaudit.cli", "unsupported-command"],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("invalid choice", completed.stderr)


if __name__ == "__main__":
    unittest.main()
