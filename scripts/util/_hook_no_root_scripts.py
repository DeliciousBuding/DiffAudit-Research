#!/usr/bin/env python3
"""pre-commit hook: reject new .py files directly in scripts/ root."""
import sys
from pathlib import Path


def main() -> None:
    failed = False
    for f in sys.argv[1:]:
        p = Path(f)
        if p.parent == Path("scripts") and p.suffix == ".py":
            print(
                f"ERROR: {f} is in scripts/ root -- "
                f"move to a subdirectory (e.g., scripts/util/, scripts/h1/)."
            )
            failed = True
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
