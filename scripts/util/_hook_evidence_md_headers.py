#!/usr/bin/env python3
"""pre-commit hook: require Date/Status/Verdict headers in evidence docs."""
import sys
from pathlib import Path

REQUIRED_HEADERS = ["**Date:**", "**Status:**", "**Verdict:**"]


def main() -> None:
    failed = False
    for f in sys.argv[1:]:
        content = Path(f).read_text(encoding="utf-8")
        missing = [h for h in REQUIRED_HEADERS if h not in content]
        if missing:
            print(
                f"ERROR: {f} missing headers in docs/evidence/: "
                f"{', '.join(missing)}"
            )
            failed = True
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
