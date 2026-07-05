#!/usr/bin/env python3
"""pre-commit hook: reject new files with YYYYMMDD in filename."""
import re
import sys

PATTERN = re.compile(r"\d{8}")


def main() -> None:
    failed = False
    for f in sys.argv[1:]:
        if PATTERN.search(f):
            print(
                f"ERROR: {f} contains YYYYMMDD date pattern -- "
                f"use semantic name instead."
            )
            failed = True
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
