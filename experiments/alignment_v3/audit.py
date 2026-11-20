"""Check sensitivity to archive label rules and the 20% queue cutoff."""
import argparse
from collections import Counter
import hashlib
import json
from math import comb
from pathlib import Path

from experiment import (
    PRIMARY_BUDGET, SOURCE_SHA256, load_candidates, pilot_problem,
    rank_candidates, summarize,
)


def original_step_marked_bad(steps, annotations):
    for original, annotation in zip(steps, annotations):
        options = annotation["completions"]
        if not options:
            break
        # Phase 2 shows the original model step as the first completion.
        if options[0]["text"] == original and options[0]["rating"] == -1:
            return True
        chosen = annotation["chosen_completion"]
        followed_step = annotation["human_completion"] if chosen is None else options[chosen]["text"]
        if followed_step != original:
            break
    return False


def audit_labels(candidates, source_lines):
    counts = Counter()
    reassigned = Counter()
    examples = []
    for candidate in candidates:
        has_bad_step = False
        for line_number in candidate.source_lines:
            row = json.loads(source_lines[line_number - 1])
            annotation = row["label"]
            bad_step = original_step_marked_bad(
                row["question"]["pre_generated_steps"], annotation["steps"]
            )
            if bad_step:
                counts[annotation["finish_reason"]] += 1
                has_bad_step = True
                if annotation["finish_reason"] == "solution":
                    examples.append(line_number)
        if has_bad_step and candidate.outcome != "flagged":
            reassigned[candidate.outcome] += 1
            candidate.reasons = Counter({"found_error": 1})
    return {
        "annotations_with_bad_original_step_by_finish_reason": dict(counts),
        "reclassified_candidates_by_original_outcome": dict(reassigned),
        "solution_annotations_with_bad_original_step_source_lines": examples,
    }


def tie_summary(queue, key, limit, target):
    threshold = key(queue[limit - 1])
    before_cutoff = [c for c in queue if key(c) < threshold]
    fixed = sum(map(target, before_cutoff))
    tied = [c for c in queue if key(c) == threshold]
    slots = limit - len(before_cutoff)
    hits = sum(map(target, tied))
    total = len(tied)
    min_hits = max(0, slots - (total - hits))
    max_hits = min(slots, hits)
    ways = comb(total, slots)
    cumulative = 0
    low = high = None
    for selected in range(min_hits, max_hits + 1):
        cumulative += comb(hits, selected) * comb(total - hits, slots - selected)
        if low is None and cumulative * 40 >= ways:
            low = fixed + selected
        if high is None and cumulative * 40 >= ways * 39:
            high = fixed + selected
    return {
        "cutoff_score": threshold,
        "slots_at_cutoff": slots,
        "candidates_tied_at_cutoff": total,
        "target_candidates_tied_at_cutoff": hits,
        "guaranteed_target_reviews_before_cutoff": fixed,
        "expected_target_reviews": fixed + slots * hits / total,
        "central_95_pct_target_review_count": [low, high],
        "possible_target_review_count": [fixed + min_hits, fixed + max_hits],
    }


def audit(candidates, source_lines):
    rankings = rank_candidates(candidates)
    limit = len(candidates) * PRIMARY_BUDGET // 100
    agreement = rankings["answer_agreement"][:limit]
    process = rankings["process_verifier"][:limit]
    agreement_ids = {c.id for c in agreement}
    process_ids = {c.id for c in process}
    original_rows = {
        row["policy"]: row for row in summarize(candidates, rankings)
        if row["budget_pct"] == PRIMARY_BUDGET
    }
    tie_results = {}
    unknown_label_bounds = {}
    for outcome, select, field in (
        ("all_flagged", lambda c: True, "reviewed_flagged"),
        ("answer_key_matched_flagged", lambda c: c.answer_match, "reviewed_matching_flagged"),
    ):
        tie_results[outcome] = {
            policy: tie_summary(
                rankings[policy], key, limit, lambda c: select(c) and c.outcome == "flagged",
            )
            for policy, key in (
                ("answer_agreement", lambda c: c.agreement),
                ("process_verifier", lambda c: c.score),
            )
        }
        unknown_agreement_only = sum(
            c.outcome == "unresolved" and select(c) and c.id not in process_ids for c in agreement
        )
        unknown_process_only = sum(
            c.outcome == "unresolved" and select(c) and c.id not in agreement_ids for c in process
        )
        observed_gain = original_rows["process_verifier"][field] - original_rows["answer_agreement"][field]
        unknown_label_bounds[outcome] = [
            observed_gain - unknown_agreement_only, observed_gain + unknown_process_only
        ]

    label_counts = audit_labels(candidates, source_lines)
    rescored = {
        row["policy"]: {
            field: row[field] for field in (
                "flagged_total", "reviewed_flagged", "recall_pct", "matching_flagged_total",
                "reviewed_matching_flagged", "matching_recall_pct",
            )
        }
        for row in summarize(candidates, rankings) if row["budget_pct"] == PRIMARY_BUDGET
    }
    return {
        "source_sha256": SOURCE_SHA256,
        "budget_pct": PRIMARY_BUDGET,
        "review_slots": limit,
        "uniform_tie_break_sensitivity": tie_results,
        "possible_process_minus_agreement_flagged_counts_after_resolving_unknowns": unknown_label_bounds,
        "alternate_step_rating_labels": label_counts | {"policies": rescored},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = args.input.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("Input does not match the pinned Phase 2 test archive")
    cases = [c for c in load_candidates(data) if not pilot_problem(c.problem_id)]
    report = audit(cases, data.splitlines())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
