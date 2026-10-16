# Idea showcase: presenter guide

**The Right to Intervene**  
Preserving effective human control in AI-managed production systems.

**Stage:** research proposal. The walkthrough is a hand-calculated illustration. No controller implementation, experimental results, or confirmed novelty are claimed.

## Start here

1. Rehearse the short pitch below in your own words.
2. Open the [worked example](walkthrough.md) for a concrete explanation you can show on screen or act out with paper cards.
3. Review the [questions and answers](questions.md), especially the predictive-control comparison and SCOT connection.

The repository is private. For the showcase, use your signed-in screen or download these files beforehand. An audience member may not be able to open your repository link.

## The idea in one sentence

I want to test whether an AI-managed factory can keep enough time and resources available for people to carry out an authorized intervention later.

## 30-second pitch

> Imagine an inspector asks an automated factory to isolate a suspicious batch. The system accepts the command, but its transporter is already committed elsewhere. The inspector has permission, yet the intervention cannot finish on time. My proposed research asks whether an oversight system can preserve that ability before resources get committed. I would measure intervention success and production cost, and use SCOT to examine whose control the design protects. This is currently a research idea.

## 90-second pitch

> My project is called The Right to Intervene. It asks whether human control remains meaningful when several AI agents share a production system.
>
> Here is the problem: an inspector may be authorized to quarantine a batch, but earlier scheduling decisions can leave no transport capacity to move it before the deadline. A command can be accepted even though its outcome is no longer achievable.
>
> I propose an independent oversight layer that checks future intervention feasibility before approving production actions. It could reserve capacity or change the schedule when a protected intervention would otherwise become impossible.
>
> I would begin with a small simulated factory and compare the method against a strong predictive controller. Both would know the same system. To test an algorithmic contribution fairly, I would also compare methods with the same intervention requirements.
>
> SCOT, the Social Construction of Technology, helps ask whose definition of successful operation shapes those requirements. Managers may prioritize output, while inspectors need quarantine capacity and workers need meaningful pause options. Those are proposed stakeholder models, not interview findings.
>
> I would measure completed interventions by stakeholder alongside throughput and delays. The main uncertainty is whether existing predictive methods already solve the problem. My first step is to build a small example and test that baseline.

## Three-minute presentation route

| Time | Show or explain | Point to leave with the audience |
| --- | --- | --- |
| 0:00–0:25 | Title and short factory story | Permission does not ensure an achievable outcome. |
| 0:25–1:05 | Worked example timeline | An earlier resource commitment can remove a later option. |
| 1:05–1:35 | Proposed oversight | Check intervention feasibility before approving an action. |
| 1:35–2:00 | SCOT comparison | The chosen protections reflect whose priorities shape the system. |
| 2:00–2:40 | Experiment and baselines | Measure retained control and its cost against strong alternatives. |
| 2:40–3:00 | Status, uncertainty, next step | The first deliverable is a reproducible test of the mechanism. |

## Quick reference

**Question:** Can oversight preserve delayed human interventions while maintaining productive operation?

**Hypothesis:** Explicit intervention requirements will reduce avoidable deadline failures under shared-resource bottlenecks, with a measurable operating cost.

**Independent variables:** oversight method, request delay, resource scarcity, disruption, model error. Compare governance arrangements in a separate experiment with physical constraints fixed.

**Main outcome:** completed authorized interventions by deadline, reported separately for each stakeholder. Also measure production, safety violations, and computation time.

**Strong comparison:** network-wide predictive control, plus a small exact optimizer with identical intervention requirements.

**What could disprove the advantage:** the baseline already preserves intervention, or the proposed protection only works by effectively stopping production.

**First milestone:** reproduce the worked example in a simulator, independently check feasibility, and run the predictive baseline.

**Useful audience question:** “Which human intervention would you most want this system to preserve, and what production cost would you accept?” Treat informal answers as discussion, not research data.

## Before presenting

- Practice once with a timer and once without reading the script.
- Be able to explain why the transporter cannot switch tasks in the example.
- Keep the example and Q&A available offline.
- Describe proposed work in future tense and explain your own decisions accurately.

These are AI-assisted rehearsal notes for an idea showcase. Adapt the wording to your own understanding. See the [source notes](../docs/source-notes.md) for evidence boundaries and competition context.
