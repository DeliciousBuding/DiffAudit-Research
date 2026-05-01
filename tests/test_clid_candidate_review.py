import json
import tempfile
import unittest
from pathlib import Path


class ClidCandidateReviewTests(unittest.TestCase):
    def _write_packet(self, root: Path) -> None:
        member_dir = root / "datasets" / "member"
        nonmember_dir = root / "datasets" / "nonmember"
        outputs = root / "outputs"
        summary_dir = root / "score-summary-workspace"
        member_dir.mkdir(parents=True)
        nonmember_dir.mkdir(parents=True)
        outputs.mkdir()
        summary_dir.mkdir()
        member_rows = []
        nonmember_rows = []
        for index in range(4):
            filename = f"{index:03d}.png"
            (member_dir / filename).write_bytes(f"m-{index}".encode("ascii"))
            (nonmember_dir / filename).write_bytes(f"n-{index}".encode("ascii"))
            member_rows.append(json.dumps({"file_name": filename, "text": f"member prompt {index}"}))
            nonmember_rows.append(json.dumps({"file_name": filename, "text": f"nonmember prompt {index}"}))
        (member_dir / "metadata.jsonl").write_text("\n".join(member_rows), encoding="utf-8")
        (nonmember_dir / "metadata.jsonl").write_text("\n".join(nonmember_rows), encoding="utf-8")
        (outputs / "scores_TRTE_train.txt").write_text(
            "header\n0.1\t-1\n0.2\t-2\n0.3\t-3\n0.4\t-4\n",
            encoding="utf-8",
        )
        (outputs / "scores_TRTE_test.txt").write_text(
            "header\n0.9\t1\n0.8\t2\n0.7\t3\n0.6\t4\n",
            encoding="utf-8",
        )
        (summary_dir / "score-summary.json").write_text(
            json.dumps(
                {
                    "method": "clid",
                    "low_fpr_gate": {"passed": True},
                }
            ),
            encoding="utf-8",
        )

    def test_blocks_small_split_even_when_score_gate_passed(self) -> None:
        from diffaudit.attacks.clid_candidate_review import review_clid_candidate_packet

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._write_packet(root)
            payload = review_clid_candidate_packet(root, permutations=16)

        self.assertEqual(payload["status"], "blocked")
        self.assertIn("balanced_split_rows", payload["blocking"])
        self.assertEqual(payload["overlap"]["image_sha256"], 0)


if __name__ == "__main__":
    unittest.main()
