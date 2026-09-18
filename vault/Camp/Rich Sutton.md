---
title: "Rich Sutton"
date: 2026-09-16
tags: [people]
generated: 7f63a4e5450e
---
# Rich Sutton

*Reinforcement learning; the Bitter Lesson; Turing Award 2024*

Co-wrote the standard reinforcement learning textbook, shared the 2024 Turing Award with Andrew Barto, and in 2019 wrote the one-page Bitter Lesson that the Claude Code team keeps on the wall.

**What they would tell you**
- Methods that scale with computation win over methods that encode human knowledge.
- The lesson is bitter because it keeps being relearned.
- Search and learning are the two general methods.

**Going deeper**
The essay is short enough to read at the signpost. The textbook (free online) is the reference for RL, the technique behind RLHF at Stop 5. His argument is the intellectual backbone of the scaling era and of Cherny's "build for the model six months out".

**Rolinda asks:** Bitter for whom?

## The encounter
- What is the bitter lesson?
- Rich Sutton: That general methods which ride on more computation keep beating methods built around what we happen to know, over decades and across fields. ([The bitter lesson, summarised](https://en.wikipedia.org/wiki/Bitter_lesson))
- Which general methods?
- Rich Sutton: Two: search and learning. Deep Blue searched, AlphaGo Zero learned without the expert knowledge, and vision gave up its hand-made features. ([The bitter lesson, summarised](https://en.wikipedia.org/wiki/Bitter_lesson))
- Why bitter?
- Rich Sutton: Because it is less flattering to us than researchers expected, so they have been slow to accept it, and keep relearning it. ([The bitter lesson, summarised](https://en.wikipedia.org/wiki/Bitter_lesson))
- And the prize?
- Rich Sutton: The 2024 Turing Award with Andrew Barto, for the foundations of reinforcement learning: a machine that learns from experience, which is what Turing asked for in 1947. ([Turing Award 2024 (Amii)](https://www.amii.ca/updates-insights/rich-sutton-awarded-a-m-turing-award-for-reinforcement-learning-research))

## Your exercise: The rule you wrote against plain search
About 12 minutes, in `workspace/mentors/sutton/`. Status: not yet.

1. Write workspace/mentors/sutton/search.py with NUMS = [2, 17, 30, 41, 55, 70, 88].
2. First try a rule you invent for finding the two numbers that add up to 100, and print what it gives.
3. Then try every pair. Print exactly: search found: 30 70
4. Run it: python3 search.py. Then add notes.md with ## What I learned.

Checked by `vibe check --mentor sutton`: python3 search.py prints 'search found: 30 70'.

The plaque on the island reads: Search and learning scale.


## Sources
- [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)
- [Reinforcement Learning: An Introduction (free)](http://incompleteideas.net/book/the-book.html)
- [The bitter lesson, summarised](https://en.wikipedia.org/wiki/Bitter_lesson)
- [Turing Award 2024 (Amii)](https://www.amii.ca/updates-insights/rich-sutton-awarded-a-m-turing-award-for-reinforcement-learning-research)

Back to [[Your path]]

#people
