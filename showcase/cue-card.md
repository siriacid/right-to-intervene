# The Right to Intervene

**Presenter cue card · Idea showcase · Research proposal**

## Opening

Can an AI-managed factory keep enough time and resources available for people to carry out an authorized intervention later?

## Example

One shared transporter. A normal job takes 3 steps. A quarantine move takes 1 step. The inspector asks at time 1 and needs completion by time 3.

- Commit immediately: transporter frees at 3, quarantine finishes at 4. Too late.
- Preserve capacity: quarantine runs from 1 to 2. The normal job finishes later, at 5.

**Assumption:** transport jobs cannot be interrupted. These are illustrative numbers, not experimental results. A safe pause or deadline extension must be compared if available.

## Proposal

Before approving an action, check whether protected interventions remain possible. Reserve capacity or adjust scheduling when needed.

## SCOT

Managers may value output. Inspectors may value quarantine capacity. Workers may value pause rights. These are hypothetical stakeholder models. Compare which priorities shape the rules and who bears their costs.

## Test

Use a small simulated factory. Compare against network-wide predictive control and an exact optimizer with the **same intervention requirements**.

Measure completed interventions by stakeholder, plus throughput, delays, safety violations, and computation time.

## Honest limit

Existing predictive methods may already solve this. Novelty and performance remain untested. First: implement one small case, check it independently, and test the baseline.

## Close

“Which intervention would you protect, and what production cost would you accept?”

AI-assisted rehearsal aid. [Full guide](README.md) · [Example](walkthrough.md) · [Q&A](questions.md)
