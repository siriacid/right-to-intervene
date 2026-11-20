from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest

from experiment import Candidate, load_candidates, pilot_problem, rank_candidates, reviewed_counts, run, summarize


def candidate(name, answer, score, reason):
    return Candidate(name, name[0], answer, "A", {score}, reasons=Counter({reason: 1}))


class AuditTests(unittest.TestCase):
    def test_annotation_duplicates_and_conflicts(self):
        question = {
            "problem": "Which letter is A?",
            "pre_generated_steps": ["Pick A."],
            "pre_generated_answer": " A ",
            "ground_truth_answer": "A",
            "pre_generated_verifier_score": 0.25,
        }
        raw = [
            {"question": question | {"pre_generated_verifier_score": score},
             "label": {"finish_reason": reason}}
            for score, reason in ((0.25, "found_error"), (0.25, "found_error"), (0.75, "solution"))
        ]
        [case] = load_candidates("\n".join(map(json.dumps, raw)).encode())
        self.assertEqual(case.source_lines, [1, 2, 3])
        self.assertEqual(case.outcome, "unresolved")
        self.assertEqual(case.score, 0.5)
        self.assertTrue(case.answer_match)

    def test_review_ranking_and_accounting(self):
        cases = [
            candidate("a1", "A", .01, "found_error"),
            candidate("a2", "A", .9, "solution"),
            candidate("a3", "B", .8, "solution"),
            candidate("b1", "A", .7, "give_up"),
            candidate("b2", "A", .6, "solution"),
        ]
        rankings = rank_candidates(cases)
        self.assertEqual(rankings["answer_agreement"][0].id, "a3")
        self.assertEqual(rankings["process_verifier"][0].id, "a1")
        comparison = {
            row["policy"]: row for row in summarize(cases, rankings) if row["budget_pct"] == 20
        }
        self.assertEqual(comparison["process_verifier"]["matching_recall_pct"], 100)
        self.assertEqual(comparison["process_verifier"]["unreviewed_flagged"], 0)
        self.assertEqual(comparison["answer_agreement"]["matching_recall_pct"], 0)
        self.assertEqual(comparison["answer_agreement"]["unreviewed_flagged"], 1)

    def test_bootstrap_weights_keep_clusters_and_respect_budget(self):
        queue = [
            candidate("a1", "A", .1, "found_error"),
            candidate("a2", "B", .2, "give_up"),
            candidate("b1", "A", .3, "solution"),
        ]
        self.assertEqual(reviewed_counts(queue, 3, Counter(a=2)), {
            "flagged": 2, "matching_flagged": 2, "unresolved": 1,
        })
        self.assertEqual(reviewed_counts(queue, 1, Counter(b=1))["cleared"], 1)

    def test_pilot_assignment_and_unverified_input(self):
        self.assertTrue(pilot_problem("a"))
        self.assertFalse(pilot_problem("b"))
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / "fake.jsonl"
            raw.write_bytes(b"{}\n")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                run(raw, Path(directory) / "out", "pilot", False)
            self.assertFalse((Path(directory) / "out").exists())


if __name__ == "__main__":
    unittest.main()
