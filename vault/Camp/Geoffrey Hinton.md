---
title: "Geoffrey Hinton"
date: 2026-09-16
tags: [people]
generated: 0d0082ab5eb5
---
# Geoffrey Hinton

*Backpropagation, deep learning; Nobel Prize in Physics 2024*

Co-author of the 1986 paper that made backpropagation practical, teacher of Sutskever and Krizhevsky (AlexNet), Turing Award 2018, Nobel Prize in Physics 2024 for foundational work on learning in neural networks. Left Google in 2023 to speak freely about risks.

**What they would tell you**
- Distributed representations: a concept is a pattern across many units, not one unit.
- Learning by error propagation scales; hand-written rules do not.
- Take the risks seriously; the people who built it are worried.

**Going deeper**
The 1986 Nature paper is three pages and readable. His Nobel lecture and the prize's popular-science summary explain Boltzmann machines and why physics gave the prize. His post-2023 interviews are the clearest lay statement of why some pioneers turned cautious.

**Rolinda asks:** He won a physics prize for this?

## The encounter
- What did he actually invent?
- Geoffrey Hinton: He was one of the researchers who introduced back-propagation, and distributed representations come from that line of work: a concept is a pattern across many units, never one unit. ([His page at Toronto](https://www.cs.toronto.edu/~hinton/))
- And a Nobel Prize in physics?
- Geoffrey Hinton: Shared with John Hopfield in 2024, for the discoveries that make machine learning with neural networks possible. His Boltzmann machine learns to recognise characteristic elements in data. ([Cambridge on the 2024 Nobel Prize](https://www.cam.ac.uk/research/news/university-of-cambridge-alumnus-awarded-2024-nobel-prize-in-physics))
- Why does he warn about it now?
- Geoffrey Hinton: He argued in Cambridge that large scale digital computation is probably far better at acquiring knowledge than biological computation, and may soon be much more intelligent than us. ([Cambridge on the 2024 Nobel Prize](https://www.cam.ac.uk/research/news/university-of-cambridge-alumnus-awarded-2024-nobel-prize-in-physics))

## Your exercise: Twenty steps of learning from error
About 12 minutes, in `workspace/mentors/hinton/`. Status: not yet.

1. Write workspace/mentors/hinton/descent.py with w = 0.0 and the target function f(w) = (w - 3) ** 2.
2. Twenty times: compute the gradient 2 * (w - 3) and take a step of 0.1 against it.
3. Print each step, and at the end print exactly: w = 3.0 (use round(w, 1)).
4. Run it: python3 descent.py. Then add notes.md with ## What I learned.

Checked by `vibe check --mentor hinton`: python3 descent.py ends at 'w = 3.0'.

The plaque on the island reads: A concept is a pattern.


## Sources
- [Learning representations by back-propagating errors (Nature 1986)](https://www.nature.com/articles/323533a0)
- [Nobel Prize 2024, Hinton facts](https://www.nobelprize.org/prizes/physics/2024/hinton/facts/)
- [His page at Toronto](https://www.cs.toronto.edu/~hinton/)
- [Cambridge on the 2024 Nobel Prize](https://www.cam.ac.uk/research/news/university-of-cambridge-alumnus-awarded-2024-nobel-prize-in-physics)

Back to [[Your path]]

#people
