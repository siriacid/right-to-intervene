# Accuracy checks

The primary run used the rules set after the pilot. These checks were added after that run to find out whether the result depends on answer spelling, the archive's finish codes, or a lucky tie-break. They reuse the same evaluation problems and therefore offer sensitivity evidence rather than independent replication.

## Same 439 slots, different analysis choices

| Analysis | Flagged candidates surfaced by verifier vs. agreement | Flagged answer-key matches surfaced by verifier vs. agreement |
| --- | ---: | ---: |
| Primary replay | 403 vs. 381 of 1,643 | 30 vs. 9 of 80 |
| PRM800K string normalization for key matching and agreement | 403 vs. 382 of 1,643 | 35 vs. 9 of 96 |
| Include negative human ratings on the original solution path | 409 vs. 388 of 1,667 | 30 vs. 9 of 81 |
| Average over uniform agreement tie-breaks | 403 vs. 382.9 expected of 1,643 | 30 vs. 9.6 expected of 80 |

These checks change one type of analysis choice at a time. The fixed-seed primary result stays in the main report. The two denominators count all flagged candidates in the stated analysis, including those outside the review queue. [Label and tie outputs](../results/audit.json) · [Normalization output](../results/robustness.json)

## Can answer formatting account for the result?

The primary comparison collapses whitespace and compares the remaining answer strings exactly. The sensitivity check used PRM800K's published `math_normalize.py` on those strings. It first changed only the definition of an answer-key match, keeping both queues fixed. It then also used those normalized answer strings for the agreement queue, keeping the same budget and tie order. The process queue uses the same archived scores in both comparisons.

The normalizer added 78 answer-key matches, of which 16 were flagged and 62 cleared. The flagged share among resolved matches changed from 80 of 407 (19.7%) to 96 of 485 (19.8%). The normalized agreement queue retained 428 of its original 439 entries. With both changes in place, the overall recall advantage was **1.28 percentage points** (paired 95% interval 0.30 to 2.20). The answer-key-match recall advantage was **27.08 points** (16.00 to 38.46). Normalizing the key match alone gave the same counts of 35 and nine and a paired interval of 16.33 to 38.54 points.

This is a check of string normalization. In source line 501, it merges `2/3` with its LaTeX fraction. In line 571, it also drops text in `-1 \text{ or } 0`, which produces a match with `-1` even though the answers differ. The analysis uses the upstream string normalizer alone. Mathematical equivalence and unit correctness require separate judgment. [Pinned normalizer source](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/grading/math_normalize.py)

## Do step ratings agree with the finish codes?

The primary labels use the archive's finish codes. For this audit, we walked the stored original generation alongside the human annotation. At a step on the original path, we required the first completion's text to match the stored original step before crediting a rating of `-1`. If the annotation continued with a different step, we stopped following that path. This avoids counting negative ratings on suggested alternatives as errors in the original trace.

All 1,674 evaluation records marked `found_error` contained an aligned negative rating. So did 25 records marked `give_up` and one record marked `solution`. That last record, on source line 998, is an arithmetic example that ends at 13,485 for 31 choose 28. The correct value is 4,495, and the annotation marks a step in the original trace as negative. Applying the broader label rule changed 23 unresolved candidates and one cleared candidate to flagged. The queues stayed fixed. The overall lead changed from 22 to 21 flags, and the strict answer-key-match lead stayed at 21 flags. [Upstream annotation instructions](https://github.com/openai/prm800k/blob/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/instructions/instructions_phase_2.pdf) · [Label audit output](../results/audit.json)

We also calculated exact bounds for the original queue counts if every unresolved candidate were relabeled either flagged or cleared. A candidate appearing in both queues contributes equally under either label. With the original queues fixed, the verifier's lead ranges from 12 to 31 additional flags overall and from 20 to 22 additional flags among strict answer-key matches. These bounds vary the unresolved labels only. The step-rating check also allows a cleared label to change.

## Did a lucky tie-break make the agreement queue look worse?

At the 20% budget, 1,103 candidates tied for the lowest agreement score. Each had an answer that appeared once in a six-candidate pool. The agreement queue used the seeded order to allocate all 439 slots within this tied group. The process verifier had a unique candidate at the cutoff.

Under uniform selection without replacement from the 1,103 tied candidates, the agreement queue is expected to surface **382.9** flags overall and **9.6** flags with answers matching the key. Exact central 95% ranges are **372–393** and **5–14**, respectively. The actual seeded counts, 381 and nine, are near those expectations. This calculation varies the order within ties while holding the archive fixed. The main bootstrap instead varies the problems while holding the tie rule fixed. [Tie calculations](../results/audit.json)

The tied group contains just 24 flagged solutions whose answers match the key. Even a tie order that placed all 24 first would surface fewer than the verifier's 30. Across all flagged solutions, agreement could surface up to 439 if every selected candidate were flagged. The overall comparison is therefore more sensitive to tie order than the result for flagged matches. [Exact bounds](../results/audit.json)
