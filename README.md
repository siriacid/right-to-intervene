# The Right to Intervene

**Studying when delayed human review helps—and when it costs more than it helps—in automated production.**

Right to Intervene is a Python research project on decision authority under uncertainty. Its current benchmark compares six policies in a synthetic inspection system with hidden equipment faults, delayed noisy sensors, and a limited budget for simulated human reviews.

**Status:** implemented simulation with exploratory results. The current experiment uses rule-based controllers, not an LLM or a learned production agent. It does not establish real-world safety or solve superalignment.

## Research question

When equipment health is uncertain, does requesting a delayed human review improve the tradeoff between verified output, failed equipment activations, and review workload compared with automated risk estimation alone?

The broader project asks whether people retain the practical ability to intervene after automated decisions commit shared resources. The current experiment studies one narrower component: the cost and usefulness of delayed information. It does not yet measure stakeholder-specific intervention feasibility or guaranteed completion of human commands.

## How the benchmark works

Two simulated job streams—urgent and standard—feed a shared inspection queue. Jobs are served by earliest deadline. A conventional inspection lane and a rapid lane have alternating service opportunities.

The rapid lane can fail without the controller immediately knowing. Its sensor reports the previous tick's health with noise. A permission gate decides whether to activate the rapid lane, restrict its use, revoke permission, or request a review. A simulated review returns the true equipment state **at the time of the request**, after a delay; that information may already be stale.

An independent quality-assurance interlock prevents unverified shipments for every policy. Consequently, the risk metric counts **attempted activations of failed equipment**, not defective shipments or injuries.

| Policy | Role |
| --- | --- |
| `conservative` | Never use the rapid lane. |
| `sensor_rule` | Activate when the delayed sensor reports healthy. |
| `reactive` | Apply the sensor rule with a cooldown after a failed activation. |
| `risk_calibrated` | Estimate health from past observations and action outcomes; use a dynamic threshold and budgeted reviews. |
| `risk_no_reviews` | Use the same estimator and threshold with reviews disabled. |
| `oracle` | Observe current hidden health; a privileged, non-deployable reference. |

Despite its identifier, `risk_calibrated` is a heuristic policy whose probability calibration has not been established. Delayed review evidence is combined approximately, not with exact Bayesian smoothing.

## Current results

The recorded main experiment contains **4,800 trials**: 160 paired seeds × six policies × five scenarios, each lasting 360 ticks. Policies share the same exogenous trace within each seed and scenario. The scenarios are normal operation, equipment wear, sensor noise, demand surge, and combined disruption.

Mean outcomes in the **combined-disruption** scenario:

| Policy | Verified deliveries | Failed activations | Reviews | Synthetic utility |
| --- | ---: | ---: | ---: | ---: |
| Conservative | 157.31 | 0.00 | 0.00 | 225.87 |
| Sensor rule | 227.23 | 21.09 | 0.00 | 211.99 |
| Reactive | 220.62 | 8.85 | 0.00 | 384.22 |
| Risk estimator + reviews | 241.48 | 7.67 | 21.88 | 439.88 |
| Risk estimator without reviews | 242.78 | 9.19 | 0.00 | 452.17 |
| Oracle reference | 250.99 | 0.00 | 0.00 | 629.26 |

**The central finding is a tradeoff.** Compared with the no-review ablation, adding reviews produces:

- **1.52 fewer failed activations** per trial (paired 95% bootstrap interval: −1.75 to −1.27).
- **1.29 fewer verified deliveries** (−1.66 to −0.91).
- **12.29 fewer utility points** (−16.35 to −7.97).

Reviews reduce risky activations, but their delay and cost make them less favorable under the chosen utility weights. The conservative policy achieves zero failed activations with substantially lower output; no deployable policy is best on every outcome.

Utility is a hand-selected combination of on-time deliveries, late deliveries, failed activations, review requests, and unfinished jobs. It is not a validated measure of societal benefit. The intervals use 1,000 paired bootstrap resamples, capture simulator-seed variation only, and are not adjusted for multiple comparisons.

See the [full results and limitations](experiments/authority_v2/docs/RESULTS.md), [summary data](experiments/authority_v2/results/summary.csv), and [paired effects](experiments/authority_v2/results/paired_effects.csv).

## Reproduce the experiment

Use Python 3.12, matching the repository's CI configuration. From a fresh checkout:

```bash
git clone https://github.com/siriacid/right-to-intervene.git
cd right-to-intervene
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r experiments/authority_v2/requirements.txt
cd experiments/authority_v2

python -m unittest discover -s tests -v
python experiment.py --trials 160 --horizon 360 --out results
python sensitivity.py --trials 80 --out results
```

The main runner generates per-trial data, selected seed-zero traces, summary tables, paired comparisons, a manifest, and PNG figures. The sensitivity runner adds 960 trials covering review budgets and delays. These commands overwrite files in the selected output directory; use `--out results-local` to keep the committed reference tables intact.

The repository includes compact reference tables. Full trial data and plots can be regenerated locally or obtained from a completed [GitHub Actions run](https://github.com/siriacid/right-to-intervene/actions). Dependency ranges are declared, but an exact environment lock and an immutable archival release remain to be added.

## Repository guide

| Location | Contents |
| --- | --- |
| [Current benchmark](experiments/authority_v2/README.md) | Environment, policies, parameters, and reproduction details. |
| [Methods](experiments/authority_v2/docs/RESEARCH_PROTOCOL.md) | Retrospective protocol, metrics, assumptions, and biases. |
| [Results](experiments/authority_v2/docs/RESULTS.md) | Scenario comparisons, paired intervals, and sensitivity analysis. |
| [Next study](experiments/authority_v2/docs/NEXT_STUDY.md) | Proposed value-of-information review policies and evaluation plan. |
| [Related work](experiments/authority_v2/docs/RELATED_WORK.md) | Literature map and boundaries of the novelty claim. |
| [Earlier experiment](experiments/factory_v0_1/README.md) | Historical v0.1 prototype, retained with its oracle-access limitation and negative result. |
| [Original research notes](docs/research-notes.md) | Broader intervention-feasibility proposal and stakeholder framework; not implemented by the current benchmark. |
| [Original source notes](docs/source-notes.md) | Background reading from the concept stage. |

## Limitations and next direction

The environment is synthetic, reviews are simulated perfect historical observations, and the quality-assurance interlock is assumed. Faults are exogenous; the model does not include adversarial agents, real workers, or a detailed transport-and-storage network. Thresholds and utility weights were selected during development, with no independent held-out evaluation or preregistration.

The next experiment should test **value-of-information review selection**: request a review only when its expected improvement to a future decision outweighs its delay and opportunity cost. Compare it with the no-review policy and an exact temporal belief estimator under matched information and review budgets. Freeze the protocol before evaluating on held-out seeds and shifted conditions.

The original intervention-rights question also needs a separate test: explicitly model a human request, its required resources, and its deadline, then measure whether earlier automated commitments make completion impossible.

Research documentation was developed with AI assistance. Scientific claims, source interpretation, and release decisions require researcher review.

