"""Check how PRM800K string normalization changes the V3 result."""
import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path

from experiment import (
    BOOTSTRAPS,
    PRIMARY_BUDGET,
    SEED,
    SOURCE_REVISION,
    SOURCE_SHA256,
    bootstrap,
    load_candidates,
    pilot_problem,
    rank_candidates,
    summarize,
)

NORMALIZER_SHA256 = "13998bf8c35bdc8a76868c84e1704a78567e2552557fda69027cc186568d3a4d"


def load_normalizer(path):
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != NORMALIZER_SHA256:
        raise ValueError("Normalizer does not match the pinned PRM800K math_normalize.py SHA-256")
    # Execute exactly the verified source bytes. This module only normalizes strings.
    scope = {}
    exec(compile(source, str(path), "exec"), scope)
    return scope["normalize_answer"]


def answer_counts(candidates):
    counts = Counter(c.outcome for c in candidates if c.answer_match)
    return {label: counts[label] for label in ("flagged", "cleared", "unresolved")}


def compare(candidates, normalize):
    original_queues = rank_candidates(candidates)
    normalized = [replace(c, answer=normalize(c.answer), reference=normalize(c.reference)) for c in candidates]
    by_id = {c.id: c for c in normalized}
    same_queues = {
        policy: [by_id[c.id] for c in queue] for policy, queue in original_queues.items()
    }
    normalized_queues = rank_candidates(normalized)
    limit = len(candidates) * PRIMARY_BUDGET // 100

    modes = (
        ("original", candidates, original_queues),
        ("normalized_answer_key_match_only", normalized, same_queues),
        ("normalized_answer_key_match_and_agreement", normalized, normalized_queues),
    )
    evaluation = {}
    for mode, cases, queues in modes:
        outcomes = answer_counts(cases)
        evaluation[mode] = {
            "answer_key_match_outcomes": outcomes,
            "budget_sweep": [
                {key: row[key] for key in (
                    "policy", "budget_pct", "reviewed", "reviewed_flagged", "recall_pct",
                    "reviewed_matching_flagged", "matching_recall_pct",
                )}
                for row in summarize(cases, queues)
            ],
            "paired_bootstrap": bootstrap(cases, queues),
        }

    agreement_original = {c.id for c in original_queues["answer_agreement"][:limit]}
    agreement_normalized = {c.id for c in normalized_queues["answer_agreement"][:limit]}
    return {
        "source_revision": SOURCE_REVISION,
        "source_sha256": SOURCE_SHA256,
        "normalizer_sha256": NORMALIZER_SHA256,
        "split": "evaluation",
        "candidate_count": len(candidates),
        "primary_budget_pct": PRIMARY_BUDGET,
        "tie_and_bootstrap_seed": SEED,
        "bootstrap_draws": BOOTSTRAPS,
        "agreement_queue_overlap_at_primary_budget": len(agreement_original & agreement_normalized),
        "newly_matched_outcomes": dict(Counter(
            c.outcome for c in candidates if not c.answer_match and by_id[c.id].answer_match
        )),
        "evaluation": evaluation,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Pinned phase2_test.jsonl")
    parser.add_argument("--normalizer", type=Path, required=True, help="Pinned PRM800K math_normalize.py")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON file")
    args = parser.parse_args()
    data = args.input.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("Input does not match the pinned PRM800K Phase 2 test SHA-256")
    normalize = load_normalizer(args.normalizer)
    candidates = [c for c in load_candidates(data) if not pilot_problem(c.problem_id)]
    result = compare(candidates, normalize)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
