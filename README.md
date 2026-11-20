# Right to Intervene
## Prioritizing human review of LLM reasoning

**When human review is limited, which model-generated solutions should be checked first?**

Right to Intervene studies how to allocate human oversight to automated outputs. The current version, **V3**, compares review queues for archived language-model solutions to math problems. It asks whether a learned process-verifier score surfaces more human-flagged reasoning than agreement between final answers, under the same review budget.

A solution can reach the expected answer through a flawed derivation. V3 therefore measures both overall coverage of human flags and coverage of flagged solutions whose answer text matches the reference. The experiment reuses published outputs, verifier scores, and human annotations from PRM800K; it does not train a new model or run a live human-review intervention.

[Experiment and reproduction](experiments/alignment_v3/README.md) · [Mechanism](experiments/alignment_v3/docs/MECHANISM.md) · [Methods](experiments/alignment_v3/docs/METHODS.md) · [Results](experiments/alignment_v3/docs/RESULTS.md) · [Audit](experiments/alignment_v3/docs/AUDIT.md)

## Current findings

The evaluation partition contains **2,195 unique solutions to 370 problems**, held out from the V3 pilot. Archived annotations classify 1,643 as flagged, 481 as cleared, and 71 as unresolved. At a **20% review budget**, each policy receives **439 candidate slots**.

| Review queue | Human flags surfaced / 1,643 | Overall recall | Flagged answer-key matches surfaced / 80 | Match recall |
| --- | ---: | ---: | ---: | ---: |
| Seeded random | 335 | 20.39% | 20 | 25.00% |
| Final-answer agreement | 381 | 23.19% | 9 | 11.25% |
| Process verifier | 403 | 24.53% | 30 | 37.50% |

The verifier surfaced **22 additional flags overall**, a **1.34 percentage-point** recall gain over agreement (paired 95% bootstrap interval: **0.43–2.36 points**). Its point estimate did **not** reach the post-pilot practical target of at least two points, although the interval includes that target.

The secondary result was larger: among flagged solutions whose final answer text matched the key, the verifier surfaced **30 rather than 9**, a **26.25-point** recall gain (descriptive 95% interval: **13.89–39.19 points**). This subgroup accounts for 21 of the 22 net additional flags.

**Interpretation:** the queues differ substantially in which flawed explanations they surface, even when the difference in overall recall is small. This is evidence about review selection in one archive, not proof that a reviewer would detect or fix every selected issue.

See the [committed summary](experiments/alignment_v3/results/summary.csv), [run manifest](experiments/alignment_v3/results/manifest.json), and [full interpretation](experiments/alignment_v3/docs/RESULTS.md). The [audit](experiments/alignment_v3/docs/AUDIT.md) examines answer normalization, step ratings, unresolved labels, and tie-breaking.

## How V3 works

1. Verify the pinned PRM800K input hash and merge repeated annotations of the same solution.
2. Assign whole problems to a deterministic pilot or evaluation partition.
3. Rank the same candidate pool by seeded random order, low final-answer agreement, or low archived process-verifier score.
4. Select the same number of candidates from each queue at each budget.
5. Count archived human flags among selected candidates. Use answer keys only for evaluation, not queue selection.
6. Compare recall using 2,000 paired bootstrap resamples of whole problems.

A review budget counts candidate slots, not measured reviewer minutes, model-inference cost, or successful interventions. The [mechanism walkthrough](experiments/alignment_v3/docs/MECHANISM.md) includes a small worked example.

## Reproduce the current version

Use Python 3.12. The core V3 runner and its tests use the standard library.

~~~bash
git clone https://github.com/siriacid/right-to-intervene.git
cd right-to-intervene
python3.12 -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
cd experiments/alignment_v3
python -m unittest discover -s tests -v
~~~

For the full replay, install Git LFS and follow the [pinned dataset download instructions](experiments/alignment_v3/README.md#reproduce-the-study). Then, from the same directory:

~~~bash
python experiment.py --input results-local/phase2_test.jsonl \
  --split pilot --out results-local/pilot
python experiment.py --input results-local/phase2_test.jsonl \
  --split evaluation --out results-local/evaluation
~~~

Optional plots require Matplotlib. The [experiment README](experiments/alignment_v3/README.md) also gives audit and robustness commands. Use the ignored results-local directory to keep committed reference outputs intact.

## Scope and limitations

- The source study selected solutions for annotation using process-verifier scores. This is not an unbiased sample of all model outputs.
- Human flags can include mathematical errors, incomplete arguments, and other explanation problems. They are not a direct measurement of malicious behavior.
- Answer-key matching primarily uses whitespace-normalized strings. The audit tests another normalizer, but neither is a general proof of mathematical equivalence.
- The evaluation partition is held out from the V3 pilot. This does not establish independence from the upstream model or verifier development process.
- Reviews are replayed from annotations; detection, correction, release decisions, reviewer time, and downstream harm are not measured.
- The bootstrap intervals describe variation in problem composition in this archive. They do not establish generalization to other models or tasks.

## Documentation and experiment history

| Location | Purpose |
| --- | --- |
| [Research overview](docs/research-notes.md) | Current question, hypotheses, definitions, and evidence boundaries. |
| [Sources and data provenance](docs/source-notes.md) | Pinned inputs, annotation provenance, and the scope of related work. |
| [Next study](docs/NEXT_STUDY.md) | Proposed independent sampling and prospective reviewer evaluation. |
| [Experiment index](experiments/README.md) | What each version measures and how the versions relate. |
| [V3 LLM review](experiments/alignment_v3/README.md) | Current experiment, reproduction, methods, results, and audits. |
| [V2 production simulation](experiments/authority_v2/README.md) | Earlier study of delayed equipment-state reviews. |
| [v0.1 factory prototype](experiments/factory_v0_1/README.md) | Earlier permission-gating prototype and its limitations. |

V2 and v0.1 remain available for reproduction. They use different environments, outcomes, and information assumptions; their results should not be pooled with V3 or described as LLM-review results.

Research documentation was developed with AI assistance. Scientific interpretation and publication decisions remain the researcher's responsibility.
