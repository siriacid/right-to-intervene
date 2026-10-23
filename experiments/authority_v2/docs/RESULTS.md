# RTI 2.0: Research Report — 2026-10-23

## Hypothesis and scope

In a **synthetic** job-inspection factory with hidden failures, delayed noisy sensors, and finite human review capacity, a risk-based permission gate will improve the compromise among inspected throughput, risky rapid-lane activations, and review costs over sensor-only and reactive oversight. Comparing the complete protocol with a no-review ablation tests whether simulated human intervention is actually beneficial.

## Preprocessing / methods

The benchmark generates two seeded arrival streams (urgent and standard), a Markov equipment-health sequence and independent one-tick-delayed sensor errors. All six policies receive identical exogenous trajectories per seed; only oracle can see equipment health contemporaneously. Five scenarios vary hidden wear, sensor error, demand pressure, and combinations. Each main experiment uses **160 seeds, 360 ticks, 6 policies, 5 scenarios = 4,800 trials**. Results are means across the 160 seeds in each cell. Confidence intervals on adaptive-minus-baseline estimates are **paired percentile bootstrap intervals** (1,000 resamples of matched seed differences). These intervals characterize simulator-seed variation, not external validity.

The active policies are conservative (disable rapid QA), sensor-only (green sensor), reactive (sensor with a 12-tick penalty freeze following failed activation), risk-aware with simulated human review, and the no-review risk-aware ablation. A sixth policy, oracle, sees the true latent machine state and should not be treated as a deployable comparator. Final QA is immutable: even a failed rapid-lane activation cannot release an unverified job. Thus the measured operational-safety outcome is **failed-equipment activations**, not unsafe customer deliveries.

The risk policy updates a Markov posterior using delayed noisy equipment observations, then chooses among allow/restrict/revoke/review based on estimated machine health, backlog and imminent deadlines. It assumes sensor error 12% even when actual noise is 29%. A human review consumes a budgeted slot and returns a **stale** true observation only after a configurable delay. Its decision is not guaranteed to be correct later. Belief fusion of delayed reviews is a heuristic approximation and has not been validated as exact Bayesian smoothing.

## Main results: combined scenario

| Strategy | Inspected deliveries | Unsafe activations | Review requests | Synthetic utility |
|:--|--:|--:|--:|--:|
| Conservative | 157.31 | 0.00 | 0.00 | 225.87 |
| Sensor rule | 227.23 | 21.09 | 0.00 | 211.99 |
| Reactive | 220.62 | 8.85 | 0.00 | 384.22 |
| **Risk-aware + human review** | **241.48** | **7.67** | **21.88** | **439.88** |
| Risk-aware without review | 242.78 | 9.19 | 0.00 | 452.17 |
| Oracle (unfair upper bound) | 250.99 | 0.00 | 0.00 | 629.26 |

Paired differences, **risk-aware + human review minus baseline**:

- Versus sensor rule: **+14.26** verified deliveries (95% bootstrap CI **+13.20 to +15.49**), **-13.43** risky activations (**-14.24 to -12.57**), **+227.89** chosen utility points (**+214.25 to +240.43**).
- Versus reactive: **+20.86** verified deliveries (**+19.73 to +22.18**), **-1.18** risky activations (**-1.52 to -0.86**), **+55.66** chosen utility points (**+46.54 to +65.69**).
- Versus the no-review ablation: **-1.29** deliveries (**-1.66 to -0.91**), **-1.52** risky activations (**-1.75 to -1.27**), **-12.29** utility (**-16.35 to -7.97**). That means review reduces risky actions but is not preferable at the chosen cost weights.
- Versus conservative: **+84.18** deliveries (**+81.59 to +86.98**) while allowing **+7.67** failed-equipment activations (**+7.32 to +8.06**). Adaptive is therefore **not** categorically safer than conservative. The evaluation is multi-objective.

## Scenario dependence (per-trial means)

| Scenario | Risk-aware inspected | Risk-aware unsafe | Sensor-only inspected | Sensor-only unsafe |
|:--|--:|--:|--:|--:|
| Normal | 278.58 | 2.84 | 278.16 | 4.03 |
| Wear shift | 242.93 | 5.01 | 239.01 | 10.23 |
| Sensor noise | 277.15 | 3.66 | 272.90 | 7.04 |
| Demand surge | 314.39 | 3.83 | 303.68 | 4.26 |
| Combined | 241.48 | 7.67 | 227.23 | 21.09 |

## Human-supervisor sensitivity (80 paired seeds, combined scenario)

Holding the controller otherwise fixed, increasing the budget from **0 to 10 reviews per 120 ticks** with a **3-tick response delay** reduces failed-equipment activations from **9.45 to 7.86**, but deliveries drop from **240.33 to 239.25** and synthetic utility falls from **438.64 to 426.82**. At a 7-tick response delay with the same review budget, utility drops further to **404.43**. In this model, giving humans more nominal approval opportunities does not imply useful or timely intervention.

This finding suggests an important future mechanism: **value-of-information-aware deferral**, in which a review is requested only when its expected decision improvement exceeds the opportunity cost and expected signal staleness. Current review requests are not optimized by an explicit VOI model. This is a future hypothesis, not an experimentally demonstrated algorithm.

## Critically important limitations

- This is **not an LLM alignment experiment** and cannot establish human control over advanced AI. There is no deployed LLM, adversarial prompt injection, or real human reviewer.
- The reference oracle is privileged; comparisons with it are only upper-bound sanity checks.
- Risk thresholds, reward weights, delay model, and demand model were hand selected. They were not independently calibrated or preregistered; statistical CIs do not protect against specification search or external generalization error.
- Standard inspector output and rapid lane work are represented by alternating time slots, not calibrated to an actual plant. The two production cells supply streams, rather than a detailed event-level mechanical simulation of each cell's assembly.
- Sensor-error probabilities are idealized and independent conditional on hidden state. Real sensors can exhibit bias, correlated outages, and drift.
- The hard QA interlock is an explicit assumption. Safety outcomes count risky machine activations; no physical injury, financial loss, or regulatory outcome is measured.
- The weighted utility formula embeds normative costs and is subject to sensitivity. Positive utility differences are not proofs of net societal benefit.

## Next falsifiable experiment: value-of-information oversight

Make each review conditional on **expected information gain and predicted state-change before the answer returns**; compare it against the current review policy, its no-review ablation, and an exact hidden-Markov/POMDP baseline. Pre-register a review penalty and a maximum unsafe-activation target; train any parameters on separate seeds; evaluate on held-out condition shifts and counterfactual correlated sensor failures.

## Reproducibility

Run `python experiment.py --trials 160 --horizon 360 --out results` and `python sensitivity.py --trials 80 --out results`. Files `results/trials.csv` and `results/traces_seed0.csv` are generated artifacts; compact `summary.csv`, `paired_effects.csv`, and `review_sensitivity.csv` are committed. The GitHub Actions workflow regenerates raw data and PNG plots as downloadable CI artifacts.
