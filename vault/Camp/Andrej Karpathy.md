---
title: "Andrej Karpathy"
date: 2026-09-16
tags: [people]
---
# Andrej Karpathy

*Researcher, educator; ex OpenAI, ex Tesla AI*

Founding member of OpenAI, led Tesla Autopilot's AI team, taught Stanford's first deep-learning class, and now teaches the internet: the Zero to Hero series builds neural networks from scratch in code, and the general-audience talks explain LLMs without maths. Coined "vibe coding" in 2025 and "Software 3.0" for programming in natural language.

**What they would tell you**
- Build the smallest version yourself; understanding follows from code you can run.
- LLMs are a new kind of computer: the prompt is the program.
- Vibe coding is real and fine for the right projects; know when you are doing it.

**Going deeper**
Zero to Hero goes micrograd (a 100-line autograd engine), makemore (character-level language models, five parts), a WaveNet, then a GPT built to the 2017 paper, then the tokenizer. The general-audience track covers how LLMs are trained and how he uses them. He was the human baseline for ImageNet in 2014 and wrote the reproduction of LeCun's 1989 paper on modern hardware.

**Rolinda asks:** If the prompt is the program, who is the programmer?

## The encounter
- Where do I start with models?
- Andrej Karpathy: With the smallest one you can write yourself. His course opens with a hundred-line autograd engine and a character-level bigram model before anything larger. ([Zero to Hero course](https://karpathy.ai/zero-to-hero.html))
- What is a bigram model?
- Andrej Karpathy: Count which character follows which, then pick the likely next one. Makemore part one builds exactly that from scratch, with training, sampling and a loss. ([nn-zero-to-hero on GitHub](https://github.com/karpathy/nn-zero-to-hero))
- Why from scratch when a library exists?
- Andrej Karpathy: Because the understanding comes from code you can run. The track goes micrograd, makemore, a WaveNet, a GPT to the 2017 paper, then the tokenizer. ([Zero to Hero course](https://karpathy.ai/zero-to-hero.html))
- And for people who only use the models?
- Andrej Karpathy: There is a general track next to the technical one on his page: the same ideas, without the mathematics. ([karpathy.ai](https://karpathy.ai/))

## Your exercise: A bigram model in twenty lines
About 15 minutes, in `workspace/mentors/karpathy/`. Status: not yet.

1. Write workspace/mentors/karpathy/bigram.py with TEXT = 'the cat sat on the mat'.
2. Count every pair of neighbouring characters into a dictionary of dictionaries.
3. Find the character that most often follows 'a' and print exactly: after a: t
4. Run it: python3 bigram.py. Then add notes.md with ## What I learned.

Checked by `vibe check --mentor karpathy`: python3 bigram.py prints 'after a: t'.

The plaque on the island reads: Build the small one first.


## Sources
- [karpathy.ai](https://karpathy.ai/)
- [Zero to Hero course](https://karpathy.ai/zero-to-hero.html)
- [nn-zero-to-hero on GitHub](https://github.com/karpathy/nn-zero-to-hero)
- [vibe coding post](https://x.com/karpathy/status/1886192184808149383)

Back to [[Your path]]

#people
