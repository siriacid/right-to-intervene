# Questions to prepare for

These are rehearsal answers based on the current proposal. They are not experimental findings. Use your own wording and describe only work you understand and have actually done.

## What is your project about?

I want to test whether a production system can preserve the resources needed for authorized human interventions that arrive after a delay. I would measure whether the requested outcome actually finishes on time and what protecting it costs production.

## Why is this interesting if a factory already has a stop button?

Stopping and completing an intervention are different outcomes. Pausing a line may leave a batch somewhere it still needs to be moved from. However, if an emergency stop or shipment hold safely resolves the requirement, that is a legitimate alternative I must include. My example explicitly assumes that an ongoing transport job cannot be interrupted.

## Isn't this ordinary scheduling or model predictive control?

It may be expressible with existing methods. Predictive safety is established work. My candidate contribution is a precise treatment of delayed, stakeholder-specific interventions and their resource costs. First I need to test whether a strong existing controller already handles them. An algorithmic novelty claim would need a comparison using the same requirements, observations, and relevant compute limits.

See the predictive-safety and shielding entries in the [source notes](../docs/source-notes.md). Those initial readings do not establish novelty.

## What would your system actually do?

Production agents would propose actions. A separate oversight component would predict whether protected interventions remain feasible after those actions. It could allow the action, change the schedule, reserve capacity, or use a predefined fallback. It would log the decision and later check what actually happened. This controller has not been implemented yet.

## What does “adaptive” mean?

The actions allowed at a given moment would depend on resource availability and intervention feasibility. The system would not be allowed to redefine human-approved protections merely to make its job easier. Changes to those protections would require a separate authorized decision.

## How does SCOT apply?

SCOT means Social Construction of Technology. It asks how relevant social groups interpret and shape a technology. In this project, the artifact includes the oversight rules. Managers, workers, and inspectors may disagree about what successful operation means. I would translate alternative interpretations into explicit permission arrangements and compare whose interventions remain achievable.

Interpretative flexibility appears when one group sees reserved capacity as waste and another sees it as essential control. Comparing proposed settlements can explore closure, but selecting a rule in software does not demonstrate real social acceptance. I have not collected stakeholder interviews.

## Who chooses whose intervention wins?

The governance arrangement must specify that before evaluation. I would define protected requests, allowed combinations, and conflict priorities explicitly. If two requests cannot both be satisfied, the system must report the conflict and use the stated escalation or fallback. Silently changing a requirement would not count as success.

## What is your hypothesis?

Under shared-resource bottlenecks and delayed requests, explicit intervention requirements will reduce avoidable failures compared with predictive control that only protects operational safety. That tests whether the added requirement matters. To test a new algorithm, I must also compare against an existing optimizer with identical intervention requirements.

## What would you measure?

The main measure is the fraction of authorized test requests completed by their stated deadline, separated by stakeholder and request type. I would report requests that were already impossible before the evaluated decision separately. Other measures include production output, delivery delays, physical violations, recovery time, and computation time. An overall average could hide a group repeatedly losing control.

## How will you make the comparison fair?

Methods would face paired scenarios with the same requests, initial state, and disturbances. I would match information and actuator access and report computation differences. For small instances, an independent exact feasibility check would help identify unavoidable failures. I would tune on development cases and reserve other disruptions for evaluation.

## Could you guarantee success just by stopping all production?

That might preserve some options, but it would not demonstrate useful production control. I would include throughput and delays alongside intervention success and compare methods across tradeoffs. The acceptable operating cost should be stated before interpreting the main results.

## What if the model is wrong?

Predicted feasibility can fail when real durations or disturbances exceed the model's assumptions. I would test timing error and bounded disruptions, then report where protection breaks. A guarantee would need explicit assumptions about uncertainty, sensing, and actuation. No such guarantee has been established here.

## What would make you change the idea?

If a well-tuned predictive baseline already solves the cases, there may be no algorithmic advantage. If improvement only appears in one carefully chosen example or requires near-zero production, the claim would need to narrow. Those results could still support a useful benchmark or clarify the cost of intervention requirements.

## What have you completed, and what comes next?

The repository contains the research question, proposed comparisons, an initial source map, and a hand-calculated presentation example. It does not contain an implemented controller or experimental results. The next step is a minimal simulator, an independently checked schedule, and a strong predictive baseline before expanding to multiple stakeholders.

## Where does AI fit? Do you need an LLM?

The initial production agents can use simple scheduling policies. I do not need to add a language model to test the control mechanism. Learned production policies could come later, once the environment and evaluation are reliable. The central question concerns what actions an automated decision-maker is allowed to commit to.

## Does this solve superalignment?

The motivating concern is meaningful human control. The proposed evidence would concern a bounded production simulator under explicit assumptions. It would not establish control of AGI or ASI. A later physical demonstration or larger network would be a further test, not an automatic generalization.

## What was your role, and how did you use AI?

Explain your actual contribution: which questions and constraints you chose, what sources you personally read, and which parts you can justify. AI assisted with organizing this repository and drafting these rehearsal materials. Do not claim to have implemented, tested, or personally read material you have not. The [source notes](../docs/source-notes.md) distinguish the initial reading depth and include competition context.

## If you do not know an answer

> I have not tested that yet. The assumption in my current model is ____. I would change ____ and measure ____ to investigate it.

Use that structure only when you can fill it honestly. A clear next test is more useful than a guessed result.

[Presenter guide](README.md) · [Worked example](walkthrough.md)
