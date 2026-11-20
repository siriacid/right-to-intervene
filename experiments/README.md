# Experiment index

**Start with [V3: human review of LLM reasoning](alignment_v3/README.md).** It is the current Right to Intervene study. Earlier experiments remain available for reproduction and methodological context.

| Version | Question | Evidence and status |
| --- | --- | --- |
| [V3 — LLM review selection](alignment_v3/README.md) | Which archived solutions should a human inspect under a fixed candidate budget? | Current offline replay on PRM800K; methods, results, audit, and robustness checks are committed. |
| [V2 — delayed production review](authority_v2/README.md) | Does a delayed report of hidden equipment health improve decisions relative to the same estimator without reviews? | Earlier synthetic benchmark with 4,800 main and 960 sensitivity trials. |
| [v0.1 — factory permission gates](factory_v0_1/README.md) | Do adaptive gates improve a simple factory's modeled outcomes over fixed gates? | Historical prototype with oracle-access limitations and no observed adaptive advantage over the fixed gate in preliminary runs. |

V3 counts human-flagged solutions selected for review. V2 counts equipment activations, verified deliveries, and simulated review costs. v0.1 counts production outcomes and modeled constraint violations. These are different experiments, not successive evaluations on a common benchmark.

## Run the existing tests

Use Python 3.12. From the repository root, run each suite from its own experiment directory so local imports resolve correctly:

~~~bash
(cd experiments/alignment_v3 && python -m unittest discover -s tests -v)
(cd experiments/authority_v2 && python -m unittest discover -s tests -v)
(cd experiments/factory_v0_1 && python -m unittest discover -s tests -v)
~~~

V3's core tests and metrics runner need only the standard library. Earlier simulation runners and optional V3 plots require the dependencies described in the relevant experiment README.

Follow each version's reproduction instructions and write fresh outputs to results-local. Committed reference results retain their original provenance. The [current next-study plan](../docs/NEXT_STUDY.md) describes proposed work rather than an implemented fourth version.
