# Proposed RTI 2.1 Study: Value-of-Information Human Interventions

**Current empirical puzzle:** On 160 paired combined-disruption seeds, budgeted human reviews reduce failed rapid-lane activations by ~1.52/trial versus the same risk estimator without reviews, yet reduce our chosen weighted utility by ~12.29 points. The next goal is to understand when a review *actually changes the optimal action*.

## Treatment arms (pre-register before coding)

1. `risk_no_reviews`: same Bayesian health belief but never escalates.
2. `risk_calibrated`: original request-on-uncertainty rule, with delay and finite budget.
3. `voi_myopic`: request only when estimated improvement from future information exceeds inspection opportunity cost and a per-review penalty.
4. `voi_multistep`: account for belief evolution, machine repairs, and high-priority jobs over an 8–16 tick rolling horizon.
5. `exact_hmm`: treat one-tick delayed sensor and lagged human reports as timestamped emissions, refilter or smooth beliefs exactly, combined with the same threshold action rule.
6. `budgeted_oracle`: oracle observes true health, but must honor all inspection and review capacity constraints; present solely as unattainable reference.

## Falsifiable primary tests

- **Hypothesis A:** With review delay ≥3 ticks, `voi_myopic` achieves greater utility than the current `risk_calibrated` under combined disruptions without exceeding its unsafe-activation rate.
- **Hypothesis B:** Under sensor correlation shifts, exact HMM or VOI control improves both safety calibration and inspected output compared with the hand-tuned approximate belief rule.
- **Hypothesis C:** Under a fixed review budget, VOI selection concentrates audits on high-urgency decisions and beats indiscriminate review scheduling by more than its paired 95% confidence interval.

## Protocol

Use disjoint development and final-evaluation seeds. A provisional target is 400 held-out seeds per scenario after the pilot code is frozen; justify the final count using pilot precision and specify the development-set size separately. Review answers must become available only after the specified delay, with their original observation timestamps retained. Compute paired-bootstrap intervals, correction for multiple primary comparisons, reliability diagrams, and a Pareto frontier with risk vs verified throughput vs human attention. Abandon a superiority claim if an appropriate baseline dominates on these outcomes.

## Red-team extension (separate threat model)

After establishing physically grounded state transitions, connect a sandboxed untrusted language-model planner that can propose different action sequences but cannot change the safety gate or its raw sensor stream. Introduce adversarially misleading self-reports and test whether independent numeric telemetry prevents bypass. Never present non-adversarial mechanical fault tests as evidence of resistance to deliberate deception.

## Priorities before a publication release

1. **Make the results independently checkable.** Add tests of timestamped observations, review arrival times, and information access, plus an independent evaluator of shipment validity. Existing tests check repeatability, accounting, and selected constraints; they do not prove absence of information leakage.
2. **Freeze the next comparison.** State exact disjoint tuning and final-evaluation seed sets, primary contrasts, utility-weight sensitivity, and correction for multiple comparisons before running the final evaluation. The 400 held-out seeds above are a proposed target; determine tuning size separately and justify final sample size from pilot precision.
3. **Test the mechanism.** Start with exact temporal belief updates and myopic value-of-information review selection. Compare against the no-review ablation under matched observations, action opportunities, and budgets before adding a longer-horizon controller.
4. **Connect back to intervention rights.** In a separate extension, specify a human request such as quarantine, the transport/storage resources it needs, and its completion deadline. Measure lost and preserved intervention feasibility against a predictive controller with identical requirements.
5. **Package a stable research release.** Record the source commit, exact Python/dependency versions, commands, seeds, and checksums with the raw data; verify the bibliography; choose a license and archive a versioned release with citation metadata. The current repository has no license file or archival identifier.

