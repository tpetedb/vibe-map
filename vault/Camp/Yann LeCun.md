---
title: "Yann LeCun"
date: 2026-09-16
tags: [people]
generated: da0bf1351a79
---
# Yann LeCun

*Turing Award 2018; convolutional networks; Meta AI chief scientist*

Applied backpropagation to handwritten digits in 1989 and invented the convolutional network that read cheques and zip codes in production in the 1990s. Shared the 2018 Turing Award with Hinton and Bengio. Argues loudly for open-weight models and that autoregressive LLMs are not the road to human-level intelligence; his alternative is JEPA, predicting in representation space.

**What they would tell you**
- Open weights let the world inspect and build; closed frontier models concentrate power.
- Next-token prediction is a dead end for true understanding; predict abstractions, not pixels or tokens.
- Engineering scepticism is healthy: ask what the system actually learns.

**Going deeper**
His 2022 position paper lays out a world-model architecture (JEPA) where the system learns to predict the abstract representation of the next state rather than every detail. Whatever one thinks of the forecast, it is the clearest statement of the case that today's LLMs are a plateau, and worth reading against the scaling-law view at Stop 4.

**Rolinda asks:** He does not think the thing I am using is the future?

## The encounter
- Why is he not impressed by the thing I am using?
- Yann LeCun: He argues that predicting the next token does not give a system a model of the world: it can sound right, hallucinate, and neither reason nor plan. ([Interview with TIME](https://time.com/6694432/yann-lecun-meta-ai-interview/))
- What would, then?
- Yann LeCun: Predicting in an abstract representation space instead of predicting every pixel. V-JEPA drops the detail nobody can predict, such as each leaf moving, and keeps what the scene is about. ([V-JEPA (Meta AI)](https://ai.meta.com/blog/v-jepa-yann-lecun-ai-model-video-joint-embedding-predictive-architecture/))
- And why open weights?
- Yann LeCun: Because these assistants will sit between people and their knowledge, and he does not think one company should own that layer. ([Interview with TIME](https://time.com/6694432/yann-lecun-meta-ai-interview/))
- Should I be frightened?
- Yann LeCun: He calls the doom case overstated: intelligence on its own does not produce a will to dominate. Hold that next to what Hinton says and keep both. ([Interview with TIME](https://time.com/6694432/yann-lecun-meta-ai-interview/))

## Your exercise: What mattered, and what you could throw away
About 12 minutes, in `workspace/mentors/lecun/`. Status: not yet.

1. Take one task you gave an agent recently.
2. Write workspace/mentors/lecun/abstraction.md with ## What mattered and ## What I could throw away.
3. Under the first, the few facts the answer depended on. Under the second, everything you fed it that turned out to be noise.
4. Add notes.md with ## What I learned.

Checked by `vibe check --mentor lecun`: abstraction.md separates what mattered from what you could throw away.

The plaque on the island reads: Predict the idea, not the pixel.


## Sources
- [A Path Towards Autonomous Machine Intelligence (LeCun 2022, OpenReview)](https://openreview.net/pdf?id=BZ5a1r-kVsf)
- [Backpropagation applied to handwritten zip code recognition (1989)](https://ieeexplore.ieee.org/document/6795724)
- [Karpathy's reproduction](https://github.com/karpathy/lecun1989-repro)
- [V-JEPA (Meta AI)](https://ai.meta.com/blog/v-jepa-yann-lecun-ai-model-video-joint-embedding-predictive-architecture/)
- [Interview with TIME](https://time.com/6694432/yann-lecun-meta-ai-interview/)

Back to [[Your path]]

#people
