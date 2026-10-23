# Original research proposal

**Working topic:** The Right to Intervene: Preserving Human Control in Multi-Agent Production Systems.

**Status:** Historical concept notes from October 16, 2026. The [current benchmark](../experiments/authority_v2/README.md) implements a narrower study of delayed review and equipment-risk estimation. The intervention-feasibility guarantees, stakeholder comparisons, and predictive-control baselines below remain proposed work.

## 1. Problem and hypothesis

An AI agent can make an individually permissible decision that consumes resources needed for a later human intervention. Across interconnected workstations, several such decisions may prevent a protected outcome even when the system still accepts the human's command.

The proposed hypothesis is that explicitly preserving intervention feasibility will reduce failed authorized interventions relative to safety-only predictive control under shared-resource bottlenecks and delayed requests. This protection is expected to have a measurable cost in production, resource utilization, or computation; its practical value must be tested.

This separates three properties:

- **Permission:** the requester is authorized to issue the command.
- **Feasibility:** an available sequence of actions can achieve the requested outcome under the stated assumptions.
- **Execution:** the system actually completes that sequence by the deadline.

Feasibility alone does not establish reliable execution, and neither establishes that a permission arrangement is socially legitimate.

## 2. Intervention requirements

Each protected intervention needs a precise specification.

| Field | Example for an inspection intervention |
| --- | --- |
| Authorized requester | Quality inspector |
| Trigger | Suspected defect in an identified batch |
| Required outcome | Batch isolated in designated quarantine storage |
| Request delay | A bounded number of simulation steps between detection and arrival of the request |
| Execution deadline | Before release from the controlled area |
| Required resources | Transport availability and sufficient quarantine capacity |
| Persistent constraints | Physical limits and explicitly protected operational requirements |
| Conflict rule | Human-defined priority or escalation when another intervention competes for the same resources |

Delay and deadline are distinct: a request arriving on time may still be impossible to execute before its outcome deadline. Select actual numeric limits from the modeled process and document their justification before the main evaluation.

Checking each intervention separately does not prove that all can be executed simultaneously. Define the allowed combinations, priority rules, and resource commitments explicitly. When requirements become mutually infeasible, record the conflict and use an authorized fallback; do not silently weaken the requirements and report success.

Any guarantee must state the assumed disturbance bounds, state information, model accuracy, available actuators, and planning horizon. Failures outside those assumptions should be reported separately from failures within them.

## 3. Proposed system

The minimum useful environment is a discrete-event production network with two assembly cells, shared transport, inspection, limited storage, and rework. Different routes and processing times allow upstream choices to affect downstream capacity.

Production agents propose scheduling and routing actions. The oversight layer evaluates the resulting commitments and permits, modifies, or rejects the proposals. A predefined fallback controller handles situations where ordinary production cannot continue within the protected requirements.

Adaptive authority means that an agent's permitted actions depend on the current ability to preserve intervention. It does not mean that the agent can change the human-approved protections. Revisions to those protections require an explicitly authorized governance process.

Use machine-readable action and state records. Logs should identify the proposal, selected action, applicable intervention requirements, predicted resource usage, reason for intervention, and observed outcome. Log integrity is a useful extension, but not the central research contribution.

## 4. SCOT as an experimental design framework

SCOT asks how relevant social groups interpret an artifact and shape its accepted design. Here, the artifact is the oversight system, including its definitions of success, permission structure, and protected interventions.

| Group | Initial hypothesis about a valued outcome | Possible intervention to model |
| --- | --- | --- |
| Managers | Delivery reliability and productive flexibility | Reprioritize an order within agreed limits |
| Workers | Manageable workload and control over working conditions | Pause a workstation without violating other protected workload limits |
| Quality inspectors | Prevent release of questionable products | Quarantine or reinspect a batch |
| Customers | Maintain agreed service despite competing demand | Invoke a predefined minimum-service commitment |
| Maintenance engineers | Retain feasible opportunities to service equipment | Take equipment offline within an agreed window |

These are design hypotheses, not findings about actual people. Simulated stakeholder requests must be labeled as simulated; they cannot establish trust, acceptance, or legitimacy among real workers or customers.

**Interpretative flexibility:** a highly utilized buffer can signify productive efficiency to one group and a loss of emergency capacity to another.

**Closure and stabilization:** compare how different proposed arrangements settle design disagreements—for example, management-centered permissions, separate stakeholder vetoes, and negotiated intervention guarantees. Selecting one arrangement in software does not show that a real social disagreement has been resolved.

For each arrangement, measure both system performance and the distribution of retained control. Keep physical safety constraints fixed when isolating the effects of governance choices. Explain which commercial or workload commitments are treated as hard requirements, which are negotiable, and why.

## 5. Comparisons and fair evaluation

| Comparator | Role |
| --- | --- |
| Production-focused agents with basic physical limits | Expose the failure mechanism |
| Local safety shields | Test the sufficiency of workstation-level checks |
| Network-wide predictive safety controller | Strong baseline that already anticipates downstream consequences |
| Intervention-preserving oversight | Proposed protection for delayed authorized requests |
| Centralized optimizer with identical intervention requirements | Small-instance reference for feasibility and solution quality |

Use equivalent observations, disturbance assumptions, actuator access, and computation budgets where appropriate. Report unavoidable differences. Retain the same production policies when isolating the effect of the oversight layer.

There are two different claims to test: (1) whether including intervention requirements changes outcomes, and (2) whether a new algorithm enforces those requirements more effectively or efficiently. Beating a controller with a different objective supports the first claim, not automatically the second.

## 6. Conditions and measurements

Vary resource scarcity, inspection slowdowns, request delay, and processing-time prediction error. Include normal operation, individual disruptions, and combinations held out during development. Later tests can examine sensor errors and unfamiliar network layouts.

Report intervention success by stakeholder and intervention type, maximum tolerable delay, physical constraint violations, throughput, delivery delays, recovery time, unused capacity, and computation time. Define denominators and units before evaluation. Requests that were impossible even before the evaluated decision must not be mixed silently with avoidable failures.

For small cases, use an independent exact feasibility check to distinguish unavoidable failures from controller errors. Verify the modeled dynamics against hand-checkable traces. A matching implementation bug in the controller and evaluator must not become evidence of correctness.

Compare methods on paired scenarios and random seeds. Include independent training runs if policies are learned. Choose repetition counts and statistical methods after pilot estimates of variability; preserve raw results, configurations, software versions, and failed runs. Select thresholds using development cases rather than the held-out evaluation cases.

Useful ablations remove delay modeling, shared-resource coordination, or stakeholder-specific requirements one at a time. Each should address a stated mechanism rather than merely increase the number of experiments.

## 7. What would challenge the hypothesis?

- A well-tuned predictive controller already preserves the protected interventions.
- The proposed method only succeeds by stopping nearly all production.
- Improvements disappear after observations and computation budgets are matched.
- Model error defeats the predicted recovery paths.
- Benefits depend on one hand-designed bottleneck and do not extend to held-out cases.

Such results remain useful: they identify where explicit intervention protection is redundant, too costly, or unreliable.

## 8. Contribution and remaining uncertainty

Predictive safety, multi-agent shielding, corrigibility, and human empowerment are established research areas. The candidate contribution is an explicit treatment of stakeholder-specific intervention requirements, response delays, and production-resource commitments, together with a reproducible evaluation and potentially an efficient checking method.

The inspected sources did not establish this exact combination, but novelty is unconfirmed. The closest methods must be studied before making an originality claim. The immediate uncertainty is whether a strong predictive baseline already solves the intended examples.

## 9. Milestones and extensions

1. Specify one intervention and a minimal example with an independently verified loss of feasibility.
2. Implement and tune the strong predictive baseline.
3. Add explicit intervention preservation and measure its costs.
4. Extend to multiple stakeholders and conflicting requests.
5. Test held-out disruptions and network layouts; document failure boundaries.
6. Investigate whether stronger production optimization preserves or consumes intervention capacity.

Further extensions include larger networks, distributed feasibility checks, formal guarantees under bounded disturbances, and a physical demonstration. AGI/ASI and superalignment remain motivating questions beyond what the proposed industrial experiments could establish.

## Documentation provenance

These notes were organized with AI assistance from the project discussion on October 16, 2026. They record the original proposal, not empirical findings or stakeholder interviews.

