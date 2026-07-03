"""Check public-source URLs for the E2 N=50 preflight queue.

This is a lightweight reachability check. It does not download datasets,
weights, archives, or artifact payloads.
"""

from __future__ import annotations

import csv
import datetime as dt
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_DIR = ROOT / "docs" / "internal" / "e2-n50-freeze-preflight-2026-06-06"
REFRESH_QUEUE = PREFLIGHT_DIR / "e2_n50_public_source_refresh_queue.csv"
ACTIONABLE_QUEUE = PREFLIGHT_DIR / "e2_n50_actionable_queue.csv"
SCOUT_QUEUE = PREFLIGHT_DIR / "e2_n50_public_surface_scout_2026_06_06.csv"
OUT_CSV = PREFLIGHT_DIR / "e2_n50_public_source_url_check.csv"
OUT_MD = PREFLIGHT_DIR / "e2_n50_public_source_url_check.md"
OUT_ACTIONABLE_CSV = PREFLIGHT_DIR / "e2_n50_actionable_url_check.csv"
OUT_ACTIONABLE_MD = PREFLIGHT_DIR / "e2_n50_actionable_url_check.md"
OUT_SCOUT_CSV = PREFLIGHT_DIR / "e2_n50_public_surface_scout_url_check.csv"
OUT_SCOUT_MD = PREFLIGHT_DIR / "e2_n50_public_surface_scout_url_check.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate_urls(row: dict[str, str]) -> list[str]:
    values = []
    for field in ["public_source_candidates", "source_url", "artifact_url"]:
        values.extend(part.strip() for part in row.get(field, "").split(";"))

    urls: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value.startswith(("http://", "https://")):
            continue
        cleaned = value.rstrip(".,;`'")
        if cleaned in seen:
            continue
        seen.add(cleaned)
        urls.append(cleaned)
    return urls


def probe_url(url: str, timeout: int) -> dict[str, object]:
    headers = {
        "User-Agent": "DiffAudit-E2-Preflight/2026-06-06",
        "Range": "bytes=0-0",
    }
    for method in ["HEAD", "GET"]:
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if method == "GET":
                    resp.read(1)
                status = int(resp.status)
                return {
                    "method": method,
                    "status_code": status,
                    "ok": int(200 <= status < 400),
                    "final_url": resp.geturl(),
                    "content_type": resp.headers.get("Content-Type", ""),
                    "error": "",
                }
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 405, 501}:
                continue
            return {
                "method": method,
                "status_code": int(exc.code),
                "ok": 0,
                "final_url": exc.geturl() or url,
                "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
                "error": str(exc.reason),
            }
        except urllib.error.URLError as exc:
            if method == "HEAD":
                continue
            return {
                "method": method,
                "status_code": "",
                "ok": 0,
                "final_url": url,
                "content_type": "",
                "error": str(exc.reason),
            }
        except TimeoutError as exc:
            if method == "HEAD":
                continue
            return {
                "method": method,
                "status_code": "",
                "ok": 0,
                "final_url": url,
                "content_type": "",
                "error": str(exc),
            }
    return {
        "method": "",
        "status_code": "",
        "ok": 0,
        "final_url": url,
        "content_type": "",
        "error": "no probe attempted",
    }


def write_markdown(
    path: Path,
    rows: list[dict[str, object]],
    checked_at: str,
    title: str,
    scope_note: str,
) -> None:
    total = len(rows)
    ok_count = sum(int(row["ok"]) for row in rows)
    no_url_count = sum(1 for row in rows if not row["url"])
    by_domain: dict[str, int] = {}
    for row in rows:
        domain = urlparse(str(row["url"])).netloc
        if not domain:
            continue
        by_domain[domain] = by_domain.get(domain, 0) + 1

    lines = [
        f"# {title}",
        "",
        f"> Checked at: {checked_at}",
        f"> Scope: {scope_note}",
        "",
        "## Summary",
        "",
        f"- URL candidates probed: `{total - no_url_count}`",
        f"- reachable 2xx/3xx URLs: `{ok_count}`",
        f"- non-2xx/3xx or failed URLs: `{total - no_url_count - ok_count}`",
        f"- rows without URL candidate: `{no_url_count}`",
        "",
        "## Domain Counts",
        "",
    ]
    for domain, count in sorted(by_domain.items()):
        lines.append(f"- `{domain}`: {count}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "A reachable URL only proves that the public source can currently be opened. It does not prove row-bound target identity, score/response coverage, metric provenance, or consumer-boundary suitability.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def check_queue(queue_path: Path, out_csv: Path, out_md: Path, title: str, scope_note: str) -> int:
    checked_at = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = read_csv(queue_path)
    output_rows: list[dict[str, object]] = []
    for row in rows:
        urls = candidate_urls(row)
        if not urls:
            output_rows.append(
                {
                    "checked_at_utc": checked_at,
                    "queue_id": row.get("queue_id", ""),
                    "e2_seed_id": row.get("e2_seed_id", ""),
                    "title": row["title"],
                    "url": "",
                    "method": "",
                    "status_code": "",
                    "ok": 0,
                    "final_url": "",
                    "content_type": "",
                    "error": "no public URL candidate",
                }
            )
            continue
        for url in urls:
            result = probe_url(url, timeout=15)
            output_rows.append(
                {
                    "checked_at_utc": checked_at,
                    "queue_id": row.get("queue_id", ""),
                    "e2_seed_id": row.get("e2_seed_id", ""),
                    "title": row["title"],
                    "url": url,
                    **result,
                }
            )

    fieldnames = [
        "checked_at_utc",
        "queue_id",
        "e2_seed_id",
        "title",
        "url",
        "method",
        "status_code",
        "ok",
        "final_url",
        "content_type",
        "error",
    ]
    write_csv(out_csv, output_rows, fieldnames)
    write_markdown(out_md, output_rows, checked_at, title, scope_note)
    print(f"Wrote {out_csv} with {len(output_rows)} URL probe row(s)")
    return len(output_rows)


def main() -> int:
    check_queue(
        REFRESH_QUEUE,
        OUT_CSV,
        OUT_MD,
        "E2 Public Source URL Check",
        "lightweight URL reachability for the public-source refresh queue only; not artifact admission.",
    )
    check_queue(
        ACTIONABLE_QUEUE,
        OUT_ACTIONABLE_CSV,
        OUT_ACTIONABLE_MD,
        "E2 Actionable Queue URL Check",
        "lightweight URL reachability for all actionable/followup rows; not artifact admission.",
    )
    if SCOUT_QUEUE.exists():
        check_queue(
            SCOUT_QUEUE,
            OUT_SCOUT_CSV,
            OUT_SCOUT_MD,
            "E2 Public Surface Scout URL Check",
            "lightweight URL reachability for newly scouted public-surface candidates; not artifact admission.",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
