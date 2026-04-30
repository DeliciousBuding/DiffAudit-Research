from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Callable


def capture_cli_json(main: Callable[[list[str]], int], argv: list[str]) -> tuple[int, dict[str, Any]]:
    stdout = StringIO()
    with redirect_stdout(stdout):
        exit_code = main(argv)
    return exit_code, json.loads(stdout.getvalue())

