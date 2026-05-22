import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from tests.helpers import capture_cli_json


def _write_probe_package(
    root: Path,
    *,
    member_columns: list[str] | None = None,
    member_rows: int = 4,
    member_filenames: list[str] | None = None,
    member_script_uses_hidden_id: bool = True,
) -> Path:
    package_root = root / "copymark-laion-mi"
    package_root.mkdir(parents=True, exist_ok=True)

    columns = member_columns or ["url", "caption"]
    rows = []
    for idx in range(member_rows):
        row = {
            "url": f"https://example.com/{idx}.jpg",
            "caption": f"caption {idx}",
        }
        if "image_id" in columns:
            row["image_id"] = idx
        rows.append({key: row[key] for key in columns})
    pd.DataFrame(rows).to_parquet(package_root / "members.parquet", index=False)

    filenames = member_filenames or [f"{1000 + idx}.png" for idx in range(member_rows)]
    (package_root / "pia_laion_mi_image_log.json").write_text(
        json.dumps({"member": filenames, "nonmember": [f"{idx}.png" for idx in range(member_rows)]}, indent=2),
        encoding="utf-8",
    )

    hidden_id_expr = "int(df.iloc[idx, 2])" if member_script_uses_hidden_id else "idx"
    (package_root / "get_laion_mi_2_5k_member_img_caption.py").write_text(
        "\n".join(
            [
                "import pandas as pd",
                "def main(df):",
                f"    return {hidden_id_expr}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return package_root


class CopyMarkLaionMiProbeTests(unittest.TestCase):
    def test_probe_blocks_hidden_id_binding_gap(self) -> None:
        from diffaudit.attacks.copymark_laion_mi import probe_copymark_laion_mi_assets

        with tempfile.TemporaryDirectory() as tmpdir:
            package_root = _write_probe_package(
                Path(tmpdir),
                member_columns=["url", "caption"],
                member_rows=4,
                member_filenames=["28311127.png", "438659.png", "26246441.png", "19213348.png"],
                member_script_uses_hidden_id=True,
            )
            payload = probe_copymark_laion_mi_assets(package_root=package_root)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["track"], "black-box")
        self.assertEqual(payload["method"], "copymark_laion_mi")
        self.assertTrue(payload["checks"]["member_parquet"])
        self.assertTrue(payload["checks"]["member_image_log"])
        self.assertTrue(payload["checks"]["member_script"])
        self.assertTrue(payload["checks"]["public_member_schema_has_two_columns"])
        self.assertTrue(payload["checks"]["member_script_uses_hidden_id_column"])
        self.assertFalse(payload["checks"]["member_filenames_within_public_row_range"])
        self.assertFalse(payload["checks"]["binding_reconstructible_from_public_surface"])
        self.assertEqual(payload["member_parquet"]["columns"], ["url", "caption"])
        self.assertEqual(payload["member_image_log"]["max_numeric_member_id"], 28311127)

    def test_probe_reports_ready_when_public_surface_is_row_bindable(self) -> None:
        from diffaudit.attacks.copymark_laion_mi import probe_copymark_laion_mi_assets

        with tempfile.TemporaryDirectory() as tmpdir:
            package_root = _write_probe_package(
                Path(tmpdir),
                member_columns=["url", "caption"],
                member_rows=4,
                member_filenames=["0.png", "1.png", "2.png", "3.png"],
                member_script_uses_hidden_id=False,
            )
            payload = probe_copymark_laion_mi_assets(package_root=package_root)

        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["checks"]["binding_reconstructible_from_public_surface"])
        self.assertTrue(payload["checks"]["member_filenames_within_public_row_range"])
        self.assertFalse(payload["checks"]["member_script_uses_hidden_id_column"])

    def test_cli_probe_reports_blocked(self) -> None:
        from diffaudit.cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            package_root = _write_probe_package(
                Path(tmpdir),
                member_columns=["url", "caption"],
                member_rows=4,
                member_filenames=["28311127.png", "438659.png", "26246441.png", "19213348.png"],
                member_script_uses_hidden_id=True,
            )
            exit_code, payload = capture_cli_json(
                main,
                ["probe-copymark-laion-mi-assets", "--package-root", str(package_root)],
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["paths"]["package_root"], str(package_root))


if __name__ == "__main__":
    unittest.main()
