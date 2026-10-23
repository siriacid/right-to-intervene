# Factory oversight benchmark (v0.1)

**Historical prototype.** Retained for methodological transparency and reproduction of the initial negative result. Start with the [current v2 benchmark](../authority_v2/README.md) for the active experiment.

This experiment tests adaptive permission gating in a **synthetic** two-stage factory with shared transport, inspection, and constrained buffers. It is not real-world safety validation.

## Run
```bash
python -m pip install -r requirements.txt
python experiment.py --trials 100 --horizon 240 --out results
python -m unittest discover -s tests -v
```

The experiment evaluates four strategies (unconstrained, reactive, fixed, adaptive) across four scenarios (normal, inspection slowdown, conflicting priorities, combined), using matched seeded demand draws. The controller can propose unsafe shipment without inspection or production into full storage; violations count both.

The adaptive policy **has oracle access to future arrivals and to the slowdown schedule**. Therefore comparisons cannot establish production-ready predictive control. Preliminary runs found zero modeled violations for both fixed and adaptive gates, with essentially identical verified throughput; adaptive did **not** outperform fixed.

Outputs are regenerated into `results/trials.csv`, `results/traces.csv`, `results/summary.csv`, `results/results.png`, and `results/tradeoff.png`. Summary confidence intervals are normal approximations over seeds, not paired-difference confidence intervals.

The v2 benchmark introduces delayed/noisy observations, review costs, and paired treatment differences in a different inspection model. A genuine production-planning action space and explicit intervention-feasibility evaluation remain future work; v0.1 and v2 results should not be pooled.

