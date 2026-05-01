import json
import tempfile
import unittest
from pathlib import Path


def _write_rows(path: Path, texts: list[str]) -> None:
    rows = []
    for index, text in enumerate(texts):
        rows.append(json.dumps({"file_name": f"{index:03d}.png", "text": text}))
    path.write_text("\n".join(rows), encoding="utf-8")


def _read_texts(path: Path) -> list[str]:
    return [
        json.loads(line)["text"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class ClidPromptPerturbationTests(unittest.TestCase):
    def test_fixed_prompt_rewrites_both_splits(self) -> None:
        from scripts.perturb_clid_bridge_prompts import perturb_metadata_prompts

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            member_path = root / "member.jsonl"
            nonmember_path = root / "nonmember.jsonl"
            _write_rows(member_path, ["member one", "member two"])
            _write_rows(nonmember_path, ["nonmember one", "nonmember two"])

            payload = perturb_metadata_prompts(
                member_path,
                nonmember_path,
                mode="fixed",
                prompt="a face",
            )

            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["mode"], "fixed")
            self.assertEqual(_read_texts(member_path), ["a face", "a face"])
            self.assertEqual(_read_texts(nonmember_path), ["a face", "a face"])

    def test_swap_split_prompts_preserves_rows_and_swaps_text(self) -> None:
        from scripts.perturb_clid_bridge_prompts import perturb_metadata_prompts

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            member_path = root / "member.jsonl"
            nonmember_path = root / "nonmember.jsonl"
            _write_rows(member_path, ["member one", "member two"])
            _write_rows(nonmember_path, ["nonmember one", "nonmember two"])

            payload = perturb_metadata_prompts(
                member_path,
                nonmember_path,
                mode="swap-split-prompts",
                prompt="unused",
            )

            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["mode"], "swap-split-prompts")
            self.assertEqual(_read_texts(member_path), ["nonmember one", "nonmember two"])
            self.assertEqual(_read_texts(nonmember_path), ["member one", "member two"])

    def test_swap_split_prompts_requires_balanced_rows(self) -> None:
        from scripts.perturb_clid_bridge_prompts import perturb_metadata_prompts

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            member_path = root / "member.jsonl"
            nonmember_path = root / "nonmember.jsonl"
            _write_rows(member_path, ["member one"])
            _write_rows(nonmember_path, ["nonmember one", "nonmember two"])

            with self.assertRaisesRegex(ValueError, "equal member and nonmember row counts"):
                perturb_metadata_prompts(
                    member_path,
                    nonmember_path,
                    mode="swap-split-prompts",
                    prompt="unused",
                )

    def test_within_split_shuffle_preserves_split_prompt_sets(self) -> None:
        from scripts.perturb_clid_bridge_prompts import perturb_metadata_prompts

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            member_path = root / "member.jsonl"
            nonmember_path = root / "nonmember.jsonl"
            member_prompts = ["member one", "member two", "member three", "member four"]
            nonmember_prompts = ["nonmember one", "nonmember two", "nonmember three", "nonmember four"]
            _write_rows(member_path, member_prompts)
            _write_rows(nonmember_path, nonmember_prompts)

            payload = perturb_metadata_prompts(
                member_path,
                nonmember_path,
                mode="within-split-shuffle",
                prompt="unused",
                seed=3,
            )

            shuffled_member_prompts = _read_texts(member_path)
            shuffled_nonmember_prompts = _read_texts(nonmember_path)
            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["mode"], "within-split-shuffle")
            self.assertCountEqual(shuffled_member_prompts, member_prompts)
            self.assertCountEqual(shuffled_nonmember_prompts, nonmember_prompts)
            self.assertNotEqual(shuffled_member_prompts, member_prompts)
            self.assertNotEqual(shuffled_nonmember_prompts, nonmember_prompts)


if __name__ == "__main__":
    unittest.main()
