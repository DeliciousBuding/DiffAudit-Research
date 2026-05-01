import json
import tempfile
import unittest
from pathlib import Path


def _write_metadata(root: Path, split: str, prompts: list[str]) -> None:
    split_dir = root / "datasets" / split
    split_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        json.dumps({"file_name": f"{index:03d}.png", "text": prompt})
        for index, prompt in enumerate(prompts)
    ]
    (split_dir / "metadata.jsonl").write_text("\n".join(rows), encoding="utf-8")


class ClidPromptTextReviewTests(unittest.TestCase):
    def test_prompt_text_review_finds_separable_prompts(self) -> None:
        from diffaudit.attacks.clid_prompt_text_review import review_clid_prompt_text_only

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            member_prompts = [f"member unique smile train {index}" for index in range(100)]
            nonmember_prompts = [f"nonmember unique glasses test {index}" for index in range(100)]
            _write_metadata(root, "member", member_prompts)
            _write_metadata(root, "nonmember", nonmember_prompts)

            payload = review_clid_prompt_text_only(root, min_count=2)

        self.assertEqual(payload["status"], "ready")
        self.assertGreaterEqual(payload["metrics"]["auc"], 0.8)
        self.assertEqual(payload["verdict"], "prompt text alone is a strong split separator")

    def test_prompt_text_review_stays_low_on_identical_prompt_sets(self) -> None:
        from diffaudit.attacks.clid_prompt_text_review import review_clid_prompt_text_only

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            prompts = [f"shared prompt token {index % 10}" for index in range(100)]
            _write_metadata(root, "member", prompts)
            _write_metadata(root, "nonmember", prompts)

            payload = review_clid_prompt_text_only(root, min_count=2)

        self.assertEqual(payload["status"], "ready")
        self.assertLess(payload["metrics"]["auc"], 0.65)
        self.assertEqual(payload["verdict"], "prompt text alone is not a strong split separator")


if __name__ == "__main__":
    unittest.main()
