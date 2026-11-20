# How the V3 test works

V3 asks a question about human oversight of language models. If a reviewer can inspect only a fraction of the generated solutions, which way of choosing those solutions brings more flawed reasoning to their attention? V3 gives three selection rules the same archive and the same number of review slots. It uses the archive's human judgments to count the errors each rule would put in front of a reviewer.

The test runs offline. It reuses generated solutions, human annotations, and verifier scores published with PRM800K. The Python runner builds and scores review queues. Its measured outcome is **whether a flagged solution enters the queue**. Actual review decisions, repairs, and release outcomes would require a prospective study. [Source archive and schema](https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163)

1. Verify the archive and merge duplicate annotations into unique candidates.
2. Split the candidates by problem and rank the evaluation candidates three ways.
3. Take the same number of candidates from each queue.
4. Use the archived human labels and answer key to count what each queue surfaced.

## 1. Turn the archive into a pool of solutions

Each annotation row refers to a math problem and one full model-generated solution. It contains the model's final answer, a reference answer, an archived verifier score, and a human annotation outcome. The runner verifies the source file's SHA-256 before reading it. Repeated annotations of the same problem text and full generated step sequence become one **candidate**. This keeps reviewers from spending multiple slots on identical text and prevents duplicated annotations from inflating final-answer agreement.

- A candidate is **flagged** when it has at least one `found_error` outcome and no `solution` outcome.
- A candidate is **cleared** when it has at least one `solution` outcome and no `found_error` outcome.
- A candidate is **unresolved** when it has both decisive outcomes or only inconclusive outcomes such as `give_up`.

Every candidate stays in the pool, including unresolved candidates. When selected, each uses one review slot. Human labels serve as the evaluation reference. A flag can reflect a mistake, an incomplete argument, or another quality issue. A clearance reflects the archived judgment. If one solution has several distinct archived verifier scores, the runner uses their mean.

The exact problem text determines the split. The runner hashes the problem with SHA-256 and interprets the hash as an integer. Problems with a hash divisible by five go into the pilot, and the other problems go into the evaluation. This keeps all candidates for a problem together and lets their agreement scores use the full archived pool for that problem. [Methods and label definitions](METHODS.md)

## 2. Build three queues for the same budget

| Queue | Signal | What moves a solution toward the front |
| --- | --- | --- |
| Random | A fixed pseudorandom order derived from the seed and candidate ID | An earlier position in that order. |
| Answer agreement | The fraction of unique candidates for that problem with the same final answer string after whitespace is collapsed | A rarer answer within the problem's pool. A candidate counts toward its own answer's frequency. |
| Process verifier | The candidate's archived score from a learned verifier of solution steps | A lower score. V3 uses its ordering as a signal of concern. |

The answer agreement rule moves an outlier forward even when the outlier has the correct answer. It measures how common the answer text is among the archived candidates. The verifier can distinguish different derivations that end with the same answer because the archived scores are specific to each candidate solution. Ties use the same seed-based order as the random queue. Human labels and the answer key enter when scoring the chosen candidates.

For each budget, the runner takes the first `floor(candidate count × budget fraction)` **from each queue across the entire evaluation set**. Every solution uses one slot. At the primary 20% budget, `floor(2,195 × 0.20)` gives 439 slots for each queue. This budget measures candidate slots. Estimating time or monetary cost would require measurements of reviewer time, model generation, and verifier inference. [Held-out summary](../results/summary.csv)

## 3. Score the selected solutions

| Measure | What goes in the numerator | What goes in the denominator |
| --- | --- | --- |
| Overall recall | Flagged candidates in the queue | All flagged candidates in the evaluation pool. |
| Answer-key-match recall | Flagged candidates in the queue whose answer text matches the key | All flagged candidates whose answer text matches the key. |
| Review precision | Flagged candidates in the queue | Flagged plus cleared candidates in the queue. |
| Unreviewed flagged rate | Flagged candidates outside the queue | Flagged plus cleared candidates outside the queue. |

The primary answer-key check collapses whitespace and compares the resulting text. Under this rule, `0.5` and `1/2` are different strings. A solution that matches the key can still have a human-flagged step. This is why the test reports answer-key-match recall in addition to overall recall. A ratio with a zero denominator is undefined. For example, review precision is undefined at a zero-slot budget, while recall is zero if the evaluation pool contains flagged candidates.

The runner calculates the verifier's recall minus answer agreement's recall in **percentage points** at a 20% budget. It uses a paired bootstrap to see how that gap varies with problem composition. Each of 2,000 draws samples whole problems with replacement and brings along all their candidates. Both queues use the same draw and the same recomputed number of slots. This preserves the within-problem answer pool and the fact that one problem can contribute several related errors. The reported interval spans the 2.5th through 97.5th percentiles of the gaps. Its scope is variation across the archive's problems under this procedure. [Analysis protocol](METHODS.md) · [Run manifest](../results/manifest.json)

## A worked example with five solutions

This invented example uses two problems. Problem A asks for the area of a rectangle with sides 2 and 3, whose answer key is `6`. Problem B asks how many objects are in three groups of three, whose answer key is `9`.

| Candidate | Reasoning | Final answer | Agreement | Verifier score | Human outcome |
| --- | --- | ---: | ---: | ---: | --- |
| A1 | Adds the sides and then adds one. | `6` | 2/3 | 0.10 | Flagged. The answer matches the key and the reasoning is faulty. |
| A2 | Multiplies the side lengths. | `6` | 2/3 | 0.90 | Cleared. |
| A3 | Adds the side lengths. | `5` | 1/3 | 0.35 | Flagged. |
| B1 | Counts three equal groups of three. | `9` | 2/2 | 0.20 | Unresolved. In this example the reviewer stopped without a decision. |
| B2 | Adds three, three, and three. | `9` | 2/2 | 0.80 | Cleared. |

One fixed tie order for this example is `A1 → A2 → B2 → A3 → B1`. The random queue takes that order. Agreement moves `A3` ahead of the two candidates with answer `6`, then puts the two candidates from the unanimous problem B last. The process queue sorts by ascending verifier score.

| Queue | Order | Selected at 20% | Overall recall | Answer-key-match recall |
| --- | --- | --- | ---: | ---: |
| Random | A1, A2, B2, A3, B1 | A1 | 1/2 | 1/1 |
| Answer agreement | A3, A1, A2, B2, B1 | A3 | 1/2 | 0/1 |
| Process verifier | A1, B1, A3, B2, A2 | A1 | 1/2 | 1/1 |

At 20%, every queue gets one slot and all three have 50% overall recall. Agreement finds the wrong final answer. The verifier and random queue each find the bad derivation that ends in the expected answer. At 40%, the queues each get two slots. Agreement selects both flagged candidates, while the verifier selects A1 and the unresolved B1. B1 still costs one slot. The verifier surfaces one flag in two allocated slots and has 100% precision among its one resolved review. This illustrates how queue coverage and review precision answer different questions.

## Trace an actual candidate through the runner

Open the [candidate table](../results/candidates.csv) or regenerate it using the [reproduction instructions](../README.md#reproduce-the-study). Each row has the source line numbers, all archived annotation outcomes for that candidate, its answer-key-match flag, and its rank in each queue. For the primary budget, a rank of 439 or lower puts the candidate inside that queue. Filter a queue by this cutoff and count the rows marked `flagged` to reproduce its numerator. Within those rows, count `answer_key_match = True` to reproduce the answer-key-match numerator. The same counts are in the [summary table](../results/summary.csv). The [results](RESULTS.md) walk through a source example and explain how the measured effects depend on the budget and dataset.

The [accuracy checks](AUDIT.md) rerun the comparison with a different definition of matching answers and with negative ratings from the original solution path. They also calculate what happens when the tie order or unresolved labels vary.
