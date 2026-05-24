import unittest
from unittest.mock import patch

from scripts.run_h2_response_strength_validation import parse_args, seed_offsets_for_policy


class RunH2ResponseStrengthValidationTests(unittest.TestCase):
    def test_default_seed_offset_policy_preserves_existing_cache_shape(self) -> None:
        with patch("sys.argv", ["run_h2_response_strength_validation.py"]):
            args = parse_args()

        self.assertEqual(args.seed_offset_policy, "class-ordered")

    def test_class_ordered_policy_preserves_original_offsets(self) -> None:
        self.assertEqual(seed_offsets_for_policy("class-ordered", member_count=512), (0, 512))

    def test_shared_position_policy_uses_same_offsets_for_both_classes(self) -> None:
        self.assertEqual(seed_offsets_for_policy("shared-position", member_count=512), (0, 0))

    def test_unknown_policy_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown seed offset policy"):
            seed_offsets_for_policy("bad-policy", member_count=512)


if __name__ == "__main__":
    unittest.main()
