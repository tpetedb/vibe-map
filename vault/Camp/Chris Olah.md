---
title: "Chris Olah"
date: 2026-09-16
tags: [people]
generated: 8b68298e87ca
---
# Chris Olah

*Interpretability research lead, Anthropic*

Co-founder of Anthropic and of Distill, the journal that made machine learning explanations visual. Leads the work on looking inside models: finding features and circuits that correspond to concepts, including in production Claude models.

**What they would tell you**
- A model is not a black box if you are willing to look.
- Features are the units of understanding; circuits are how they combine.
- Explain with pictures.

**Going deeper**
Transformer Circuits publishes the research: from toy models to finding millions of features in a real Claude model. For Evening 3 the takeaway is that non-determinism and hallucination are being studied mechanically, not just mitigated with rules, and that your checks are the practical layer on top of that science.

**Rolinda asks:** So someone is actually reading its mind?

## The encounter
- Is the model a black box?
- Chris Olah: Only if nobody looks. The whole thread asks whether a transformer can be reverse engineered into a program a person can read. ([Transformer Circuits](https://transformer-circuits.pub))
- What are they reading?
- Chris Olah: Features, the interpretable units pulled out with sparse autoencoders, and the circuits that connect them into behaviour. ([Transformer Circuits](https://transformer-circuits.pub))
- Why so many pictures?
- Chris Olah: Because an explanation you can see and poke at is the point. Distill was built for that, and for paying down the research debt that builds up when nobody explains. ([Distill](https://distill.pub))

## Your exercise: Draw the circuit of one decision
About 15 minutes, in `workspace/mentors/olah/`. Status: not yet.

1. Pick one decision a tool makes for you: a spam filter, a recommendation, an autocomplete.
2. Write workspace/mentors/olah/circuit.md with ## What I looked at and your best guess at the inputs, the middle and the output.
3. Draw it as a mermaid flowchart in a fenced block that starts with three backticks and the word mermaid.
4. Add notes.md with ## What I learned.

Checked by `vibe check --mentor olah`: circuit.md holds a mermaid diagram and what you looked at.

The plaque on the island reads: Look inside, and draw it.


## Sources
- [Transformer Circuits](https://transformer-circuits.pub)
- [Distill](https://distill.pub)

Back to [[Your path]]

#people
