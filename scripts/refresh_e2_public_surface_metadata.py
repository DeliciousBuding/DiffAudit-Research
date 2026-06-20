"""Refresh no-download metadata for E2 public-surface scout rows.

The script reads the E2 scout queue and inspects public source metadata only:
repository metadata, root/tree file names, dataset card metadata, Zenodo file
catalogs, arXiv entry metadata, and OpenReview note/page metadata. It does not
download datasets, weights, archives, generated payloads, or model files.
"""

from __future__ import annotations

import csv
import datetime as dt
import argparse
import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_DIR = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"
DEFAULT_SCOUT_QUEUE = PREFLIGHT_DIR / "e2_n50_public_surface_scout_2026_06_06.csv"
DEFAULT_OUT_CSV = PREFLIGHT_DIR / "e2_n50_public_surface_metadata_refresh.csv"
DEFAULT_OUT_MD = PREFLIGHT_DIR / "e2_n50_public_surface_metadata_refresh.md"
DEFAULT_OUT_GATE_QUEUE_CSV = PREFLIGHT_DIR / "e2_n50_scout_gate_review_queue.csv"

USER_AGENT = "DiffAudit-E2-Metadata-Refresh/2026-06-06"
MAX_TEXT_BYTES = 256_000
MAX_SIGNAL_ITEMS = 24

SCORE_TERMS = re.compile(
    r"(score|scores|metric|metrics|auc|roc|result|results|logit|logits|tensor|"
    r"feature|features|csv|json|npy|npz|pkl|pickle|parquet)",
    re.IGNORECASE,
)
SPLIT_TERMS = re.compile(r"(split|member|nonmember|non-member|train|test|holdout|shadow)", re.IGNORECASE)
CHECKPOINT_TERMS = re.compile(r"(checkpoint|ckpt|weight|weights|model|safetensors|\.pt|\.pth|\.bin)", re.IGNORECASE)
RESPONSE_TERMS = re.compile(r"(response|responses|generated|sample|samples|image|images|video|audio)", re.IGNORECASE)
CODE_TERMS = re.compile(r"(\.py|\.ipynb|requirements|environment|setup|src/|scripts?/|code)", re.IGNORECASE)
CONTEXT_ITEM_PREFIXES = (
    "abstract:",
    "cardData:",
    "description:",
    "language:",
    "page_title:",
    "pdf:",
    "resource_type:",
    "tags:",
    "title:",
    "topics:",
)

NON_PAYLOAD_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".csv",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".ipynb",
    ".xml",
}

GITHUB_README_NAMES = ("README.md", "README.MD", "readme.md", "Readme.md")

IDENTITY_OUTPUT_COLUMNS = [
    "github_head_shas",
    "github_tree_shas",
    "hf_shas",
    "zenodo_file_fingerprints",
    "arxiv_versions",
    "openreview_note_ids",
]
EXPECTED_IDENTITY_COLUMNS = {
    "github_head_shas": "expected_github_head_shas",
    "github_tree_shas": "expected_github_tree_shas",
    "hf_shas": "expected_hf_shas",
    "zenodo_file_fingerprints": "expected_zenodo_file_fingerprints",
    "arxiv_versions": "expected_arxiv_versions",
    "openreview_note_ids": "expected_openreview_note_ids",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate_urls(row: dict[str, str]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for part in row.get("public_source_candidates", "").split(";"):
        value = part.strip().rstrip(".,;`'")
        if not value.startswith(("http://", "https://")) or value in seen:
            continue
        seen.add(value)
        urls.append(value)
    return urls


def unique_join(values: list[str]) -> str:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        compact = re.sub(r"\s+", " ", str(value or "").strip())
        if not compact or compact in seen:
            continue
        seen.add(compact)
        output.append(compact)
    return ";".join(output)


def split_identity_values(value: str) -> set[str]:
    return {part.strip() for part in str(value or "").split(";") if part.strip()}


def identity_values_match(expected: set[str], actual: set[str]) -> bool:
    for expected_value in expected:
        if not any(
            expected_value == actual_value
            or actual_value.startswith(expected_value + "|")
            or actual_value.startswith(expected_value + "@")
            for actual_value in actual
        ):
            return False
    return True


def fetch_text(url: str, timeout: int = 20, max_bytes: int = MAX_TEXT_BYTES) -> tuple[int | None, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(max_bytes)
            return int(resp.status), resp.geturl(), data.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read(min(max_bytes, 4096)).decode("utf-8", errors="replace")
        return int(exc.code), exc.geturl() or url, body
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, url, f"ERROR: {exc}"


def fetch_json(url: str) -> tuple[int | None, str, object | None, str]:
    status, final_url, text = fetch_text(url)
    if status is None or not (200 <= status < 300):
        return status, final_url, None, text[:300]
    try:
        return status, final_url, json.loads(text), ""
    except json.JSONDecodeError as exc:
        return status, final_url, None, f"json decode error: {exc}"


def github_repo(url: str) -> tuple[str, str] | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def git_ls_remote_head(owner: str, name: str, branch: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{owner}/{name}.git", f"refs/heads/{branch}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    first = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else ""
    parts = first.split()
    if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]{40}", parts[0]):
        return parts[0].lower()
    return ""


def git_remote_default_branch(owner: str, name: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "ls-remote", "--symref", f"https://github.com/{owner}/{name}.git", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    for line in completed.stdout.splitlines():
        match = re.match(r"ref:\s+refs/heads/([^\s]+)\s+HEAD", line)
        if match:
            return match.group(1)
    return ""


def git_tree_fallback(owner: str, name: str, branch: str) -> tuple[list[str], str]:
    """List repository paths from Git tree metadata without checking out blobs."""

    repo_url = f"https://github.com/{owner}/{name}.git"
    items: list[str] = []
    with tempfile.TemporaryDirectory(prefix="diffaudit-git-tree-") as tmpdir:
        clone_cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--no-checkout",
            "--single-branch",
            "--branch",
            branch,
            repo_url,
            tmpdir,
        ]
        try:
            clone = subprocess.run(
                clone_cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [], f"git_tree_fallback_error={type(exc).__name__}"
        if clone.returncode != 0:
            error = re.sub(r"\s+", " ", (clone.stderr or clone.stdout).strip())[:160]
            return [], f"git_tree_fallback_status={clone.returncode}; git_tree_fallback_error={error}"

        try:
            tree = subprocess.run(
                ["git", "-C", tmpdir, "ls-tree", "-r", "--name-only", "HEAD"],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [], f"git_tree_fallback_error={type(exc).__name__}"
        if tree.returncode != 0:
            error = re.sub(r"\s+", " ", (tree.stderr or tree.stdout).strip())[:160]
            return [], f"git_tree_fallback_status={tree.returncode}; git_tree_fallback_error={error}"

        for path in tree.stdout.splitlines()[:2000]:
            normalized = path.strip()
            if not normalized:
                continue
            ext = Path(normalized).suffix.lower()
            if ext in NON_PAYLOAD_EXTENSIONS or any(
                term in normalized.lower()
                for term in ["split", "score", "metric", "result", "member", "checkpoint", "response", "sample"]
            ):
                items.append(normalized)
    return items[:1000], f"git_tree_fallback=ok; git_tree_fallback_count={len(items)}"


def hf_dataset_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "huggingface.co":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) >= 3 and parts[0] == "datasets":
        return "/".join(parts[1:3])
    return None


def hf_model_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "huggingface.co":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) >= 2 and parts[0] not in {"datasets", "spaces", "organizations"}:
        return "/".join(parts[:2])
    return None


def zenodo_record_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "zenodo.org":
        return None
    match = re.search(r"/records/(\d+)", parsed.path)
    return match.group(1) if match else None


def arxiv_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "arxiv.org":
        return None
    match = re.search(r"/abs/([^/?#]+)", parsed.path)
    return match.group(1) if match else None


def openreview_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "openreview.net":
        return None
    query = urllib.parse.parse_qs(parsed.query)
    values = query.get("id")
    return values[0] if values else None


def signal_counts(items: list[str]) -> dict[str, int]:
    text_items = [item for item in items if is_artifact_signal_item(item)]
    return {
        "code_hint_count": sum(1 for item in text_items if CODE_TERMS.search(item)),
        "split_hint_count": sum(1 for item in text_items if SPLIT_TERMS.search(item)),
        "score_metric_hint_count": sum(1 for item in text_items if SCORE_TERMS.search(item)),
        "checkpoint_hint_count": sum(1 for item in text_items if CHECKPOINT_TERMS.search(item)),
        "response_hint_count": sum(1 for item in text_items if RESPONSE_TERMS.search(item)),
    }


def is_artifact_signal_item(item: str) -> bool:
    value = item.strip()
    if not value:
        return False
    if value.startswith(CONTEXT_ITEM_PREFIXES):
        return False
    if re.match(r"^README(?:\.[Mm][Dd])?:", value):
        return False
    return True


def sample_items(items: list[str]) -> str:
    cleaned: list[str] = []
    for item in [item for item in items if is_artifact_signal_item(item)]:
        compact = re.sub(r"\s+", " ", item.strip())
        if not compact or compact in cleaned:
            continue
        cleaned.append(compact[:120])
        if len(cleaned) >= MAX_SIGNAL_ITEMS:
            break
    return " | ".join(cleaned)


def metadata_rate_limited(notes: list[str]) -> bool:
    joined = " ".join(notes).lower()
    return "api rate limit exceeded" in joined or "rate_limited=1" in joined


def classify_artifact_surface(
    counts: dict[str, int],
    source_kinds: set[str],
    risk: str,
    notes: list[str],
) -> str:
    if metadata_rate_limited(notes) and not any(counts.values()):
        return "metadata_retry_needed"
    if counts["score_metric_hint_count"] and (counts["split_hint_count"] or counts["response_hint_count"]):
        return "score_or_metric_surface_hint"
    if counts["split_hint_count"] and counts["checkpoint_hint_count"]:
        return "split_checkpoint_surface_hint"
    if counts["split_hint_count"] and counts["response_hint_count"]:
        return "split_response_surface_hint"
    if counts["score_metric_hint_count"]:
        return "metric_only_surface_hint"
    if counts["split_hint_count"]:
        return "split_only_surface_hint"
    if counts["code_hint_count"]:
        return "code_only_surface_hint"
    if source_kinds <= {"arxiv", "openreview"}:
        return "paper_metadata_only"
    if "defense" in risk.lower() or "cross-modal" in risk.lower():
        return "semantic_or_modality_risk"
    return "no_artifact_surface_hint"


def classify_followup(bucket: str, risk: str) -> str:
    risk_lower = risk.lower()
    if bucket == "metadata_retry_needed":
        return "metadata_retry_needed"
    if bucket in {"score_or_metric_surface_hint", "split_checkpoint_surface_hint", "split_response_surface_hint"}:
        if "cross-modal" in risk_lower or "defense" in risk_lower or "semantic" in risk_lower:
            return "review_semantics_before_freeze_candidate"
        return "priority_gate_review"
    if bucket in {"metric_only_surface_hint", "split_only_surface_hint", "code_only_surface_hint"}:
        return "artifact_followup"
    if bucket == "paper_metadata_only":
        return "paper_source_only_backup"
    return "backup_or_exclude"


def summarize_identities(identity_maps: list[dict[str, str]]) -> dict[str, str]:
    github_head_values: list[str] = []
    github_tree_values: list[str] = []
    hf_values: list[str] = []
    zenodo_values: list[str] = []
    arxiv_values: list[str] = []
    openreview_values: list[str] = []

    for identity in identity_maps:
        repo = identity.get("github_repo", "")
        head = identity.get("github_head_sha", "")
        tree = identity.get("github_tree_sha") or identity.get("github_commit_tree_sha", "")
        if repo and head:
            github_head_values.append(f"{repo}@{head}")
        if repo and tree:
            github_tree_values.append(f"{repo}@tree:{tree}")

        hf_repo = identity.get("hf_repo_id", "")
        hf_sha = identity.get("hf_sha", "")
        if hf_repo and hf_sha:
            hf_values.append(f"{hf_repo}@{hf_sha}")

        record_id = identity.get("zenodo_record_id", "")
        for fingerprint in identity.get("zenodo_file_fingerprints", "").split(" || "):
            if record_id and fingerprint.strip():
                zenodo_values.append(f"{record_id}:{fingerprint.strip()}")

        arxiv_entry = identity.get("arxiv_entry_id", "")
        arxiv_updated = identity.get("arxiv_updated", "")
        if arxiv_entry:
            arxiv_values.append(f"{arxiv_entry}|updated={arxiv_updated}")

        openreview_note = identity.get("openreview_note_id", "")
        if openreview_note:
            tmdate = identity.get("openreview_tmdate", "")
            openreview_values.append(f"{openreview_note}|tmdate={tmdate}")

    summary = {
        "github_head_shas": unique_join(github_head_values),
        "github_tree_shas": unique_join(github_tree_values),
        "hf_shas": unique_join(hf_values),
        "zenodo_file_fingerprints": unique_join(zenodo_values),
        "arxiv_versions": unique_join(arxiv_values),
        "openreview_note_ids": unique_join(openreview_values),
    }
    identity_blob = json.dumps(summary, sort_keys=True, ensure_ascii=False)
    summary["identity_fingerprint_sha256"] = hashlib.sha256(identity_blob.encode("utf-8")).hexdigest()
    return summary


def classify_identity_delta(row: dict[str, str], identities: dict[str, str]) -> str:
    expected_seen = False
    missing_actual: list[str] = []
    mismatched: list[str] = []
    matched = 0
    for actual_column, expected_column in EXPECTED_IDENTITY_COLUMNS.items():
        expected = split_identity_values(row.get(expected_column, ""))
        if not expected:
            continue
        expected_seen = True
        actual = split_identity_values(identities.get(actual_column, ""))
        if not actual:
            missing_actual.append(actual_column)
            continue
        if identity_values_match(expected, actual):
            matched += 1
        else:
            mismatched.append(actual_column)
    if mismatched:
        return "identity_mismatch:" + ",".join(mismatched)
    if missing_actual:
        return "identity_unobserved:" + ",".join(missing_actual)
    if matched:
        return "identity_matched"
    if expected_seen:
        return "identity_baseline_unchecked"
    return "no_identity_baseline"


def compact_reopen_surface_hint(items: list[str]) -> str:
    artifact_items = [item for item in items if is_artifact_signal_item(item)]
    if not artifact_items:
        return "no_public_artifact_filename_hint"
    joined = "\n".join(artifact_items)
    manifest_or_verifier = re.search(
        r"(row[-_ ]?manifest|manifest|verifier|verify|metric[s]?\.json|roc|score[s]?\.csv|prediction[s]?\.csv|response[s]?\.json)",
        joined,
        re.IGNORECASE,
    )
    row_bound = re.search(
        r"(row[-_ ]?id|image[-_ ]?id|filename|member|nonmember|non[-_ ]member|label|y_true|y_pred)",
        joined,
        re.IGNORECASE,
    )
    if manifest_or_verifier and row_bound:
        return "filename_hint_manual_gate_review_needed"
    if manifest_or_verifier:
        return "compact_artifact_filename_hint_only"
    return "no_compact_reopen_surface_hint"


def github_metadata(url: str) -> tuple[str, list[str], str, dict[str, str]]:
    repo = github_repo(url)
    if not repo:
        return "unsupported", [], "", {}
    owner, name = repo
    identity = {"github_repo": f"{owner}/{name}"}
    api = f"https://api.github.com/repos/{owner}/{name}"
    status, _, payload, error = fetch_json(api)
    items: list[str] = []
    default_branch = "main"
    notes = f"github_repo_status={status}"
    if isinstance(payload, dict):
        default_branch = str(payload.get("default_branch") or "main")
        identity["github_default_branch"] = default_branch
        identity["github_pushed_at"] = str(payload.get("pushed_at") or "")
        identity["github_updated_at"] = str(payload.get("updated_at") or "")
        topics = payload.get("topics") or []
        items.extend(
            [
                f"description:{payload.get('description') or ''}",
                f"language:{payload.get('language') or ''}",
                f"topics:{','.join(topics) if isinstance(topics, list) else ''}",
            ]
        )
        branch_api = f"https://api.github.com/repos/{owner}/{name}/branches/{urllib.parse.quote(default_branch)}"
        branch_status, _, branch_payload, branch_error = fetch_json(branch_api)
        notes += f"; github_branch_status={branch_status}"
        if isinstance(branch_payload, dict):
            commit = branch_payload.get("commit") or {}
            if isinstance(commit, dict):
                identity["github_head_sha"] = str(commit.get("sha") or "")
                nested_commit = commit.get("commit") or {}
                if isinstance(nested_commit, dict):
                    tree = nested_commit.get("tree") or {}
                    if isinstance(tree, dict):
                        identity["github_commit_tree_sha"] = str(tree.get("sha") or "")
        elif branch_error:
            notes += f"; github_branch_error={branch_error[:120]}"
        if not identity.get("github_head_sha"):
            ls_remote_head = git_ls_remote_head(owner, name, default_branch)
            if ls_remote_head:
                identity["github_head_sha"] = ls_remote_head
                notes += "; git_ls_remote_head=ok"
        tree_url = f"https://api.github.com/repos/{owner}/{name}/git/trees/{urllib.parse.quote(default_branch)}?recursive=1"
        tree_status, _, tree_payload, tree_error = fetch_json(tree_url)
        notes += f"; github_tree_status={tree_status}"
        if isinstance(tree_payload, dict):
            identity["github_tree_sha"] = str(tree_payload.get("sha") or identity.get("github_commit_tree_sha", ""))
            truncated = bool(tree_payload.get("truncated"))
            notes += f"; tree_truncated={int(truncated)}"
            for entry in tree_payload.get("tree", [])[:1000]:
                path = str(entry.get("path") or "")
                ext = Path(path).suffix.lower()
                if ext in NON_PAYLOAD_EXTENSIONS or any(term in path.lower() for term in ["split", "score", "metric", "result", "member", "checkpoint", "response", "sample"]):
                    items.append(path)
        elif tree_error:
            notes += f"; github_tree_error={tree_error[:120]}"
    elif error:
        notes += f"; github_error={error[:120]}"
        if "API rate limit exceeded" in error:
            notes += "; github_rate_limited=1"
        remote_default_branch = git_remote_default_branch(owner, name)
        if remote_default_branch:
            default_branch = remote_default_branch
            identity["github_default_branch"] = default_branch
            notes += f"; git_remote_default_branch={default_branch}"
    if not identity.get("github_head_sha"):
        ls_remote_head = git_ls_remote_head(owner, name, default_branch)
        if ls_remote_head:
            identity["github_head_sha"] = ls_remote_head
            notes += "; git_ls_remote_head=ok"

    if "github_tree_status=200" not in notes:
        fallback_tree_items, fallback_tree_notes = git_tree_fallback(owner, name, default_branch)
        items.extend(fallback_tree_items)
        if fallback_tree_notes:
            notes += "; " + fallback_tree_notes

    fallback_items, fallback_notes = github_web_fallback(owner, name)
    items.extend(fallback_items)
    if fallback_notes:
        notes += "; " + fallback_notes
    return "github", items, notes, identity


def github_web_fallback(owner: str, name: str) -> tuple[list[str], str]:
    items: list[str] = []
    notes: list[str] = []

    for readme_name in GITHUB_README_NAMES:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{name}/HEAD/{readme_name}"
        status, _, text = fetch_text(raw_url, timeout=12, max_bytes=80_000)
        notes.append(f"raw_{readme_name}_status={status}")
        if status and 200 <= status < 300:
            items.append(f"{readme_name}:{text[:3000]}")
            break

    page_url = f"https://github.com/{owner}/{name}"
    status, _, text = fetch_text(page_url, timeout=12, max_bytes=180_000)
    notes.append(f"github_page_status={status}")
    if status and 200 <= status < 300:
        pattern = re.compile(
            rf'href="/{re.escape(owner)}/{re.escape(name)}/(?:blob|tree)/[^/]+/([^"#?]+)"'
        )
        for match in pattern.finditer(text):
            path = html.unescape(match.group(1))
            ext = Path(path).suffix.lower()
            if ext in NON_PAYLOAD_EXTENSIONS or any(
                term in path.lower()
                for term in ["split", "score", "metric", "result", "member", "checkpoint", "response", "sample"]
            ):
                items.append(path)
            if len(items) >= 300:
                break

    return items, "; ".join(notes)


def hf_metadata(url: str) -> tuple[str, list[str], str, dict[str, str]]:
    dataset_id = hf_dataset_id(url)
    model_id = hf_model_id(url)
    if dataset_id:
        repo_id = dataset_id
        kind = "huggingface_dataset"
        api = f"https://huggingface.co/api/datasets/{dataset_id}"
    elif model_id:
        repo_id = model_id
        kind = "huggingface_model"
        api = f"https://huggingface.co/api/models/{model_id}"
    else:
        return "unsupported", [], "", {}
    status, _, payload, error = fetch_json(api)
    items: list[str] = []
    identity = {"hf_repo_id": repo_id, "hf_repo_kind": kind}
    notes = f"{kind}_status={status}"
    if isinstance(payload, dict):
        identity["hf_sha"] = str(payload.get("sha") or "")
        identity["hf_last_modified"] = str(payload.get("lastModified") or "")
        items.append(f"cardData:{json.dumps(payload.get('cardData') or {}, ensure_ascii=False)[:300]}")
        for sibling in payload.get("siblings", [])[:1000]:
            name = str(sibling.get("rfilename") or "")
            if name:
                items.append(name)
        tags = payload.get("tags") or []
        if isinstance(tags, list):
            items.append(f"tags:{','.join(str(tag) for tag in tags[:30])}")
    elif error:
        notes += f"; hf_error={error[:120]}"
    return kind, items, notes, identity


def zenodo_metadata(url: str) -> tuple[str, list[str], str, dict[str, str]]:
    record_id = zenodo_record_id(url)
    if not record_id:
        return "unsupported", [], "", {}
    api = f"https://zenodo.org/api/records/{record_id}"
    status, _, payload, error = fetch_json(api)
    items: list[str] = []
    identity = {"zenodo_record_id": record_id}
    notes = f"zenodo_status={status}"
    if isinstance(payload, dict):
        metadata = payload.get("metadata") or {}
        identity["zenodo_doi"] = str(payload.get("doi") or metadata.get("doi") or "")
        identity["zenodo_updated"] = str(payload.get("updated") or metadata.get("modified") or "")
        items.append(f"title:{metadata.get('title') or ''}")
        items.append(f"resource_type:{metadata.get('resource_type') or metadata.get('upload_type') or ''}")
        fingerprints: list[str] = []
        for file_info in payload.get("files", [])[:200]:
            key = str(file_info.get("key") or "")
            size = file_info.get("size")
            checksum = str(file_info.get("checksum") or "")
            if key:
                fingerprints.append(f"{key}|size={size}|checksum={checksum}")
                items.append(f"{key} size={size} checksum={checksum[:32]}")
        identity["zenodo_file_fingerprints"] = " || ".join(fingerprints)
    elif error:
        notes += f"; zenodo_error={error[:120]}"
    return "zenodo_record", items, notes, identity


def arxiv_metadata(url: str) -> tuple[str, list[str], str, dict[str, str]]:
    paper_id = arxiv_id(url)
    if not paper_id:
        return "unsupported", [], "", {}
    api = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(paper_id)
    status, _, text = fetch_text(api)
    items: list[str] = []
    identity = {"arxiv_query_id": paper_id}
    notes = f"arxiv_status={status}"
    if status and 200 <= status < 300:
        try:
            root = ET.fromstring(text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find("atom:entry", ns)
            if entry is not None:
                entry_id = entry.findtext("atom:id", default="", namespaces=ns)
                updated = entry.findtext("atom:updated", default="", namespaces=ns)
                published = entry.findtext("atom:published", default="", namespaces=ns)
                title = entry.findtext("atom:title", default="", namespaces=ns)
                summary = entry.findtext("atom:summary", default="", namespaces=ns)
                identity["arxiv_entry_id"] = entry_id
                identity["arxiv_updated"] = updated
                identity["arxiv_published"] = published
                items.append(f"title:{title}")
                items.append(f"summary:{summary[:600]}")
        except ET.ParseError as exc:
            notes += f"; arxiv_parse_error={exc}"
    return "arxiv", items, notes, identity


def openreview_metadata(url: str) -> tuple[str, list[str], str, dict[str, str]]:
    note_id = openreview_id(url)
    if not note_id:
        return "unsupported", [], "", {}
    items: list[str] = []
    identity = {"openreview_note_id": note_id}
    notes_parts: list[str] = []
    for api in [
        "https://api2.openreview.net/notes?id=" + urllib.parse.quote(note_id),
        "https://api2.openreview.net/notes?forum=" + urllib.parse.quote(note_id),
    ]:
        status, _, payload, error = fetch_json(api)
        notes_parts.append(f"openreview_api_status={status}")
        if isinstance(payload, dict) and payload.get("notes"):
            for note in payload.get("notes", [])[:20]:
                if isinstance(note, dict):
                    identity.setdefault("openreview_note_number", str(note.get("number") or ""))
                    identity.setdefault("openreview_cdate", str(note.get("cdate") or ""))
                    identity.setdefault("openreview_tmdate", str(note.get("tmdate") or ""))
                content = note.get("content") or {}
                title = content.get("title", {})
                abstract = content.get("abstract", {})
                pdf = content.get("pdf", {})
                items.append(f"title:{title.get('value') if isinstance(title, dict) else title}")
                items.append(f"abstract:{abstract.get('value') if isinstance(abstract, dict) else abstract}")
                items.append(f"pdf:{pdf.get('value') if isinstance(pdf, dict) else pdf}")
        elif error:
            notes_parts.append(f"openreview_error={error[:120]}")
    if not items:
        status, _, text = fetch_text(url)
        notes_parts.append(f"openreview_page_status={status}")
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
        if title_match:
            items.append("page_title:" + html.unescape(re.sub(r"\s+", " ", title_match.group(1))).strip())
    return "openreview", items, "; ".join(notes_parts), identity


def inspect_url(url: str) -> tuple[str, list[str], str, dict[str, str]]:
    for inspector in [github_metadata, hf_metadata, zenodo_metadata, arxiv_metadata, openreview_metadata]:
        kind, items, notes, identity = inspector(url)
        if kind != "unsupported":
            return kind, items, notes, identity
    status, _, text = fetch_text(url, max_bytes=32_000)
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    item = ""
    if title_match:
        item = "page_title:" + html.unescape(re.sub(r"\s+", " ", title_match.group(1))).strip()
    return "generic_page", [item] if item else [], f"page_status={status}", {}


def refresh_row(row: dict[str, str], refreshed_at: str) -> dict[str, object]:
    source_kinds: set[str] = set()
    all_items: list[str] = []
    notes: list[str] = []
    identity_maps: list[dict[str, str]] = []
    urls = candidate_urls(row)
    for url in urls:
        kind, items, note, identity = inspect_url(url)
        source_kinds.add(kind)
        all_items.extend(items)
        identity_maps.append(identity)
        if note:
            notes.append(f"{url}: {note}")

    counts = signal_counts(all_items)
    identities = summarize_identities(identity_maps)
    artifact_bucket = classify_artifact_surface(counts, source_kinds, row.get("risk_or_duplicate", ""), notes)
    followup_bucket = classify_followup(artifact_bucket, row.get("risk_or_duplicate", ""))
    return {
        "refreshed_at_utc": refreshed_at,
        "queue_id": row["queue_id"],
        "title": row["title"],
        "url_count": len(urls),
        "source_kinds": ";".join(sorted(source_kinds)),
        **identities,
        "identity_delta_status": classify_identity_delta(row, identities),
        "compact_reopen_surface_hint": compact_reopen_surface_hint(all_items),
        "artifact_surface_hint": artifact_bucket,
        "followup_bucket": followup_bucket,
        **counts,
        "signal_items_sample": sample_items(all_items),
        "why_distinct": row.get("why_distinct", ""),
        "likely_false_promotion_relevance": row.get("likely_false_promotion_relevance", ""),
        "required_followup": row.get("required_followup", ""),
        "risk_or_duplicate": row.get("risk_or_duplicate", ""),
        "metadata_notes": " || ".join(notes)[:1200],
    }


def write_markdown(rows: list[dict[str, object]], refreshed_at: str, out_md: Path) -> None:
    bucket_counts: dict[str, int] = {}
    followup_counts: dict[str, int] = {}
    identity_counts: dict[str, int] = {}
    reopen_counts: dict[str, int] = {}
    for row in rows:
        bucket_counts[str(row["artifact_surface_hint"])] = bucket_counts.get(str(row["artifact_surface_hint"]), 0) + 1
        followup_counts[str(row["followup_bucket"])] = followup_counts.get(str(row["followup_bucket"]), 0) + 1
        identity_counts[str(row["identity_delta_status"])] = identity_counts.get(str(row["identity_delta_status"]), 0) + 1
        reopen_counts[str(row["compact_reopen_surface_hint"])] = (
            reopen_counts.get(str(row["compact_reopen_surface_hint"]), 0) + 1
        )

    lines = [
        "# E2 Public Surface Metadata Refresh",
        "",
        f"> Refreshed at: {refreshed_at}",
        "> Scope: no-download public metadata only; not artifact admission.",
        "",
        "## Artifact Surface Hints",
        "",
    ]
    for bucket, count in sorted(bucket_counts.items()):
        lines.append(f"- `{bucket}`: {count}")
    lines.extend(["", "## Follow-Up Buckets", ""])
    for bucket, count in sorted(followup_counts.items()):
        lines.append(f"- `{bucket}`: {count}")
    lines.extend(["", "## Identity Delta Status", ""])
    for bucket, count in sorted(identity_counts.items()):
        lines.append(f"- `{bucket}`: {count}")
    lines.extend(["", "## Compact Reopen Hints", ""])
    for bucket, count in sorted(reopen_counts.items()):
        lines.append(f"- `{bucket}`: {count}")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Title | Identity delta | Reopen hint | Artifact hint | Follow-up |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {queue_id} | {title} | `{identity_delta_status}` | `{compact_reopen_surface_hint}` | `{artifact_surface_hint}` | `{followup_bucket}` |".format(
                **{key: str(value).replace("|", "/") for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This high-value delta refresh records public metadata identity only: GitHub HEAD/tree identity, Hugging Face SHA, Zenodo file-list identity, OpenReview/arXiv metadata, and small public manifest/verifier filenames if they appear. It does not download archives, datasets, model shards, image/audio/video payloads, unpickle result files, run notebooks, execute attacks, or launch CPU/GPU/DCU reproduction.",
            "",
            "A source identity change is not admission evidence by itself. A row can reopen only when the public surface exposes a compact row manifest, safe row-bound score/response or prediction packet, metric JSON/ROC verifier, target/checkpoint identity, provenance hashes, and a label-shuffle, permutation, or surface-delta control. If those objects are absent, the current boundary remains: no C14/N50 update, no admitted evidence, no second public score/response asset, and no compute release.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def write_gate_review_queue(rows: list[dict[str, object]], out_gate_queue_csv: Path) -> None:
    review_order = {
        "priority_gate_review": 1,
        "review_semantics_before_freeze_candidate": 2,
        "artifact_followup": 3,
    }
    queue_rows: list[dict[str, object]] = []
    for row in sorted(
        [row for row in rows if str(row["followup_bucket"]) in review_order],
        key=lambda item: (review_order[str(item["followup_bucket"])], str(item["queue_id"])),
    ):
        queue_rows.append(
            {
                "review_order": len(queue_rows) + 1,
                "scout_queue_id": row["queue_id"],
                "title": row["title"],
                "artifact_surface_hint": row["artifact_surface_hint"],
                "followup_bucket": row["followup_bucket"],
                "source_kinds": row["source_kinds"],
                "gate_review_focus": row["required_followup"],
                "risk_or_duplicate": row["risk_or_duplicate"],
                "signal_items_sample": row["signal_items_sample"],
            }
        )
    write_csv(
        out_gate_queue_csv,
        queue_rows,
        [
            "review_order",
            "scout_queue_id",
            "title",
            "artifact_surface_hint",
            "followup_bucket",
            "source_kinds",
            "gate_review_focus",
            "risk_or_duplicate",
            "signal_items_sample",
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_SCOUT_QUEUE)
    parser.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--out-gate-queue-csv", type=Path, default=DEFAULT_OUT_GATE_QUEUE_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    refreshed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = [refresh_row(row, refreshed_at) for row in read_csv(args.input_csv)]
    fieldnames = [
        "refreshed_at_utc",
        "queue_id",
        "title",
        "url_count",
        "source_kinds",
        *IDENTITY_OUTPUT_COLUMNS,
        "identity_fingerprint_sha256",
        "identity_delta_status",
        "compact_reopen_surface_hint",
        "artifact_surface_hint",
        "followup_bucket",
        "code_hint_count",
        "split_hint_count",
        "score_metric_hint_count",
        "checkpoint_hint_count",
        "response_hint_count",
        "signal_items_sample",
        "why_distinct",
        "likely_false_promotion_relevance",
        "required_followup",
        "risk_or_duplicate",
        "metadata_notes",
    ]
    write_csv(args.out_csv, rows, fieldnames)
    write_gate_review_queue(rows, args.out_gate_queue_csv)
    write_markdown(rows, refreshed_at, args.out_md)
    print(f"Wrote {args.out_csv} with {len(rows)} metadata row(s)")
    print(f"Wrote {args.out_gate_queue_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
