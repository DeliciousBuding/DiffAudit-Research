from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


PAPER = Path(__file__).resolve().parents[1]
REFS = PAPER / "refs.bib"
OUTPUT = PAPER / "data" / "reference_integrity_audit.csv"

ENTRY_RE = re.compile(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,", re.MULTILINE)
FIELD_LINE_RE = re.compile(r"^\s*(?P<field>[A-Za-z][A-Za-z0-9_]*)\s*=\s*(?P<value>.+?)\s*,?\s*$")
FIELDS = [
    "bib_key",
    "entry_type",
    "title",
    "year",
    "identifier_kind",
    "identifier_value",
    "verification_url",
    "http_status",
    "verification_status",
    "verification_note",
    "metadata_status",
    "metadata_source",
    "metadata_note",
    "checked_at_utc",
]


def parse_bib(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(ENTRY_RE.finditer(text))
    entries: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fields: dict[str, str] = {
            "entry_type": match.group("type").lower(),
            "bib_key": match.group("key"),
        }
        for raw_line in text[start:end].splitlines():
            field_match = FIELD_LINE_RE.match(raw_line)
            if not field_match:
                continue
            value = field_match.group("value").strip()
            if (value.startswith("{") and value.endswith("}")) or (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            fields[field_match.group("field").lower()] = value.strip()
        entries.append(fields)
    return entries


def fetch_status(url: str) -> tuple[int | None, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; DiffAudit reference-integrity audit)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status = int(getattr(response, "status", response.getcode()))
            payload = response.read(65536).decode("utf-8", errors="replace")
            return status, payload
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(4096).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        return None, str(exc)


def normalize_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"\\[`'\"^~=.]?\{([^{}]+)\}", r"\1", value)
    value = re.sub(r"\\[A-Za-z]+\s*", " ", value)
    value = value.replace("{", " ").replace("}", " ")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[^0-9A-Za-z]+", " ", value).lower()
    return " ".join(value.split())


def title_coverage(expected_title: str, observed_text: str) -> float:
    expected_tokens = [token for token in normalize_text(expected_title).split() if len(token) >= 3]
    if not expected_tokens:
        return 0.0
    observed = set(normalize_text(observed_text).split())
    hits = sum(1 for token in expected_tokens if token in observed)
    return hits / len(expected_tokens)


def title_matches(expected_title: str, observed_text: str) -> bool:
    expected = normalize_text(expected_title)
    observed = normalize_text(observed_text)
    if not expected or not observed:
        return False
    return expected in observed or observed in expected or title_coverage(expected_title, observed_text) >= 0.8


def year_matches(expected_year: str, observed_year: str) -> bool:
    return bool(expected_year) and expected_year == observed_year


def csl_metadata_for_doi(doi: str) -> tuple[str, str, str] | None:
    url = f"https://doi.org/{urllib.parse.quote(doi, safe='/')}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.citationstyles.csl+json",
            "User-Agent": "Mozilla/5.0 (compatible; DiffAudit reference-integrity audit)",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read(65536).decode("utf-8", errors="replace"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    title = str(data.get("title", "")).strip()
    issued = data.get("issued", {})
    year = ""
    if isinstance(issued, dict):
        date_parts = issued.get("date-parts", [])
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])
    return title, year, url


def crossref_metadata_for_doi(doi: str) -> tuple[str, str, str] | None:
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    status, payload = fetch_status(url)
    if status != 200:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    message = data.get("message", {})
    if not isinstance(message, dict):
        return None
    titles = message.get("title", [])
    title = str(titles[0]).strip() if titles else ""
    issued = message.get("issued", {})
    year = ""
    if isinstance(issued, dict):
        date_parts = issued.get("date-parts", [])
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])
    return title, year, url


def arxiv_metadata(eprint: str) -> tuple[str, str, str] | None:
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(eprint)}"
    status, payload = fetch_status(url)
    if status != 200:
        return None
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError:
        return None
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", namespace)
    if entry is None:
        return None
    title = " ".join(entry.findtext("atom:title", default="", namespaces=namespace).split())
    published = entry.findtext("atom:published", default="", namespaces=namespace)
    year = published[:4] if published else ""
    return title, year, url


def metadata_check(entry: dict[str, str], payload: str = "") -> tuple[str, str, str]:
    expected_title = entry.get("title", "")
    expected_year = entry.get("year", "")
    doi = entry.get("doi", "").strip()
    eprint = entry.get("eprint", "").strip()
    archive_prefix = entry.get("archiveprefix", "").lower()

    metadata: tuple[str, str, str] | None = None
    source = ""
    if doi:
        metadata = csl_metadata_for_doi(doi)
        source = "doi_csl_json"
        if metadata is None:
            metadata = crossref_metadata_for_doi(doi)
            source = "crossref"
    elif eprint and archive_prefix == "arxiv":
        metadata = arxiv_metadata(eprint)
        source = "arxiv_api"
    elif payload:
        coverage = title_coverage(expected_title, payload)
        if title_matches(expected_title, payload):
            return "verified", "url_payload", f"verified: title token coverage={coverage:.2f}"
        return "failed", "url_payload", f"failed: title token coverage={coverage:.2f}"

    if metadata is None:
        return "failed", source or "metadata_unavailable", "failed: metadata endpoint unavailable"
    observed_title, observed_year, source_url = metadata
    title_ok = title_matches(expected_title, observed_title)
    year_ok = year_matches(expected_year, observed_year)
    if title_ok and year_ok:
        return "verified", source, f"verified: title/year match via {source_url}"
    return (
        "failed",
        source,
        f"failed: title_match={int(title_ok)} year_match={int(year_ok)} observed_title={observed_title!r} observed_year={observed_year!r}",
    )


def verify_doi(doi: str) -> tuple[str, str | None, str]:
    url = f"https://doi.org/api/handles/{urllib.parse.quote(doi, safe='/')}"
    status, payload = fetch_status(url)
    if status == 200:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return url, status and str(status), "failed: DOI handle response was not JSON"
        if data.get("responseCode") == 1:
            return url, str(status), "verified: DOI handle exists"
        return url, str(status), f"failed: DOI handle responseCode={data.get('responseCode')!r}"
    return url, "" if status is None else str(status), "failed: DOI handle endpoint did not return 200"


def verify_url(url: str, label: str) -> tuple[str, str | None, str]:
    status, _ = fetch_status(url)
    if status is not None and 200 <= status < 400:
        return url, str(status), f"verified: {label} resolved"
    return url, "" if status is None else str(status), f"failed: {label} did not resolve with 2xx/3xx"


def audit_entry(entry: dict[str, str], checked_at: str) -> dict[str, str]:
    doi = entry.get("doi", "").strip()
    eprint = entry.get("eprint", "").strip()
    archive_prefix = entry.get("archiveprefix", "").lower()
    url = entry.get("url", "").strip()
    if eprint and archive_prefix == "arxiv" and doi.lower().startswith("10.48550/arxiv."):
        value = eprint
        verification_url, http_status, note = verify_url(f"https://arxiv.org/abs/{value}", "arXiv abstract")
        kind = "arxiv_abs"
        metadata_status, metadata_source, metadata_note = metadata_check(entry)
    elif doi:
        verification_url, http_status, note = verify_doi(doi)
        kind = "doi_handle"
        value = doi
        metadata_status, metadata_source, metadata_note = metadata_check(entry)
    elif eprint and archive_prefix == "arxiv":
        value = eprint
        verification_url, http_status, note = verify_url(f"https://arxiv.org/abs/{value}", "arXiv abstract")
        kind = "arxiv_abs"
        metadata_status, metadata_source, metadata_note = metadata_check(entry)
    elif url:
        value = url
        status, payload = fetch_status(url)
        if status is not None and 200 <= status < 400:
            verification_url, http_status, note = url, str(status), "verified: reference URL resolved"
        else:
            verification_url = url
            http_status = "" if status is None else str(status)
            note = "failed: reference URL did not resolve with 2xx/3xx"
        kind = "url"
        metadata_status, metadata_source, metadata_note = metadata_check(entry, payload)
    else:
        kind = "missing_identifier"
        value = ""
        verification_url = ""
        http_status = ""
        note = "failed: no DOI, arXiv eprint, or URL available"
        metadata_status = "failed"
        metadata_source = "missing_identifier"
        metadata_note = "failed: no metadata source available"

    return {
        "bib_key": entry.get("bib_key", ""),
        "entry_type": entry.get("entry_type", ""),
        "title": entry.get("title", ""),
        "year": entry.get("year", ""),
        "identifier_kind": kind,
        "identifier_value": value,
        "verification_url": verification_url,
        "http_status": http_status or "",
        "verification_status": "verified" if note.startswith("verified:") else "failed",
        "verification_note": note,
        "metadata_status": metadata_status,
        "metadata_source": metadata_source,
        "metadata_note": metadata_note,
        "checked_at_utc": checked_at,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows = [audit_entry(entry, checked_at) for entry in parse_bib(REFS)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    failed = [row for row in rows if row["verification_status"] != "verified"]
    print(f"Wrote {args.output} ({len(rows)} references; {len(failed)} failed)")
    if failed:
        for row in failed:
            print(f"FAILED {row['bib_key']}: {row['verification_note']}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
