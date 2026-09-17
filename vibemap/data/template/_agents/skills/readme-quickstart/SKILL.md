---
name: readme-quickstart
description: Writes or repairs a README.md that gets a stranger from clone to a working run on the first screen (name, one line on what and for whom, quickstart with exact commands, usage, structure, contributing, licence), after makeareadme.com and Tom's doc-doc templates. Use when the user says "write a README", "improve the README", "add a quickstart", "how do people get started", "document how to run this", "onboarding docs", or a project has no README.
allowed-tools: Read Bash(ls *) Bash(cat README.md)
---
# README and quickstart

The README is the first thing a person sees and the last thing maintainers update. GitHub shows it under the file list, so it is the front page. Guide: https://www.makeareadme.com

Rules:
- `README.md` at the repo root. Line one: the name. Line two: one sentence saying what this is and for whom. Why: a reader decides in ten seconds whether to keep reading.
- The quickstart is on the first screen: prerequisites, install, run, in that order, every command in a fenced block, with the output the reader should see. Why: the reader wants to run it, not read about it.
- Every command in the README is copied from a terminal where it just worked. Run them again when they change. Why: a README that lies costs more than no README.
- Order after the quickstart (the doc-doc house order): Usage, Project structure, Architecture, Contributing, License. makeareadme adds Badges, Visuals, Support, Roadmap, Authors, Project status; take the ones that apply, skip the rest.
- Write for the newest reader. Define or link every term the project invented. Why: the maintainer is not the audience.
- Link, do not duplicate: `CHANGELOG.md` for what changed, `docs/adr/` for why, `docs/` for the long version. Why: two copies drift, one link does not.
- Say the licence in one line and name the file.
- The README changes in the same commit as the command it describes. Why: that is the only moment anyone remembers.
- Two screens at most. If it grows, move the long parts to `docs/` and link them; a `QUICKSTART.md` when the quickstart alone needs a page.

Template:

````
# <name>

<one sentence: what it does, for whom>

## Quickstart

Needs: <tool and version>, <tool>.

```sh
git clone <url> && cd <name>
<install command>
<run command>
```

You should see: `<first line of the output>`.

## Usage

<the two or three commands people run every day, one line each on what it does>

## Project structure

- `<dir>/`: <what lives there>

## Contributing

<branch, test command, style rule>. What changed: CHANGELOG.md. Why: docs/adr/.

## License

MIT, see LICENSE.
````

Sources:
- Make a README, Danny Guo: https://www.makeareadme.com
- GitHub docs, About READMEs (where it must live, what it should say): https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- Tom's doc-doc README and quickstart scaffolds (`readme.md.j2`, `quickstart.md.j2`, private repo): https://github.com/tpetedb/doc-doc
- The live example: `README.md` in this repo
