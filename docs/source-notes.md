# Source notes

These links were inspected during topic development on October 16, 2026. The notes distinguish established work from the proposed project's interpretation. This is an initial reading map, not an exhaustive literature review or a submission-ready bibliography.

## Predictive safety

[A predictive safety filter for learning-based control of constrained nonlinear dynamical systems — Kim P. Wabersich and Melanie N. Zeilinger](https://arxiv.org/abs/1812.05506)

The paper describes a model-predictive safety filter that accepts or modifies proposed control inputs while considering constraints and uncertainty. It establishes that looking ahead to preserve safety is not, by itself, a new contribution. Project implication: use a genuinely predictive baseline and identify what explicit intervention requirements add. The abstract was inspected; adapting the method requires a closer reading of the full formulation and assumptions.

## Multi-agent shielding

[Shield Decentralization for Safe Multi-Agent Reinforcement Learning — NeurIPS 2022](https://papers.neurips.cc/paper_files/paper/2022/hash/57444e14ecd9e2c8f603b4f012ce3811-Abstract-Conference.html)

This work studies decentralized shields for multi-agent systems. Project implication: distributing checks across workstations is established territory; a claimed contribution must specify the new intervention requirements or checking method. The conference abstract was inspected.

## Human control

[Human Control: Definitions and Algorithms — Ryan Carey and Tom Everitt, 2023](https://proceedings.mlr.press/v216/carey23a.html)

The paper formalizes shutdown instructability and analyzes related human-control concepts. Project implication: distinguish authorization, feasibility, and execution, and avoid treating the presence of a stop button as proof of corrigibility. The abstract was inspected; its formal definitions should be studied before claiming theoretical equivalence.

## Effects on other stakeholders

[When Empowerment Disempowers — Claire Yang, Maya Cakmak, and Max Kleiman-Weiner, original 2025 version](https://arxiv.org/html/2511.04177v1)

The inspected original version studies simulated multi-human gridworlds. Helping one user can reduce another person's environmental influence, while joint empowerment can mitigate that effect at a cost to the intended user's reward. Its methods, results, and limitations motivate measuring outcomes by stakeholder. They do not establish that the same effect occurs in manufacturing. The original version is linked explicitly because later versions may have a different title or content.

## SCOT

[The Social Construction of Facts and Artefacts — Trevor J. Pinch and Wiebe E. Bijker, 1984](https://research.utwente.nl/en/publications/the-social-construction-of-facts-and-artefacts-or-how-the-sociolo/)

The foundational article develops relevant social groups, interpretative flexibility, and closure mechanisms. Project implication: analyze how different interpretations of successful operation shape permission rules and intervention protections. The publication record and abstract were inspected. Applying SCOT to simulated governance arrangements does not demonstrate real stakeholder acceptance.

## Competition context

- [ISEF judging criteria](https://www.societyforscience.org/isef/grand-award/criteria/): engineering evaluation emphasizes a defined problem, alternative approaches, a prototype, and testing under multiple conditions.
- [ISEF rules for all projects](https://www.societyforscience.org/isef/international-rules/rules-for-all-projects/): the rules inspected require independent work and acknowledgment of AI assistance, and prohibit generative AI from writing the submitted research plan, abstract, or poster or creating citations. The researcher must read the applicable rules and sources directly before preparing competition materials.

## Next literature questions

- Which predictive or reachability methods already preserve delayed intervention outcomes?
- Can the proposed requirements be expressed directly in an existing constrained optimizer?
- What additional evidence would establish a computational contribution beyond changing the constraints?
- How have prior studies defined multi-stakeholder control and handled incompatible intervention rights?

Do not interpret an unsuccessful search as proof that an idea is new.
