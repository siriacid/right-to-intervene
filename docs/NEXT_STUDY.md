# Proposed next study — from review queues to useful human review

**Status: proposal, not an implemented experiment or a report of new results.**

V3 found a small overall recall advantage for the process verifier and a larger descriptive advantage for flagged solutions with matching final answers. The next question is whether that selection advantage survives independent sampling and improves actual review outcomes.

[Current results](../experiments/alignment_v3/docs/RESULTS.md) · [Methods](../experiments/alignment_v3/docs/METHODS.md) · [Earlier V2 follow-up](../experiments/authority_v2/docs/NEXT_STUDY.md)

## 1. Evaluate an independently sampled archive

Collect a new set of problems and candidate solutions without selecting them using either evaluated ranking signal. Freeze problem selection, generation settings, deduplication, review budgets, and exclusion rules before evaluation.

Keep problem families separated across development and evaluation where possible. Record model and verifier versions and any known overlap with their training data. Obtain human annotations under a documented rubric, with adjudication of disagreements. Report missing and unresolved labels rather than treating them as successes.

Start with the existing random, answer-agreement, and process-verifier queues. A combined signal or cost-aware queue would be a new proposed policy; tune it only on development data and freeze it before the final comparison.

## 2. Measure review time and downstream outcomes

The current budget counts candidates equally. A prospective study should measure how long review takes and whether a reviewer detects, explains, or corrects a flagged issue. Allocate comparable reviewer-time budgets, not just equal counts.

Define review assignments and the adjudication procedure in advance. Record false alarms, missed errors, correction quality, review time, unresolved cases, and the quality of material left unreviewed. Keep reviewers unaware of queue identity where the study design permits.

No live participant study has been run by V3. A participant protocol and the applicable permissions would need to be established before recruitment.

## 3. Freeze the primary question before collecting results

Choose one primary comparison and specify:

- the review-budget unit and budget level;
- the population and sampling procedure;
- the primary outcome and practical effect threshold;
- how unresolved cases and reviewer disagreement are handled;
- disjoint development and evaluation sets;
- sample size based on pilot precision;
- the uncertainty method and treatment of multiple comparisons.

Treat answer-key-match findings as secondary unless a new study explicitly makes them primary in advance. Report mathematical-equivalence checks separately from string matching.

## 4. Outcomes that would challenge the proposed benefit

A useful follow-up must allow the verifier to fail. Its apparent advantage could disappear in an unselected sample, be explained by greater inference cost, concentrate on flags reviewers cannot reliably diagnose, or vanish under equal reviewer-time budgets.

Report those results directly. Adding more monitoring is beneficial only if its information improves decisions enough to justify its costs.

## 5. Release and reproducibility work

Preserve raw inputs where licensing permits, exact environment versions, configurations, candidate-level outputs, and implementation hashes. Add an immutable release and citation metadata after the researcher selects a license and publication plan. The existing replay and audit remain the reference until a new protocol and evaluation are completed.
