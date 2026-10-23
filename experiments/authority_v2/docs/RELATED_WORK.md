# Related Work & The Limits of Our Novelty Claim

This benchmark is **not the first** risk-based human-control mechanism, AI control protocol, or model uncertainty monitor. The work should be introduced as a controlled empirical study of delayed health evidence and supervisory review workload in a small synthetic factory. It does **not** establish broader scientific novelty or LLM-safety efficacy.

## Closest methodological connections

1. **ControlArena (UK AI Security Institute and Redwood Research).** A framework to test AI control protocols against potentially untrusted agent behavior. It emphasizes the distinction between a model doing the task and an independent monitoring/deferral protocol. Our current simulation has no adversarial untrusted model and therefore does *not* test the threat model studied in ControlArena. Website: https://control-arena.aisi.org.uk/
2. **Kutasov et al. (2025), _Evaluating Control Protocols for Untrusted AI Agents_.** Compares deferral and oversight protocols under attacks and finds that critical-action deferral can be robust to adaptive attackers. Our work uses non-adversarial equipment failures, not malicious model behavior. arXiv: https://arxiv.org/abs/2511.02997
3. **Terekhov et al. (ICLR 2026), _Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols_.** Explains why an LLM monitor may become a vulnerable component when the monitored agent can influence it. Our equipment-risk estimator is numeric and not exposed to an attacking model. https://proceedings.iclr.cc/paper_files/paper/2026/hash/54b153ad8a138f4c186f21a8b7341d5e-Abstract-Conference.html
4. **Manheim and Homewood (2025), _Limits of Safe AI Deployment: Differentiating Oversight and Control_.** Differentiates preventive control from reactive monitoring and post-hoc oversight; helps clarify terminology for the permission gate. https://arxiv.org/abs/2507.03525
5. **Tsamados, Floridi and Taddeo (2025), _Human Control of AI Systems: From Supervision to Teaming_.** Discusses technical and conceptual challenges of human control over AI systems. https://doi.org/10.1007/s43681-024-00489-4

## Research gap to test, not assert

The candidate question is **whether delays, information staleness, and limited review capacity make selective human deferment worse than automated risk estimation**, and whether a value-of-information-aware intervention threshold can reverse the finding in held-out scenario shifts.

A publishable contribution would require novelty review, robust modeling of informative review actions, comparison to tuned POMDP/HMM alternatives, held-out validation, and eventually a connection to real agent control. This first version has *not* done those things.
