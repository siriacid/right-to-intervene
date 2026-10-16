# The Right to Intervene

**Preserving effective human control in multi-agent production systems.**

This research concept investigates whether an AI-managed production network can remain safe in the present while making a later human intervention impossible—and whether adaptive oversight can prevent that loss of control.

**Status:** Concept development. This repository currently contains research documentation, not an implemented controller or experimental results. Novelty remains to be verified against the closest prior work.

## Research question

Can an adaptive oversight system preserve different stakeholders' ability to intervene after a specified response delay, while maintaining productive operation during cascading disruptions?

An intervention is effective only if the requested outcome can actually be achieved within its deadline. Accepting a command or providing a stop button does not, by itself, establish effective control.

## Why this matters

Imagine two assembly cells sharing transport, inspection, and storage. Production agents accelerate output and reserve resources. An inspector then requests that a suspicious batch be isolated. The command is accepted, but storage and transport capacity are already committed, so isolation cannot finish before the batch leaves the controlled area.

Each earlier decision may satisfy local rules while their combined consequences eliminate a protected intervention. The project studies how to detect and prevent this failure before those commitments are made.

## Proposed approach

An independent oversight layer evaluates proposed production actions against both operational constraints and explicit intervention requirements. Each requirement specifies an authorized requester, requested outcome, response delay, execution deadline, and constraints that must remain satisfied.

Before an action executes, the oversight layer checks whether protected interventions would remain feasible. It may reserve capacity, change a route, limit dispatch, or invoke a predefined fallback. Compatible intervention combinations and conflict priorities must be specified explicitly.

The initial simulated network would include two assembly cells, shared transport, an inspection station, limited storage, and a rework route. Physical implementation is a possible later extension.

## SCOT connection

Social Construction of Technology (SCOT) provides a framework for examining whose interpretation of successful operation shapes the oversight system. Managers, workers, inspectors, customers, and maintenance engineers may value different forms of control.

The project would compare alternative permission arrangements and measure who retains the ability to intervene, who bears the cost, and how those outcomes change under disruption. These arrangements are proposed experimental models, not evidence of real stakeholder agreement.

## Evaluation

The central comparison is against strong network-wide predictive safety control. A small-instance centralized optimizer given the same intervention requirements would provide an additional feasibility and performance reference.

| Question | Measurement |
| --- | --- |
| Does intervention remain effective? | Successful completion of authorized interventions within deadlines |
| How much response time is available? | Maximum tolerable intervention delay |
| Whose control is preserved? | Success and failure rates reported separately by stakeholder |
| What does protection cost? | Throughput, delivery delays, unused capacity, and computation time |
| Does the system remain safe? | Constraint violations and recovery time |

Tests would vary resource scarcity, inspection disruption, response delay, and prediction error. A controller that protects interventions by stopping almost all production would not establish a useful solution.

## Scope and next step

The target is a bounded mechanism for human control in simulated industrial systems. The project does not claim to solve superalignment or demonstrate control of AGI or ASI.

The first milestone is one small, independently checkable example where present safety and future intervention feasibility differ, followed by a comparison against a predictive controller.

## Supporting documentation

- [Research notes](docs/research-notes.md): intervention definitions, SCOT analysis, proposed comparisons, measurements, limitations, and milestones.
- [Source notes](docs/source-notes.md): related work, evidence boundaries, and links for further reading.

These documents were organized with AI assistance from project discussions. They are working repository documentation and require researcher review; they are not a completed ISEF submission.
