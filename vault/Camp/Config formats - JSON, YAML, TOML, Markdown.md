---
title: "Config formats: JSON, YAML, TOML, Markdown"
date: 2026-09-16
tags: [tech, dark]
---
# Config formats: JSON, YAML, TOML, Markdown

Tools read settings from text files in a few formats. JSON: strict, braces, what APIs speak. YAML: indentation, what CI and Docker Compose use. TOML: sections, what Python packaging uses. Markdown: prose with light structure, what agents and Obsidian read.

**History.** JSON was first presented at json.org by Douglas Crockford in 2001; YAML began in 2001 (1.0 spec in 2004); Markdown by John Gruber in 2004; TOML by Tom Preston-Werner in 2013. Agents made Markdown the config format for instructions (AGENTS.md, SKILL.md) because it is readable by both people and models.

**Try in five minutes.** Open .claude/settings.json (JSON) and .agents/skills/duckdb-sql/SKILL.md (Markdown with YAML frontmatter). Spot the three formats in one repo.

- Docs: [JSON](https://www.json.org/json-en.html), [YAML](https://yaml.org/spec/1.2.2/), [TOML](https://toml.io), [Markdown](https://daringfireball.net/projects/markdown/), [Source: ECMA-404, The JSON data interchange syntax (2nd edition)](https://ecma-international.org/wp-content/uploads/ECMA-404_2nd_edition_december_2017.pdf), [Source: YAML 1.0 specification (2004)](https://yaml.org/spec/1.0/), [Source: Markdown 1.0.1 (December 2004)](https://daringfireball.net/projects/markdown/), [Source: TOML v0.1.0 release (March 2013)](https://github.com/toml-lang/toml/releases/tag/v0.1.0)
- Unlocks: [[.env files and secrets]], [[YAML in practice - CI and Compose]], [[TOML in practice - pyproject.toml]], [[AGENTS.md]], [[Skills (Agent Skills standard)]]
- Age: Dark Age · Level: Intern

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #dark
