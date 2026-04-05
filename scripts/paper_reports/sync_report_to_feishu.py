from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


PUBLIC_PERMISSION_PAYLOAD = {
    "link_share_entity": "anyone_readable",
    "share_entity": "anyone",
    "external_access_entity": "open",
    "comment_entity": "anyone_can_view",
    "copy_entity": "anyone_can_view",
    "security_entity": "anyone_can_view",
}


def run_command(args: list[str], cwd: Path) -> dict:
    completed = subprocess.run(
        args,
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def extract_doc_id(payload: dict) -> str:
    data = payload.get("data", {})
    doc_id = data.get("doc_id") or data.get("document_id")
    if doc_id:
        return doc_id
    url = data.get("url") or data.get("doc_url")
    if url:
        match = re.search(r"/docx/([A-Za-z0-9]+)", url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract doc_id from payload: {payload}")


def remove_local_markdown_images(markdown: str) -> str:
    return re.sub(r"(?m)^!\[[^\]]*\]\([^)]+\)\s*$", "", markdown)


def derive_title(report_path: Path, markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return report_path.stem


def create_or_update_doc(
    cwd: Path,
    title: str,
    markdown: str,
    doc: str | None,
) -> str:
    if doc:
        payload = run_command(
            [
                "lark-cli",
                "docs",
                "+update",
                "--as",
                "user",
                "--doc",
                doc,
                "--mode",
                "overwrite",
                "--markdown",
                markdown,
            ],
            cwd,
        )
        return extract_doc_id(payload)

    payload = run_command(
        [
            "lark-cli",
            "docs",
            "+create",
            "--as",
            "user",
            "--title",
            title,
            "--markdown",
            markdown,
        ],
        cwd,
    )
    return extract_doc_id(payload)


def set_public_permission(cwd: Path, doc_id: str) -> None:
    run_command(
        [
            "lark-cli",
            "api",
            "PATCH",
            f"/open-apis/drive/v2/permissions/{doc_id}/public",
            "--params",
            json.dumps({"type": "docx"}, ensure_ascii=True),
            "--data",
            json.dumps(PUBLIC_PERMISSION_PAYLOAD, ensure_ascii=True),
            "--as",
            "user",
        ],
        cwd,
    )


def insert_image(cwd: Path, doc_id: str, image_path: Path, caption: str | None) -> None:
    relative_path = Path(image_path).resolve().relative_to(cwd.resolve())
    args = [
        "lark-cli",
        "docs",
        "+media-insert",
        "--as",
        "user",
        "--doc",
        f"https://www.feishu.cn/docx/{doc_id}",
        "--type",
        "image",
        "--file",
        str(relative_path),
    ]
    if caption:
        args.extend(["--caption", caption])
    run_command(args, cwd)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or update a Feishu report doc from a local Markdown report.",
    )
    parser.add_argument("report", type=Path, help="Local Markdown report path")
    parser.add_argument(
        "--doc",
        type=str,
        default=None,
        help="Existing Feishu doc URL or doc_id to update",
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=None,
        help="Optional local image asset to insert after markdown upload",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Optional explicit Feishu doc title",
    )
    parser.add_argument(
        "--image-caption",
        type=str,
        default=None,
        help="Optional caption for the inserted image",
    )
    args = parser.parse_args()

    cwd = Path.cwd()
    markdown_raw = args.report.read_text(encoding="utf-8")
    markdown_upload = remove_local_markdown_images(markdown_raw)
    title = args.title or derive_title(args.report, markdown_raw)

    doc_id = create_or_update_doc(cwd, title, markdown_upload, args.doc)
    set_public_permission(cwd, doc_id)

    if args.image:
        insert_image(cwd, doc_id, args.image, args.image_caption)

    print(
        json.dumps(
            {
                "doc_id": doc_id,
                "doc_url": f"https://www.feishu.cn/docx/{doc_id}",
                "title": title,
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
