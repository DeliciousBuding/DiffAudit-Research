"""
One-click runner for the Stable Diffusion MIA experiment.
Reproduces Table 3 of the paper (both Laion5 and Laion5-BLIP rows).

Steps executed automatically:
  1. Download LAION member images + prepare COCO nonmember split
  2. (optional) Generate BLIP captions for laion5_blip
  3. Run all 5 attackers on laion5
  4. Run all 5 attackers on laion5_blip

Usage:
    python run_experiment.py                       # full run, laion5 only
    python run_experiment.py --also-blip           # also run laion5_blip
    python run_experiment.py --skip-prepare        # skip data download
    python run_experiment.py --attackers ReDiffuse # single attacker
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

ALL_ATTACKERS = ["SecMI", "PIA", "PIAN", "Naive", "ReDiffuse"]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _run(cmd: List[str], cwd: Path, log_file: Path, env: dict) -> Tuple[int, str]:
    print("\n[RUN]", " ".join(cmd), flush=True)
    proc = subprocess.Popen(
        cmd, cwd=str(cwd), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    lines: List[str] = []
    with log_file.open("a", encoding="utf-8") as lf:
        for line in proc.stdout or []:
            sys.stdout.write(line)
            lf.write(line)
            lines.append(line)
    rc = proc.wait()
    return rc, "".join(lines)


def _parse_metrics(output: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for key, prefix in [("AUC", "AUC:"), ("ASR", "ASR:"),
                         ("TP@1FPR", "TPR @ 1% FPR:"), ("threshold", "Threshold:")]:
        for line in output.splitlines():
            if prefix in line:
                result[key] = line.split(prefix, 1)[1].strip()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir",  default=".")
    parser.add_argument("--python-exe",   default=sys.executable)
    parser.add_argument("--member-size",  type=int,  default=2500)
    parser.add_argument("--batch-size",   type=int,  default=4)
    parser.add_argument("--seed",         type=int,  default=0)
    # Paper Appendix A exact settings
    parser.add_argument("--attack-num",   type=int,  default=1)
    parser.add_argument("--interval",     type=int,  default=10)
    parser.add_argument("--k",            type=int,  default=10)
    parser.add_argument("--average",      type=int,  default=10)
    parser.add_argument("--checkpoint",   default="CompVis/stable-diffusion-v1-4")
    parser.add_argument("--attackers",    default=",".join(ALL_ATTACKERS))
    parser.add_argument("--prepare-mode", choices=["random", "high-mem"], default="random",
                        help="random uses prepare_laion_stable_data.py; high-mem selects memorization-prone LAION members.")
    parser.add_argument("--skip-prepare", action="store_true")
    parser.add_argument("--also-blip",    action="store_true",
                        help="Also run laion5_blip after laion5.")
    parser.add_argument("--score-mode",   default="first",
                        help="ReDiffuse scalar mode: first,last,mean,median,max,min,step0,...")
    parser.add_argument("--rediffuse-scorer", default="original_ssim",
                        help="ReDiffuse feature: original_ssim,vae_ssim,latent_mse.")
    parser.add_argument("--torch-dtype",  default="auto",
                        help="Model dtype for attack.py: auto,float16,float32.")
    parser.add_argument("--save-scores",  action="store_true",
                        help="Save ReDiffuse per-step SSIM features and select the best detector offline.")
    parser.add_argument("--runs-dir",     default="runs",
                        help="Output directory for runs; relative paths are resolved from project-dir.")
    parser.add_argument("--run-name",     default="")
    args = parser.parse_args()

    root    = Path(args.project_dir).resolve()
    py      = Path(args.python_exe)
    attackers = [a.strip() for a in args.attackers.split(",") if a.strip()]
    unknown   = set(attackers) - set(ALL_ATTACKERS)
    if unknown:
        raise ValueError(f"Unknown attackers: {unknown}")

    run_id  = args.run_name.strip() or datetime.now().strftime("run_%Y%m%d_%H%M%S")
    runs_dir = Path(args.runs_dir)
    if not runs_dir.is_absolute():
        runs_dir = root / runs_dir
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    log     = run_dir / "all.log"
    csv_out = run_dir / "result.csv"
    csv_out.write_text("dataset,attacker,attack_num,interval,k,average,AUC,ASR,TP@1FPR,threshold,score_mode,rediffuse_scorer\n",
                       encoding="utf-8")
    summary = run_dir / "summary.json"

    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    results: Dict[str, Dict] = {}

    # 1 — prepare data
    if not args.skip_prepare:
        prepare_script = "prepare_high_memorization_members.py" if args.prepare_mode == "high-mem" else "prepare_laion_stable_data.py"
        rc, _ = _run(
            [str(py), "-u", prepare_script,
             "--project-dir", str(root), "--member-size", str(args.member_size),
             "--seed", str(args.seed)],
            root, log, env,
        )
        if rc != 0:
            print("[ERROR] data preparation failed")
            return rc

    # helper to run one dataset
    def _run_dataset(dataset: str) -> bool:
        nonlocal results
        # optionally generate BLIP captions
        if dataset == "laion5_blip":
            rc, _ = _run(
                [str(py), "-u", "generate_blip_captions.py",
                 "--project-dir", str(root)],
                root, log, env,
            )
            if rc != 0:
                print("[ERROR] BLIP caption generation failed")
                return False

        for attacker in attackers:
            scores_npz = run_dir / f"{dataset}_{attacker}_scores.npz"
            cmd = [
                str(py), "-u", "attack.py",
                "--attacker_name", attacker,
                "--dataset",       dataset,
                "--checkpoint",    args.checkpoint,
                "--attack_num",    str(args.attack_num),
                "--interval",      str(args.interval),
                "--k",             str(args.k),
                "--average",       str(args.average),
                "--seed",          str(args.seed),
                "--batch_size",    str(args.batch_size),
                "--result_csv",    str(csv_out),
                "--torch_dtype",   args.torch_dtype,
            ]
            if attacker == "ReDiffuse":
                cmd += ["--score_mode", args.score_mode, "--rediffuse_scorer", args.rediffuse_scorer]
                if args.save_scores:
                    cmd += ["--scores_npz", str(scores_npz)]
            rc, out = _run(
                cmd,
                root, log, env,
            )
            m = _parse_metrics(out)
            results[f"{dataset}/{attacker}"] = {"rc": rc, **m}
            if rc != 0:
                print(f"[ERROR] {attacker} on {dataset} failed")
                return False
            if attacker == "ReDiffuse" and args.save_scores and scores_npz.exists():
                rc_sel, _ = _run(
                    [str(py), "-u", "select_rediffuse_detector.py",
                     "--scores-npz", str(scores_npz),
                     "--output-json", str(run_dir / f"{dataset}_mia_detector_rediffuse_best.json"),
                     "--output-csv", str(run_dir / f"{dataset}_rediffuse_score_selection.csv"),
                     "--checkpoint", args.checkpoint],
                    root, log, env,
                )
                if rc_sel != 0:
                    print("[ERROR] ReDiffuse score selection failed")
                    return False
            print(f"[ok] {dataset}/{attacker}: {m}")
        return True

    # 2 — laion5
    ok = _run_dataset("laion5")

    # 3 — laion5_blip (optional)
    if ok and args.also_blip:
        _run_dataset("laion5_blip")

    summary.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[DONE] results → {csv_out}")
    print(f"       summary  → {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
