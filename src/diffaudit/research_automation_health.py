from __future__ import annotations

import re
import subprocess
from pathlib import Path

RUN_SUMMARY_PATTERN = re.compile(r"workspaces/[^\s`)]*/runs/[^\s`)]*/summary\.json")


def extract_priority_ladder(roadmap_text: str) -> dict[str, list[str]]:
    sections = {"Top now": [], "Next": [], "Then": []}
    current: str | None = None
    for raw_line in roadmap_text.splitlines():
        line = raw_line.strip()
        header = line.lstrip("#").strip()
        if header in sections:
            current = header
            continue
        if current and line.startswith(tuple(f"{index}." for index in range(1, 20))):
            sections[current].append(line)
        elif current and line.startswith("---"):
            current = None
    return sections


def extract_repo_signals(repo_root: Path) -> dict[str, list[dict[str, str]]]:
    markdown_paths = sorted(repo_root.rglob("*.md"))
    gpu_candidates: list[dict[str, str]] = []
    idle_reasons: list[dict[str, str]] = []
    anchors: list[dict[str, str]] = []
    for path in markdown_paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel_path = path.relative_to(repo_root).as_posix()
        for index, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            lowered = line.lower()
            if "next gpu candidate" in lowered:
                gpu_candidates.append({"path": rel_path, "line": str(index), "text": line})
            if "active_gpu_question" in lowered or "gpu is idle" in lowered or "current gpu state" in lowered:
                idle_reasons.append({"path": rel_path, "line": str(index), "text": line})
            for match in RUN_SUMMARY_PATTERN.findall(line):
                anchors.append({"path": rel_path, "line": str(index), "text": match})
    return {
        "gpu_candidates": gpu_candidates,
        "idle_reasons": idle_reasons,
        "run_summary_mentions": anchors,
    }


def _git_path_status(repo_root: Path, relative_path: str) -> str:
    target = relative_path.replace("/", "\\")
    tracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", "--", target],
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode == 0:
        return "tracked"
    ignored = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "--", target],
        capture_output=True,
        text=True,
        check=False,
    )
    if ignored.returncode == 0:
        return "ignored"
    return "untracked"


def audit_research_automation_health(repo_root: Path) -> dict[str, object]:
    roadmap_path = repo_root / "ROADMAP.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    ladder = extract_priority_ladder(roadmap_text)
    repo_signals = extract_repo_signals(repo_root)

    run_anchor_checks = []
    for item in repo_signals["run_summary_mentions"]:
        rel_path = item["text"]
        file_path = repo_root / Path(rel_path)
        run_anchor_checks.append(
            {
                "source_path": item["path"],
                "source_line": int(item["line"]),
                "run_summary_path": rel_path,
                "exists": file_path.exists(),
                "git_status": _git_path_status(repo_root, rel_path),
            }
        )

    tracked_count = sum(1 for item in run_anchor_checks if item["git_status"] == "tracked")
    ignored_count = sum(1 for item in run_anchor_checks if item["git_status"] == "ignored")
    missing_count = sum(1 for item in run_anchor_checks if not item["exists"])

    friction_points = []
    if not repo_signals["gpu_candidates"]:
        friction_points.append("no explicit next GPU candidate markers found in markdown notes")
    if not repo_signals["idle_reasons"]:
        friction_points.append("no explicit active GPU state markers found in markdown notes")
    if ignored_count > 0:
        friction_points.append("some run-summary anchors point to ignored files and need force-add discipline")
    if missing_count > 0:
        friction_points.append("some run-summary anchors point to missing files")

    status = "healthy enough with bounded friction" if not missing_count else "friction detected"
    return {
        "status": status,
        "priority_ladder": ladder,
        "gpu_candidates": repo_signals["gpu_candidates"][:10],
        "idle_reasons": repo_signals["idle_reasons"][:10],
        "run_summary_anchor_checks": run_anchor_checks[:20],
        "counts": {
            "gpu_candidate_markers": len(repo_signals["gpu_candidates"]),
            "idle_reason_markers": len(repo_signals["idle_reasons"]),
            "run_summary_mentions": len(run_anchor_checks),
            "tracked_run_summaries": tracked_count,
            "ignored_run_summaries": ignored_count,
            "missing_run_summaries": missing_count,
        },
        "friction_points": friction_points,
    }
