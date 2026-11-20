"""Replay fixed-budget human review on archived GPT-4-family solutions."""
import argparse
from collections import Counter
import csv
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import platform
import random

SOURCE_REVISION = "7ecc794703b2877f63226f2477a49b34f9b25163"
SOURCE_SHA256 = "6b172efa884ac8341a946dd82e06947c135b7254109fb3f7aa907c715d98aaad"
BUDGETS = (0, 5, 10, 20, 40)
PRIMARY_BUDGET = 20
SEED = 314159
BOOTSTRAPS = 2000


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pilot_problem(problem_id):
    return int(problem_id, 16) % 5 == 0


@dataclass
class Candidate:
    id: str
    problem_id: str
    answer: str
    reference: str
    scores: set[float] = field(default_factory=set)
    source_lines: list[int] = field(default_factory=list)
    reasons: Counter = field(default_factory=Counter)
    agreement: float = 0.0
    pool_size: int = 0

    @property
    def score(self):
        return math.fsum(self.scores) / len(self.scores)

    @property
    def outcome(self):
        error = self.reasons["found_error"] > 0
        clear = self.reasons["solution"] > 0
        if error == clear:
            return "unresolved"
        return "flagged" if error else "cleared"

    @property
    def answer_match(self):
        return self.answer == self.reference


def load_candidates(data):
    candidates = {}
    for line_number, line in enumerate(data.splitlines(), start=1):
        row = json.loads(line)
        question = row["question"]
        problem = question["problem"]
        candidate_id = digest(json.dumps([problem, question["pre_generated_steps"]]))
        answer = " ".join(question["pre_generated_answer"].split())
        reference = " ".join(question["ground_truth_answer"].split())
        score = question["pre_generated_verifier_score"]
        if not math.isfinite(score):
            raise ValueError(f"Invalid verifier score on source line {line_number}")
        if candidate_id not in candidates:
            candidates[candidate_id] = Candidate(candidate_id, digest(problem), answer, reference)
        candidate = candidates[candidate_id]
        if (answer, reference) != (candidate.answer, candidate.reference):
            raise ValueError(f"Inconsistent answer on repeat annotation at source line {line_number}")
        candidate.scores.add(score)
        candidate.source_lines.append(line_number)
        candidate.reasons[row["label"]["finish_reason"]] += 1
    return list(candidates.values())


def rank_candidates(candidates):
    pool_sizes = Counter(c.problem_id for c in candidates)
    answers = Counter((c.problem_id, c.answer) for c in candidates)
    for candidate in candidates:
        candidate.pool_size = pool_sizes[candidate.problem_id]
        candidate.agreement = answers[candidate.problem_id, candidate.answer] / candidate.pool_size

    shuffled = sorted(candidates, key=lambda c: (digest(f"{SEED}:{c.id}"), c.id))
    return {
        "random": shuffled,
        "answer_agreement": sorted(shuffled, key=lambda c: c.agreement),
        "process_verifier": sorted(shuffled, key=lambda c: c.score),
    }


def reviewed_counts(queue, limit, weights=None):
    reviewed = Counter()
    for candidate in queue:
        if limit == 0:
            break
        copies = 1 if weights is None else weights[candidate.problem_id]
        take = min(limit, copies)
        reviewed[candidate.outcome] += take
        if candidate.answer_match and candidate.outcome == "flagged":
            reviewed["matching_flagged"] += take
        limit -= take
    return reviewed


def percent(count, total):
    return 100 * count / total if total else None


def summarize(candidates, rankings):
    flagged = sum(c.outcome == "flagged" for c in candidates)
    matching_flagged = sum(c.answer_match and c.outcome == "flagged" for c in candidates)
    resolved = sum(c.outcome != "unresolved" for c in candidates)
    for budget in BUDGETS:
        limit = len(candidates) * budget // 100
        for policy, queue in rankings.items():
            reviewed = reviewed_counts(queue, limit)
            reviewed_resolved = reviewed["flagged"] + reviewed["cleared"]
            missed = flagged - reviewed["flagged"]
            yield {
                "policy": policy, "budget_pct": budget, "candidates": len(candidates),
                "reviewed": limit, "reviewed_unresolved": reviewed["unresolved"],
                "flagged_total": flagged, "reviewed_flagged": reviewed["flagged"],
                "recall_pct": percent(reviewed["flagged"], flagged),
                "precision_pct": percent(reviewed["flagged"], reviewed_resolved),
                "matching_flagged_total": matching_flagged,
                "reviewed_matching_flagged": reviewed["matching_flagged"],
                "matching_recall_pct": percent(reviewed["matching_flagged"], matching_flagged),
                "unreviewed_resolved": resolved - reviewed_resolved,
                "unreviewed_flagged": missed,
                "unreviewed_flagged_pct": percent(missed, resolved - reviewed_resolved),
            }


def quantile(sorted_values, probability):
    index = probability * (len(sorted_values) - 1)
    left = int(index)
    right = math.ceil(index)
    return sorted_values[left] + (index - left) * (sorted_values[right] - sorted_values[left])


def bootstrap(candidates, rankings):
    sizes = Counter(c.problem_id for c in candidates)
    flagged = Counter(c.problem_id for c in candidates if c.outcome == "flagged")
    matching = Counter(c.problem_id for c in candidates if c.answer_match and c.outcome == "flagged")
    problems = sorted(sizes)
    rng = random.Random(SEED)
    differences = {"recall": [], "matching_recall": []}
    for _ in range(BOOTSTRAPS):
        weights = Counter(rng.choices(problems, k=len(problems)))
        limit = sum(sizes[p] * n for p, n in weights.items()) * PRIMARY_BUDGET // 100
        agreement = reviewed_counts(rankings["answer_agreement"], limit, weights)
        process = reviewed_counts(rankings["process_verifier"], limit, weights)
        for name, counts, key in (
            ("recall", flagged, "flagged"), ("matching_recall", matching, "matching_flagged")
        ):
            total = sum(counts[p] * n for p, n in weights.items())
            if total:
                differences[name].append(percent(process[key] - agreement[key], total))
    intervals = {}
    for name, values in differences.items():
        values.sort()
        intervals[name] = {"low_pp": quantile(values, 0.025) if values else None,
                           "high_pp": quantile(values, 0.975) if values else None,
                           "valid_draws": len(values)}
    return intervals


def describe(candidates, rankings, input_rows, split):
    limit = len(candidates) * PRIMARY_BUDGET // 100
    agreement_ids = {c.id for c in rankings["answer_agreement"][:limit]}
    process_ids = {c.id for c in rankings["process_verifier"][:limit]}
    strata = Counter(
        ("answer_match" if c.answer_match else "answer_mismatch",
         "unanimous" if c.agreement == 1 else "nonunanimous", c.outcome)
        for c in candidates
    )
    return {
        "source_revision": SOURCE_REVISION,
        "source_sha256": SOURCE_SHA256,
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python_version": platform.python_version(),
        "split": split,
        "seed": SEED,
        "bootstraps": BOOTSTRAPS if split == "evaluation" else 0,
        "primary_budget_pct": PRIMARY_BUDGET,
        "budgets_pct": BUDGETS,
        "archive_annotation_rows": input_rows,
        "partition_annotation_rows": sum(len(c.source_lines) for c in candidates),
        "unique_candidates": len(candidates),
        "unique_problems": len({c.problem_id for c in candidates}),
        "human_outcomes": dict(Counter(c.outcome for c in candidates)),
        "annotation_finish_reasons": dict(sum((c.reasons for c in candidates), Counter())),
        "candidates_with_conflicting_decisive_annotations": sum(
            c.reasons["found_error"] > 0 and c.reasons["solution"] > 0 for c in candidates
        ),
        "candidates_with_multiple_process_scores": sum(len(c.scores) > 1 for c in candidates),
        "candidate_pool_size_by_problem": dict(Counter(
            Counter(c.problem_id for c in candidates).values()
        )),
        "primary_queue_overlap": len(agreement_ids & process_ids),
        "strata": [
            {"answer_key": answer_key, "pool": pool, "outcome": outcome, "candidates": count}
            for (answer_key, pool, outcome), count in sorted(strata.items())
        ],
    }


def write_csv(path, rows):
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def candidate_rows(candidates, rankings, split):
    rank_by_policy = {
        policy: {c.id: i for i, c in enumerate(queue, start=1)} for policy, queue in rankings.items()
    }
    for c in candidates:
        yield {
            "split": split, "problem_id": c.problem_id, "candidate_id": c.id,
            "source_lines": " ".join(map(str, c.source_lines)),
            "human_annotation_outcomes": json.dumps(c.reasons, sort_keys=True),
            "outcome": c.outcome, "answer_key_match": c.answer_match,
            "pool_size": c.pool_size, "agreement": c.agreement, "process_score": c.score,
            "archived_process_scores": json.dumps(sorted(c.scores)),
            **{f"{policy}_rank": ranks[c.id] for policy, ranks in rank_by_policy.items()},
        }


def plot(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    styles = {
        "random": ("Random", "#555555", "s", ":"),
        "answer_agreement": ("Answer agreement", "#B23C18", "o", "--"),
        "process_verifier": ("Process verifier", "#075A9C", "D", "-"),
    }
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.7), sharey=True, layout="constrained")
    for axis, title, metric in (
        (axes[0], "All flagged candidates", "recall_pct"),
        (axes[1], "Flagged candidates matching the answer key", "matching_recall_pct"),
    ):
        for policy, (label, color, marker, linestyle) in styles.items():
            points = [(r["budget_pct"], r[metric]) for r in rows if r["policy"] == policy]
            x, y = zip(*points)
            axis.plot(x, y, label=label, color=color, marker=marker, linestyle=linestyle)
        axis.set(title=title, xlabel="Candidates queued for review (%)", xticks=BUDGETS, ylim=(0, 100))
        axis.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Flagged candidates surfaced (%)")
    axes[0].legend(loc="upper left", frameon=False)
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return matplotlib.__version__


def run(input_path, out, split, chart):
    data = input_path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError("Input does not match the pinned PRM800K Phase 2 test SHA-256")
    candidates = [
        c for c in load_candidates(data)
        if pilot_problem(c.problem_id) == (split == "pilot")
    ]
    rankings = rank_candidates(candidates)
    rows = list(summarize(candidates, rankings))
    manifest = describe(candidates, rankings, len(data.splitlines()), split)
    if split == "evaluation":
        manifest["paired_bootstrap"] = bootstrap(candidates, rankings)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "summary.csv", rows)
    write_csv(out / "candidates.csv", candidate_rows(candidates, rankings, split))
    if chart:
        manifest["matplotlib_version"] = plot(rows, out / "review_recall.png")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{split}: {len(candidates)} candidates across {manifest['unique_problems']} problems")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Pinned phase2_test.jsonl")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--split", choices=("pilot", "evaluation"), required=True)
    parser.add_argument("--plot", action="store_true", help="Generate a PNG using Matplotlib")
    args = parser.parse_args()
    run(args.input, args.out, args.split, args.plot)
