---
title: "Separation of concerns"
date: 2026-09-17
tags: [tech, code]
---
# Separation of concerns

One folder, one file, one function per concern, and a boundary between them that hides how each one works. This camp is the first example: the product (the game and the vibe command) is installed, not copied into your folder; the configuration (vibe.toml, AGENTS.md, the skills, the hooks) is visible and separate; your own work has one home, workspace/. The test of a good cut is Parnas's: does each part hide a decision that is likely to change on its own? When two concerns share a file, a change to one breaks the other for no visible reason; when they are apart, you can read, test and replace one without opening the rest. Ousterhout's version: prefer deep modules, a small interface over a lot of hidden work, to shallow ones that expose everything.

**History.** Dijkstra coined the phrase in 1974 (EWD 447): intelligent thinking means studying one aspect of a problem in isolation for its own consistency, without pretending the others do not exist. Parnas (1972) gave the criterion for where to cut: around design decisions likely to change, not around the order of processing steps (information hiding). Conway (1968) noticed that module boundaries end up copying the communication structure of the people who build them. Ousterhout (2018) restated it for today's code as deep versus shallow modules. The Twelve-Factor App (2011) applies it to config versus code; Team Topologies (2021) applies it to teams as cognitive load.

**Try in five minutes.** Open your camp. For each top-level folder and file write one line in a vault note: which of the three zones it belongs to (product, configuration, your workspace) and which decision it hides. Then find one place where a file mixes two concerns (a script that both computes and prints, a note that is also a config) and name it. Naming it is the exercise; splitting it is optional.

- Docs: [Dijkstra, On the role of scientific thought (EWD 447), 1974](https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD447.html), [Parnas, On the criteria to be used in decomposing systems into modules, 1972](https://web.archive.org/web/20230815003501/http://sunnyday.mit.edu/16.355/parnas-criteria.html), [Conway, How do committees invent?, 1968](https://www.melconway.com/Home/Committees_Paper.html), [Ousterhout, A Philosophy of Software Design, 2018](http://web.stanford.edu/~ouster/cgi-bin/aposd.php), [The Twelve-Factor App, III. Config](https://12factor.net/config), [Skelton and Pais, Team cognitive load, 2021](https://itrevolution.com/articles/cognitive-load/), [Source: Dijkstra, EWD 447 (the phrase and the definition); Parnas 1972 (information hiding as the criterion)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD447.html)
- Unlocks: [[Building the builder]], [[AGENTS.md]], [[TOML in practice - pyproject.toml]], [[Files, folders and paths]]
- Shelf: Languages and code · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
