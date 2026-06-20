from __future__ import annotations

import unittest

from scripts.check_public_surface import candidate_promotion_violations_from_text


class CandidatePromotionLanguageTests(unittest.TestCase):
    def test_flags_direct_candidate_promotion(self) -> None:
        hits = candidate_promotion_violations_from_text("H2 is an admitted black-box row.")

        self.assertTrue(hits)

    def test_flags_metadata_drift_release_promotion(self) -> None:
        hits = candidate_promotion_violations_from_text(
            "Current arXiv DOI metadata and a live GitHub repository prove compute release."
        )

        self.assertTrue(hits)

    def test_keeps_negated_metadata_boundary_clean(self) -> None:
        hits = candidate_promotion_violations_from_text(
            "Current arXiv DOI metadata and a live GitHub repository do not prove compute release."
        )

        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
