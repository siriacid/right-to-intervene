# V3 methods — budgeted review of LLM reasoning

[V3 overview](../README.md) · [Mechanism](MECHANISM.md) · [Methods](METHODS.md) · [Results](RESULTS.md) · [Audit](AUDIT.md) · [Next study](../../../docs/NEXT_STUDY.md)


**Study type:** offline replay of archived outputs and labels. V3 evaluates review selection; it does not measure live correction, release outcomes, or a newly trained verifier.

## Question and hypothesis

With a fixed human-review budget, does using a score for the whole solution surface more human-flagged LLM outputs than comparing final answers? A solution can end with the expected answer and still give a faulty or incomplete explanation. We replayed three review queues on published model outputs and human labels to measure which issues each queue would bring to a reviewer. [Walkthrough with a worked example](MECHANISM.md)

## Data and split

We used the PRM800K Phase 2 test annotations at revision `7ecc794703b2877f63226f2477a49b34f9b25163`. The archive contains generated GPT-4-family solutions to MATH problems, process-verifier scores, reference answers, and human annotation outcomes. All 2,762 archive rows have generation number 6. The 458 archive problems are a subset of the 500 problems in PRM800K's published MATH test split. Upstream used its best available verifier to select solutions for annotation during Phase 2. The archive represents selected solutions from that research process. [PRM800K schema and sampling context](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/README.md) · [Upstream test split](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/math_splits/test.jsonl)

We assigned problems to the pilot if the integer value of the SHA-256 hash of their UTF-8 problem text was divisible by five. The remaining problems formed the evaluation partition held out from the V3 pilot. Problem-level assignment keeps related solutions and answer pools together. We included the entire evaluation partition, so sample size follows data availability.

Each pair of problem text and complete generated step sequence defines one candidate. We merged repeat annotations of the same candidate. A candidate is **flagged** if its decisive finish codes agree on `found_error`, **cleared** if they agree on `solution`, and **unresolved** otherwise. Other outcomes such as `give_up` are nondecisive. Unresolved candidates can use review slots and are excluded from error-rate denominators. The upstream instructions allow negative ratings for mathematical errors, incomplete proofs, and other issues such as unclear or off-topic reasoning. The measured endpoint is the archived human flag. Each candidate retains its source line numbers for inspection. [Upstream annotation instructions](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/instructions/instructions_phase_2.pdf)

The archive schema check found repeat annotations with different verifier scores for two pilot candidates. Before running the evaluation we specified using the mean of their distinct scores. No evaluation candidate had multiple distinct scores.

## Review policies

Each policy ranks the same pool and can queue at most `floor(candidate count × budget)` candidates. Ranking uses candidate identifiers, final-answer agreement, or archived verifier scores. The answer key and human outcomes are used for evaluation.

| Policy | Review priority |
| --- | --- |
| Random | Fixed pseudorandom order from a seed and candidate ID. |
| Answer agreement | Lowest share of same-problem candidates with the same final answer string first. |
| Process verifier | Lowest supplied verifier score first. |

Agreement uses all unique candidates in the same problem pool, including the candidate itself. It uses exact string equality after collapsing whitespace. All score ties use the same seeded ordering as the random queue. The agreement policy uses archived samples. Its sampling cost is outside the measured review budget. The process policy uses the archived model score and is a learned comparator.

## Outcomes and analysis

- **Primary outcome** is error recall at a 20% review budget. It is the fraction of all human-flagged candidates selected. The planned effect is the process verifier minus answer agreement in percentage points. For a practically meaningful advantage, we specified a point estimate of at least 2 percentage points and a paired 95% interval above zero.
- **Answer-key matches** are candidates whose final answer string matches the reference after collapsing whitespace. Report their flagged rate among resolved cases and the fraction of their flagged errors surfaced at the same global budget. This equality rule can miss equivalent mathematical expressions. It is used only in evaluation.
- **Review precision** is the fraction flagged among resolved reviewed candidates. Also report unresolved cases and unreviewed flagged candidates per 100 resolved candidates left unreviewed. The latter describes the replay queue and does not assume a real reviewer would catch every error.
- **Sensitivity** compares 5%, 10%, 20%, and 40% review budgets. Use zero review as a workload reference. Describe flagged rates for unanimous and nonunanimous candidate pools and how much the two 20% queues overlap.

We recomputed both 20% queues and their shared budget on 2,000 paired bootstrap draws of whole problems with replacement, using seed `314159`. Each draw repeats all candidates in its sampled problems and preserves the agreement scores within each problem. The 95% percentile intervals use the 2.5th and 97.5th percentiles of the resulting recall differences. They describe variation in problem composition under the fixed ranking and tie rules. Other than the primary comparison, we treat analyses as descriptive. The pilot and synthetic tests checked input accounting, policy ordering, and the recall calculations.

The pilot had 394 flagged candidates and 104 review slots. Answer agreement found 90 flagged candidates, so even a perfect queue could improve on it by only 3.6 percentage points of recall. Before running the evaluation, we changed the original 10-point target to 2 points, equivalent to about eight extra flags per 104 reviews at the pilot's prevalence. This criterion targets a meaningful change in queue yield within the observed recall ceiling.

The post-evaluation audit checks sensitivity to answer normalization, label coding, unresolved outcomes, and the tie-break at the review cutoff. [Audit methods and results](AUDIT.md)
