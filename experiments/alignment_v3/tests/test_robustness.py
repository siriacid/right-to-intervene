from collections import Counter
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiment import Candidate
from robustness import compare, load_normalizer


class NormalizationSensitivityTests(unittest.TestCase):
    def test_normalized_key_can_add_flag_without_changing_queue(self):
        answers = ("0.5", "1/2", "1/3", "1/3", "1/3")
        candidates = [
            Candidate(
                str(index), "problem", answer, "1/2", scores={float(index)},
                reasons=Counter({"found_error" if index == 0 else "solution": 1}),
            )
            for index, answer in enumerate(answers)
        ]
        with patch("robustness.bootstrap", return_value={}):
            results = compare(candidates, lambda answer: answer.replace("0.5", "1/2"))
        original = results["evaluation"]["original"]
        key_only = results["evaluation"]["normalized_answer_key_match_only"]
        self.assertEqual(original["answer_key_match_outcomes"]["flagged"], 0)
        self.assertEqual(key_only["answer_key_match_outcomes"]["flagged"], 1)
        self.assertEqual(results["newly_matched_outcomes"], {"flagged": 1})
        for mode, expected_matches in ((original, 0), (key_only, 1)):
            result = next(row for row in mode["budget_sweep"]
                          if row["policy"] == "process_verifier" and row["budget_pct"] == 20)
            self.assertEqual(result["reviewed_flagged"], 1)
            self.assertEqual(result["reviewed_matching_flagged"], expected_matches)

    def test_rejects_unverified_normalizer_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "normalizer.py"
            path.write_text('raise AssertionError("Unexpected execution")\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                load_normalizer(path)
