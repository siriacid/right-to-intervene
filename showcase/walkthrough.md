# A command accepted too late

**Illustrative model only.** This is a hand-calculated scheduling example, not a simulation result, a validated factory model, or evidence that the proposed algorithm outperforms existing methods.

## Setup

Two assembly cells share one transporter. A batch is waiting at inspection, and an empty quarantine space is available.

| Item | Assumption for this example |
| --- | --- |
| Normal transport job | Occupies the transporter for 3 time steps. |
| Quarantine move | Occupies the same transporter for 1 time step. |
| Inspector request | Arrives at time 1. |
| Required outcome | Complete the quarantine move by time 3, inclusive. |
| Task switching | A transport job already underway cannot be interrupted in this model. |
| Other resources | Quarantine space and the route are available. |
| Current safety | Either initial choice respects the modeled physical limits. |

Time steps are arbitrary units. These durations and the deadline are chosen to explain the mechanism, not measured from equipment. At each boundary, completed tasks release their resource before a new task starts.

The time-3 deadline is an operational intervention requirement. Missing it is a failure of that requirement, not automatically a physical accident. A real system might safely extend a deadline, pause shipment, or interrupt a task. Those options must be modeled and compared when available.

## Two schedules

| Time | Commit the transporter immediately | Preserve capacity for a request at time 1 |
| --- | --- | --- |
| 0 | Start the normal job. Transporter committed until time 3. | Defer the normal job for one step. |
| 1 | Inspector requests quarantine. The command is authorized, but the transporter is busy. | Inspector requests quarantine. Start the move now. |
| 2 | Normal job continues. | Quarantine completes. Normal job can now start. |
| 3 | Normal job completes. Earliest possible quarantine start is now. | Quarantine has already met its deadline. |
| 4 | Earliest quarantine completion, one step late. | Normal job continues. |
| 5 | — | Deferred normal job completes. |

The calculation is simple: with the initial commitment, the earliest finish is **3 + 1 = 4**, after the deadline of **3**. With capacity preserved, it is **1 + 1 = 2**.

At time 0, quarantine after the specified request delay is still possible. Starting the normal job removes that option under the stated assumptions. An oversight rule could detect this before approving the job.

This protection costs something. In the illustrated request case, the normal job finishes at time 5 instead of time 3. If no request arrives at time 1 and no later request is protected in this small example, the deferred normal job could run from time 1 to time 4. These are schedule calculations, not measured throughput effects.

## What the example establishes

It shows that authorization, present physical feasibility, and future intervention feasibility can differ in a specified resource model. It also makes the production tradeoff visible.

It does **not** establish novelty, robustness, fairness, or an algorithmic advantage. A conventional scheduler given the same quarantine requirement could choose the same protected schedule. A good experiment must include that comparator.

## A one-minute tabletop demonstration

Use two paper cards labeled **normal job: 3 steps** and **quarantine: 1 step**, one token labeled **transporter**, and a paper timeline from 0 to 5.

1. Put the transporter on the normal-job card at time 0. Move the timeline marker to time 1 and announce the quarantine request.
2. Ask: “When can the move finish?” Show that the transporter releases at 3 and quarantine finishes at 4.
3. Reset. Keep the transporter available until time 1, then assign it to quarantine. Show completion at 2 and the delayed normal job finishing at 5.
4. Ask: “Who should be allowed to require that reserved capacity, and how much delay is acceptable?”

## Where SCOT enters

A manager may interpret the idle step as lost capacity. An inspector may interpret it as the capacity needed to exercise control. These are hypothetical interpretations for the model.

Compare an output-focused arrangement with an arrangement that explicitly protects quarantine after a bounded delay. Record which actions each arrangement permits and who bears the delay. A later experiment can add worker pause rights and conflicts over the same transporter. Simulated rules cannot establish real stakeholder agreement.

## The next experiment

Implement this trace, including the non-interruption assumption and precise deadline. Check it with an independent enumeration of possible schedules. Then test a predictive controller with and without the explicit quarantine requirement. Vary request timing, allow safe interruption or shipment holds, and see when the protection is useful, redundant, or too expensive.

[Presenter guide](README.md) · [Questions and answers](questions.md) · [Full research design](../docs/research-notes.md)
