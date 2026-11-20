# Sources and data provenance — Right to Intervene V3

V3 is an offline replay on published language-model solutions and human annotations. This page identifies the inputs used by the implementation and separates them from background literature. It is not an exhaustive literature review.

[Project overview](../README.md) · [V3 methods](../experiments/alignment_v3/docs/METHODS.md) · [Accuracy checks](../experiments/alignment_v3/docs/AUDIT.md)

## Primary archive

- **Repository:** [OpenAI PRM800K](https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163).
- **Pinned revision:** 7ecc794703b2877f63226f2477a49b34f9b25163.
- **Input path:** prm800k/data/phase2_test.jsonl.
- **Input SHA-256:** 6b172efa884ac8341a946dd82e06947c135b7254109fb3f7aa907c715d98aaad.
- **Used fields:** problem text, original generated steps, generated final answer, reference answer, archived verifier score, and annotation finish reason.
- **Attribution and license:** consult the [pinned source repository](https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163) before redistributing its data.

The runner verifies the input hash. Git LFS is required to retrieve the data bytes rather than the small pointer file. Reproduction commands are in the [V3 README](../experiments/alignment_v3/README.md).

The upstream archive was selected for annotation using process-verifier scores. It is not a neutral sample of all generated answers. The V3 pilot/evaluation split is a new problem-level partition within that archive, not a claim about the upstream model's training data.

## Annotation and matching definitions

| Source | Use in V3 | Important boundary |
| --- | --- | --- |
| [PRM800K schema](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/README.md) | Interpret records, generated solutions, and stored verifier scores. | The project reuses an existing verifier; it does not train one. |
| [Phase 2 annotation instructions](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/instructions/instructions_phase_2.pdf) | Interpret archived human flags and the audit's step-rating checks. | A flag can concern an incomplete or unclear explanation as well as an incorrect calculation. |
| [Published test split](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/math_splits/test.jsonl) | Locate the upstream problem split associated with the archive. | V3 evaluates the available annotated subset. |
| [Pinned answer normalizer](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/grading/math_normalize.py) | Sensitivity analysis for key matching and answer agreement. | String normalization does not establish mathematical equivalence; the audit documents a misleading match. |

Primary matching only collapses whitespace. The normalizer is used in a separate robustness analysis, and its source hash is checked before it is loaded.

## Project evidence

| File | Role |
| --- | --- |
| [Methods](../experiments/alignment_v3/docs/METHODS.md) | Split, deduplication, policies, label rules, budgets, and statistical analysis. |
| [Summary CSV](../experiments/alignment_v3/results/summary.csv) | Counts and metrics for every policy and budget. |
| [Manifest](../experiments/alignment_v3/results/manifest.json) | Input and runner hashes, sample counts, seeds, and paired intervals. |
| [Audit output](../experiments/alignment_v3/results/audit.json) | Label checks, unresolved-label bounds, and tie-break analysis. |
| [Robustness output](../experiments/alignment_v3/results/robustness.json) | Alternate normalization and step-label analyses. |

Documentation edits do not constitute a new experiment or an independent replication. The input and runner hashes retain the provenance of the committed results.

## Background and future literature work

The earlier production-study bibliography is retained in [V2 related work](../experiments/authority_v2/docs/RELATED_WORK.md). It concerns control and delayed intervention; it is not the main evidence base for V3.

Before claiming a new review-selection method, compare this project with prior process-supervision, answer-agreement, selective-prediction, and learning-to-defer work. Distinguish selecting outputs for inspection from improving model training, choosing a final answer, or demonstrating effective human correction.

The current study supports an empirical comparison within the pinned archive. It does not establish a first-of-its-kind algorithm or a solution to general AI alignment.
