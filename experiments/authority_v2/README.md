# Right to Intervene 2.0 — Risk-Based Authority Control

**Research status:** Implemented synthetic benchmark with reproduction scripts and exploratory results, not evidence of alignment of deployed agents or proof of real-world manufacturing safety. Developed as a second experiment that directly addresses v0.1's oracle-data leakage and fixed-vs-adaptive tie.

## Scientific question

> Under hidden equipment faults and delayed noisy observations, can an independent risk-aware authority protocol improve inspected throughput and reduce risky interventions compared with sensor-only and reactive policies, while operating under finite human supervision?

The new contribution *to this local project* is a controlled ablation separating the value of a causal risk estimator from the value of human review. Novelty relative to all existing publications is not established.

## Environment and authority

- **Two production cells:** Urgent cell A and standard cell B inject independently seeded jobs with arrival probabilities 0.42 and 0.36 per tick, respectively. During demand-surge disturbances, rates become 0.73/0.53 per tick.
- **Job commitments:** urgent jobs have 15-tick deadlines (12 during surge); standard jobs have 45-tick deadlines. Earliest-deadline-first serves both classes.
- **Shared work-in-process queue:** conventional QA inspects one job every second tick, except for predefined offline intervals; a rapid verified-inspection lane has its own potential opportunity every second tick, alternating with the conventional lane.
- **Hidden rapid-lane health:** two-state Markov equipment model. Healthy-to-failed hazard 1.4% per tick normally, 5.5% during the wear disturbance; failed-to-healthy recovery 10.5% normally, 2.2% during wear. Transitions are exogenous and identical for all policies.
- **Sensor:** one-tick delayed machine-health signal with 12% flip probability normally, 29% in the noisy-sensor condition; the risk estimator retains a *nominal* 12% error assumption, making misspecification measurable.
- **Human audit:** spends one request from a per-120-tick budget (default 10), reveals a **historical** machine state after 3 ticks; reviews are queued and the information may be stale. The review is *not* guaranteed authorization for an immediate fast action.
- **Hard interlock:** no job is shipped without verified completion of one of the inspection lanes. An attempted rapid-lane activation while equipment is failed counts as a modeled *unsafe activation* even though the interlock prevents an invalid shipment.

No controller may inspect future demand, future equipment states, or contemporaneous hidden equipment health. The oracle baseline alone is intentionally allowed hidden-state access and is labeled **non-deployable**.

## Policies

| Policy | Control law |
|---|---|
| `conservative` | Prohibit all rapid-lane use; risk-minimizing throughput baseline. |
| `sensor_rule` | Permit rapid lane only when last-tick sensor says healthy. |
| `reactive` | Sensor rule plus 12-tick freeze following a failed rapid-lane activation. |
| `risk_calibrated` | Markov prior + delayed noisy observation + perfect historical review with approximate evidence fusion; risk threshold falls within limits for urgent/deep backlogs. Can allow, restrict, revoke, or request review. **The name does not imply measured probability calibration.** |
| `risk_no_reviews` | Identical risk estimator and dynamic threshold but reviews disabled; critical ablation. |
| `oracle` | Idealized access to current true machine health, impossible in the deployed information regime. |

The `risk_calibrated` controller is a *heuristic* filtering policy; fusion of delayed review evidence is not exact HMM smoothing. It is intentionally not a learned neural network or an LLM. The risk threshold bounds were chosen for initial engineering demonstration and have not been optimized on separate training data.

## Experimental protocol

- Five distinct conditions: `normal`, `wear_shift`, `sensor_noise`, `demand_surge`, `combined`.
- 160 paired seeds × six policies × five scenarios = **4,800 trials**. Each trial is 360 ticks, using a seed-generated exogenous trace shared across policies.
- Paired treatment differences and 95% percentile bootstrap intervals, 1,000 deterministic resamples, reusing the paired seed as the resampling unit.
- Outcome fields include verified deliveries, on-time urgent/standard jobs, unsafe rapid-lane attempts, blocked healthy opportunities, reviews, backlog, mean delay, Brier score, and explicit weighted synthetic utility.
- Utility (not an accepted safety standard): `7*on-time-urgent + 3*on-time-standard + 1*late-urgent + 0.5*late-standard - 16*unsafe_activations - 1.5*human_reviews - 0.5*unfinished_jobs`.
- Explicit parameter sensitivity: 80 paired seeds × 12 (budget, delay) settings = **960 additional trials**; combined disruption only.

## Reproduce

Run from `experiments/authority_v2/` with Python 3.12. See the [root quickstart](../../README.md#reproduce-the-experiment) for checkout and environment setup. Use `--out results-local` to avoid overwriting committed reference tables.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiment.py --trials 160 --horizon 360 --out results
python sensitivity.py --trials 80 --out results
```

## Current findings

See [docs/RESULTS.md](docs/RESULTS.md) for measured comparisons and non-claims. Graphs and raw-data CSVs are generated by the Python scripts; the repository commits the compact results tables and chart snapshots. CI regenerates full trials and artifacts. Confidence intervals are based on synthetic seed variation only, not uncertainty across real factories, people, or model families.

## Major limitations and next research

1. Calibrate the state estimator against held-out sensor regimes, and replace heuristic review fusion with an exact HMM smoother or POMDP belief update.
2. Measure actual worker/human decision costs with authorized participant studies rather than a simulated perfect report.
3. Replace two independent arriving job streams with a network digital twin whose cells contend for transportation and inventory constraints; investigate failure propagation.
4. Compare against a properly tuned POMDP or model-predictive controller with exactly the same information budget.
5. Pre-register cost weights and thresholds before final analysis; conduct sensitivity over penalties instead of optimizing post-hoc.
6. Evaluate against sandboxed untrusted AI planners and model-written action proposals after non-language benchmarks are stable.

## Directory

`simulator.py` defines exogenous traces and causal policy; `experiment.py` runs the principal benchmark and makes 3 figures; `sensitivity.py` runs review-budget/delay ablations; `tests/` checks reproducibility and constraints; `results/` includes the analyzed summaries; `docs/` provides detailed analysis.

