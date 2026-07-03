#!/usr/bin/env python
"""
Training Watchdog — monitors heartbeat.json and auto-restarts if stalled.
Usage:
  python watchdog.py --heartbeat <path/to/heartbeat.json> --restart-cmd "<command>"
"""

import sys, os, json, time, argparse, subprocess
from pathlib import Path
from datetime import datetime, timezone


def parse_args():
    p = argparse.ArgumentParser(description="Training Watchdog")
    p.add_argument("--heartbeat", required=True, help="Path to heartbeat.json")
    p.add_argument("--restart-cmd", required=True, help="Command to restart training")
    p.add_argument("--max-stale", type=int, default=600, help="Max seconds without heartbeat update (default: 600=10min)")
    p.add_argument("--check-every", type=int, default=60, help="Check interval in seconds (default: 60)")
    p.add_argument("--once", action="store_true", help="Check once and exit (for cron use)")
    return p.parse_args()


def read_heartbeat(path):
    try:
        data = json.loads(Path(path).read_text())
        ts = datetime.fromisoformat(data["timestamp"])
        return data, ts
    except Exception as e:
        return None, None


def main():
    args = parse_args()
    hb_path = Path(args.heartbeat)

    while True:
        data, ts = read_heartbeat(hb_path)
        now = datetime.now(timezone.utc)

        if data is None:
            print(f"[{now.isoformat()[:19]}] WATCHDOG: Cannot read heartbeat!")
            if args.once:
                sys.exit(1)
        else:
            age = (now - ts).total_seconds()
            step = data["step"]
            total = data["total_steps"]
            pct = step / total * 100

            if age > args.max_stale:
                print(f"[{now.isoformat()[:19]}] WATCHDOG: Heartbeat STALE ({age:.0f}s old, step={step}). RESTARTING...")
                subprocess.run(args.restart_cmd, shell=True)
                if args.once:
                    sys.exit(0)
            else:
                print(f"[{now.isoformat()[:19]}] OK: step={step}/{total} ({pct:.1f}%) age={age:.0f}s")

        if args.once:
            sys.exit(0)

        time.sleep(args.check_every)


if __name__ == "__main__":
    main()
