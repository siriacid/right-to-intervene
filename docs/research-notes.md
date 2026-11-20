# Research overview — Right to Intervene V3

**Current study:** prioritizing human review of language-model reasoning under a fixed review budget.

[Project introduction](../README.md) · [Experiment](../experiments/alignment_v3/README.md) · [Methods](../experiments/alignment_v3/docs/METHODS.md) · [Results](../experiments/alignment_v3/docs/RESULTS.md)

## Research problem

A language model can produce an answer that matches a reference while its explanation contains an error or an incomplete argument. When a reviewer cannot inspect every output, the selection rule determines which issues receive attention. Final-answer agreement and reasoning-verifier scores offer different signals for that decision.

V3 compares those signals on the same archived candidate solutions with the same review-slot budget. It measures whether human-flagged solutions enter the review queue. It does not measure whether real reviewers subsequently identify, repair, or block them.

## Question and hypotheses

**Primary question:** does prioritizing low process-verifier scores surface more human-flagged solutions than prioritizing low final-answer agreement at a 20% review budget?

The post-pilot practical criterion was a point estimate of at least a two-percentage-point recall advantage and a paired 95% interval above zero. The original ten-point target was reduced after inspecting the pilot's attainable recall ceiling and before the evaluation. This history is documented in the [methods](../experiments/alignment_v3/docs/METHODS.md); it is not an independently registered protocol.

**Secondary question:** do the policies differ more strongly among flagged solutions whose final answer text matches the key? This subgroup is defined for evaluation and is not an input to queue ranking.

## What is implemented

| Component | V3 implementation |
| --- | --- |
| Inputs | Pinned PRM800K Phase 2 test records: generated solutions, reference answers, archived process-verifier scores, and human annotations. |
| Unit of review | One unique problem-and-solution pair after merging repeat annotations. |
| Split | Hash-based assignment of whole problems to pilot or evaluation. |
| Policies | Seeded random order, low final-answer agreement first, and low process-verifier score first. |
| Budget | A fixed fraction of all evaluation candidates; one selected candidate consumes one slot. |
| Labels | Flagged, cleared, or unresolved, derived from archived annotation finish codes. |
| Outcomes | Overall recall, answer-key-match recall, resolved-review precision, and flags left unreviewed. |
| Uncertainty | Paired bootstrap of whole problems with the review budget recomputed in each draw. |
| Audit | Answer normalization, original-path step ratings, unresolved-label bounds, and agreement tie-breaking. |

Ranking does not use the answer key or human outcomes. Agreement counts the candidate's own answer within its problem's unique-candidate pool. Both comparison policies reuse archived signals; generating those samples and verifier scores is outside the measured budget.

## Evidence

The evaluation has 2,195 unique solutions to 370 problems, with 1,643 flagged, 481 cleared, and 71 unresolved. At 20%, every queue selects 439 candidates.

- The verifier surfaces 403 flags, agreement 381, and the seeded random queue 335.
- The verifier-minus-agreement recall difference is 1.34 percentage points, with a paired 95% interval of 0.43–2.36 points.
- The point estimate misses the two-point practical criterion. The data do not establish that the true effect is below two points, since the interval includes that value.
- Among 80 flagged candidates whose answers match the key under the primary string rule, the verifier surfaces 30 and agreement nine. The descriptive recall difference is 26.25 points, with a 95% interval of 13.89–39.19 points.

These are committed replay results, not new measurements from the documentation revision. Counts and denominators are recorded in the [summary](../experiments/alignment_v3/results/summary.csv) and [manifest](../experiments/alignment_v3/results/manifest.json).

## Interpretation

A queue can perform similarly in total recall yet surface a different class of problems. V3's strongest descriptive finding concerns flagged explanations whose final answers match the reference.

The process verifier is an existing learned comparator, not a new model trained for this project. The contribution here is the budgeted replay comparison, the analysis of which flags each policy surfaces, and the accompanying audit. Novelty relative to the research literature is not established.

## Terminology and claim boundaries

- **Human-flagged:** an archived annotation identifies a problem under the specified label rule.
- **Answer-key match:** equality under a stated string-normalization rule, not proof that the solution is mathematically valid.
- **Review selected:** a candidate enters a queue; it does not mean a human reviewed or corrected it in this study.
- **Held out:** excluded from the V3 pilot at the problem level, without establishing upstream training independence.
- **Oversight:** allocating limited inspection opportunities. V3 does not establish corrigibility, preserved intervention feasibility, resistance to deception, or alignment of a deployed system.

Unresolved candidates remain eligible for review and consume slots. They are excluded from denominators requiring a conclusive human label. The source archive's verifier-guided sampling and high flagged prevalence limit external validity.

## Relationship to earlier experiments

[V2](../experiments/authority_v2/README.md) studies delayed, simulated reports of equipment health. Reviews reduce failed activations but also reduce output and the chosen synthetic utility relative to its no-review ablation. [v0.1](../experiments/factory_v0_1/README.md) studies production permission gates and has an oracle-information limitation.

The shared question is how limited oversight changes what gets inspected or acted on. V3 is an offline reasoning-review replay, V2 is a temporal simulation, and v0.1 is an earlier factory prototype. Their numerical results are not directly comparable.

## Next steps

The [current follow-up plan](NEXT_STUDY.md) proposes an independently sampled evaluation, a measured reviewer-time budget, and a prospective test of detection and correction. New protocols should be fixed before evaluating new data. The earlier [V2 value-of-information proposal](../experiments/authority_v2/docs/NEXT_STUDY.md) remains a separate, unimplemented production-study extension.

Earlier concept-stage notes remain available in Git history. This document describes the implemented V3 study and its next research questions.
