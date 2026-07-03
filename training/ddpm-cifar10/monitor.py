#!/usr/bin/env python
"""Training monitor: read log, check heartbeat, report status. Called by cron.
Improvements from 2026-06-22 outage:
- Session-aware: only flags errors from current SESSION START boundary
- Heartbeat detection: reads heartbeat.json to detect liveness
- Stale detection: alerts if heartbeat is older than 5 min (training likely dead)
"""
import sys, json, re, os
from pathlib import Path
from datetime import datetime, timezone

PROJECT = Path(__file__).resolve().parents[2]  # Research/
DOWNLOAD = Path(os.environ.get("DIFFAUDIT_DOWNLOAD_ROOT", PROJECT.parent / "Download")).expanduser()
RUN_LABEL = os.environ.get("DIFFAUDIT_RUN_LABEL", "ddpm-cifar10-750k")

LOG = PROJECT / "training" / "outputs" / RUN_LABEL / "training.log"
CKPT_DIR = DOWNLOAD / "checkpoints" / RUN_LABEL
OUT = PROJECT / "training" / "outputs" / RUN_LABEL / "monitor.json"
HEARTBEAT = PROJECT / "training" / "outputs" / RUN_LABEL / "heartbeat.json"

def main():
    status = {"time": datetime.now().isoformat(), "ok": True, "step": 0, "loss": None, "eta_h": None, "checkpoints": [], "errors": [], "alive": False}

    if not LOG.exists():
        status["ok"] = False
        status["errors"].append("Log file not found")
        OUT.write_text(json.dumps(status, indent=2))
        print(json.dumps(status, indent=2))
        return

    text = LOG.read_text(encoding="utf-8", errors="replace")
    lines = text.strip().split("\n")

    # Session-aware error detection: only flag errors from latest SESSION START
    session_start_idx = 0
    for i in range(len(lines) - 1, -1, -1):
        if "SESSION START" in lines[i]:
            session_start_idx = i
            break
    recent_lines = lines[session_start_idx:]

    for line in recent_lines:
        if "Error" in line or "Traceback" in line or "NaN" in line:
            status["errors"].append(line)
        if "[RECOVER]" in line:
            status["errors"].append(line)  # Flag recoveries too — useful for diagnostics

    # Parse last training line (from entire log — step counter is monotonic)
    for line in reversed(lines):
        m = re.match(r"\[(\d+)/750000\] loss=([\d.]+) grad=([\d.]+) lr=([\d.e+\-]+) eta=([\d.]+)h", line)
        if m:
            status["step"] = int(m.group(1))
            status["loss"] = float(m.group(2))
            status["eta_h"] = float(m.group(5))
            break

    # Heartbeat: check if training is alive (backward-compat: may not exist yet)
    if HEARTBEAT.exists():
        try:
            hb = json.loads(HEARTBEAT.read_text())
            hb_time = datetime.fromisoformat(hb["timestamp"])
            age_sec = (datetime.now(timezone.utc) - hb_time).total_seconds()
            status["heartbeat_age_sec"] = round(age_sec)
            status["heartbeat_step"] = hb.get("step", 0)
            status["alive"] = age_sec < 300  # 5 min threshold
        except Exception:
            pass
    else:
        status["alive"] = True  # No heartbeat file yet, assume alive

    # Check checkpoints
    for ckpt in sorted(CKPT_DIR.glob("checkpoint-step*.pt")):
        status["checkpoints"].append({"name": ckpt.name, "size_mb": ckpt.stat().st_size / 1024**2})

    # Disk
    try:
        import shutil
        usage = shutil.disk_usage(CKPT_DIR)
        status["disk_gb_free"] = usage.free / 1024**3
    except:
        pass

    status["ok"] = status["alive"] and len(status["errors"]) == 0

    # Minimal output for cron
    alive_tag = "" if status["alive"] else " DEAD?"
    lines_out = [f"[{status['step']:06d}/750000] loss={status['loss']} eta={status['eta_h']}h ckpts={len(status['checkpoints'])} disk={status.get('disk_gb_free', '?'):.0f}GB{alive_tag}"]
    if not status["alive"] and status.get("heartbeat_age_sec"):
        lines_out.append(f"  [STALE] last heartbeat {status['heartbeat_age_sec']}s ago")
    if status["errors"]:
        lines_out.append(f"ERRORS: {len(status['errors'])}")
        for e in status["errors"][-3:]:
            lines_out.append(f"  {e[:120]}")

    # Auto-plot loss curve (unchanged)
    try:
        steps, losses = [], []
        for line in text.strip().split("\n"):
            m = re.match(r'\[(\d+)/750000\] loss=([\d.]+)', line)
            if m:
                steps.append(int(m.group(1)))
                losses.append(float(m.group(2)))
        if len(losses) >= 5:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import numpy as np
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(steps, losses, alpha=0.3, linewidth=0.5, color='steelblue')
            if len(losses) >= 20:
                w = min(20, len(losses)//2)
                smoothed = np.convolve(losses, np.ones(w)/w, mode='valid')
                ax.plot(steps[w-1:], smoothed, linewidth=1.5, color='darkred')
            ax.set_xlabel('Step'), ax.set_ylabel('MSE Loss')
            ax.set_title(f'DDPM CIFAR-10 750k — Loss ({steps[0]}-{steps[-1]})')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(str(LOG.parent / "loss_curve.png"), dpi=120)
            plt.close()
    except Exception:
        pass

    OUT.write_text(json.dumps(status, indent=2))
    print("\n".join(lines_out))

if __name__ == "__main__":
    main()
