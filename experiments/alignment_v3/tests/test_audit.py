import unittest

from audit import original_step_marked_bad, tie_summary


class AuditSensitivityTests(unittest.TestCase):
    def test_negative_rating_must_be_on_original_path(self):
        next_step = {
            "completions": [{"text": "original second step", "rating": -1}],
            "chosen_completion": None,
        }
        first_step = {
            "completions": [
                {"text": "original first step", "rating": 1},
                {"text": "alternate step", "rating": -1},
            ],
            "chosen_completion": 0,
        }
        original = ["original first step", "original second step"]
        self.assertTrue(original_step_marked_bad(original, [first_step, next_step]))
        self.assertFalse(original_step_marked_bad(original, [first_step]))
        self.assertFalse(original_step_marked_bad(
            original, [first_step | {"chosen_completion": 1}, next_step]
        ))

    def test_tie_distribution_has_known_exact_counts(self):
        # One guaranteed flag plus two slots from a tie with two flags and two clearances.
        queue = [(1, True), (2, True), (2, False), (2, True), (2, False), (3, True)]
        result = tie_summary(queue, lambda c: c[0], 3, lambda c: c[1])
        self.assertEqual(result["guaranteed_target_reviews_before_cutoff"], 1)
        self.assertEqual(result["slots_at_cutoff"], 2)
        self.assertEqual(result["expected_target_reviews"], 2)
        self.assertEqual(result["central_95_pct_target_review_count"], [1, 3])
        self.assertEqual(result["possible_target_review_count"], [1, 3])


if __name__ == "__main__":
    unittest.main()
