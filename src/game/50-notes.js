"Tonight":{t:"ws",md:`# Tonight
The evening, in one note. Eight [[Workstreams]], one [[Playbook]], one [[Data warehouse]], one [[Business continuity]] setup, one [[Integration layer]], and this [[Vault]].
- Guide: [[Tom]] · Apprentice: [[Lotte]] · Hospitality: [[Rolinda]]
- The rule: every chapter ends when [[Rolinda's questions]] get a one-sentence answer.
- This is Evening 1 of [[The campaign]]. Mentors: [[Your path]]
- The full roadmap, intern to expert: [[Tech tree]] · Artifacts on the island: [[Artifacts]]
- Written version: [Syllabus](https://claude.ai/artifact/SKSiMuyZHAPQZbZGFj54fG) · Fork the [[Template repo]] · Track it with the [[Terminal companion]] · All links: [[Resources]]
#overview`},
"Workstreams":{t:"ws",md:`# Workstreams
The six hours of the evening, each a note of its own.
- 18:00 [[Innovation Hub]]: ship an MVP
- 19:00 [[Centre of Excellence]]: specificity and the [[Playbook]]
- 20:00 [[Data warehouse]]: persisted scores and a chart
- 21:00 [[Business continuity]]: [[Git]], [[Rollback]] and one [[Hook]]
- 21:30 [[Integration layer]]: [[MCP]] and [[Connectors]]
- 22:00 [[Vault]]: [[Obsidian]] and the [[Graph view]]
- 22:30 [[Go-to-market]]: GitHub and GitHub Pages, a real URL
- 23:00 [[Autonomous operations]]: [[Headless mode]] on a schedule and a [[Subagent]]
Each pairs with a bottle, see [[Beverage stack]].`},
"Innovation Hub":{t:"ws",md:`# Innovation Hub (18:00)
**Goal:** something playable exists before the first glass is empty.
- Open [[Claude Code]] in an empty folder.
- Describe the game in three sentences, out loud first, then typed.
- One guardrail: [[Single-file MVP]], no libraries.
- Play it. Send it to someone.
**Lesson:** none yet, on purpose. First the quick win, then the operating model in [[Centre of Excellence]].
[[Rolinda's questions]]: "So what did you actually do?"
#workstream`},
"Centre of Excellence":{t:"ws",md:`# Centre of Excellence (19:00)
**Goal:** understand that [[Prompt specificity]] is the entire skill.
- Ask for "more impactful". Watch it regress.
- Then one precise change request: what to add, what to keep, what not to touch.
- Codify what you keep repeating into a [[Playbook]]: an [[AGENTS.md]] every agent reads, and [[Skills]] in the [[Agent Skills standard]].
**Lesson:** the agent has no line of sight into your head. What you say every time belongs in a file.
[[Rolinda's questions]]: "Why did 'more impactful' break it?"
#workstream`},
"Data warehouse":{t:"ws",md:`# Data warehouse (20:00)
**Goal:** give the numbers person a reason to care about structure.
- Add score tracking to the game.
- Persist every play to a file (CSV), see [[Schema]].
- Query it with [[DuckDB]]: top runs, per player, streaks with window functions.
- Chart it with [[Python]], standard library only.
**Lesson:** data needs a fixed home and a fixed shape. Move the file or rename a column and the chart breaks. This is where a folder becomes a project.
[[Rolinda's questions]]: "Where do the numbers live?"
#workstream`},
"Business continuity":{t:"ws",md:`# Business continuity (21:00)
**Goal:** lose the fear of breaking things.
- [[Git]] init and a first [[Commit]].
- Make a change, commit. Break it on purpose. [[Rollback]].
- One [[Hook]]: back up the [[Data warehouse]] after every edit.
- Optional: push to GitHub so it exists off the laptop.
**Lesson:** versioning is an undo button for whole evenings. Hooks make things happen without remembering to ask.
[[Rolinda's questions]]: "What happens if you delete it by accident?"
#workstream`},
"Integration layer":{t:"ws",md:`# Integration layer (21:30)
**Goal:** see Claude reach outside the chat window.
- Connect one thing you already use: calendar, files or mail, via [[MCP]] in [[Claude Code]] or [[Connectors]] in the app.
- Ask something that only works with the connection: "what does Thursday look like, draft the 10:00 agenda".
**Lesson:** the chat window is not the boundary. This is the part that changes your work week.
[[Rolinda's questions]]: "Can it see my email now?" Only what you connected, and you can unplug it.
#workstream`},
"Vault":{t:"ws",md:`# Vault (22:00)
**Goal:** end on the prettiest thing, and on long-term memory.
- Open [[Obsidian]], point [[Claude Code]] at the vault folder.
- Have it write a note for tonight, then link notes to each other.
- Open the [[Graph view]]. You are looking at it now.
**Lesson:** memory is files with links. You own them, you can read them without any agent, and they compound. See [[Claude and Obsidian]].
[[Rolinda's questions]]: "Is that a mind map?" Close enough.
#workstream`},
"Go-to-market":{t:"ws",md:`# Go-to-market (22:30)
**Goal:** the game exists somewhere other than the laptop.
- Push the folder to GitHub with [[Claude Code]] and the gh CLI.
- Enable GitHub Pages from the main branch, root folder.
- Open the URL on a phone. Send it to someone who was not here.
**Lesson:** a [[Single-file MVP]] plus [[Git]] plus a static host is a product. No server, no build step.
Docs: [GitHub Pages quickstart](https://docs.github.com/en/pages/quickstart)
[[Rolinda's questions]]: "Can my mother open it on her iPad?"
#workstream`},
"Autonomous operations":{t:"ws",md:`# Autonomous operations (23:00)
**Goal:** a note in the [[Vault]] changes without you at the keyboard.
- Run [[Headless mode]] once by hand: claude -p with a one-job prompt.
- Create a [[Subagent]] that only does that job.
- Schedule it with launchd for 08:00.
**Lesson:** the interactive session is the training wheels. The real leverage is Claude doing one boring job on a timer, forever.
Docs: [headless](https://code.claude.com/docs/en/headless), [subagents](https://code.claude.com/docs/en/sub-agents)
[[Rolinda's questions]]: "So it works while you sleep?"
#workstream`},
"Headless mode":{t:"c",md:`# Headless mode
claude -p "prompt" runs [[Claude Code]] non-interactively: it reads the prompt (and stdin), works in the folder, prints the result, exits. Composable like any command-line tool, so it goes in cron, launchd, CI, webhooks.
- --output-format text or json
- --continue to pick up the last conversation
Used in [[Autonomous operations]].
Docs: [Run Claude Code programmatically](https://code.claude.com/docs/en/headless)
#concept`},
"Subagent":{t:"c",md:`# Subagent
A second Claude the main session delegates to, with its own system prompt, tools and context window. Good for a job you want done the same way every time, like the scorekeeper in [[Autonomous operations]]. Defined as a markdown file with frontmatter in .claude/agents/.
Docs: [Subagents](https://code.claude.com/docs/en/sub-agents)
#concept`},
"AGENTS.md":{t:"c",md:`# AGENTS.md
A plain Markdown file at the root of a repository that tells any AI coding agent how to build, test and change the project. No required fields; usual sections: overview, commands, code style, testing, git rules, security. Read by 30+ agents; stewarded by the Linux Foundation's Agentic AI Foundation.
- [[Claude Code]] reads [[CLAUDE.md]] instead; put \`@AGENTS.md\` on its first line and keep Claude-only extras below.
- The [[Template repo]] ships one. Change a rule, watch every agent follow it.
Docs: [agents.md](https://agents.md)
#concept`},
"Agent Skills standard":{t:"c",md:`# Agent Skills standard
The open format behind [[Skills]]: a folder with a SKILL.md (frontmatter: name, description; then instructions), plus optional scripts and references. Loaded only when relevant, so it costs no context until used.
- Cross-tool folder: \`.agents/skills/\`. Claude Code reads \`.claude/skills/\`; the [[Template repo]] symlinks them.
- Installers: \`npx skills add <repo> --skill <name>\`, \`gh skill install\`.
Docs: [agentskills.io](https://agentskills.io) · [Claude Code skills](https://code.claude.com/docs/en/skills) · [community packs](https://github.com/wshobson/agents)
#concept`},
"DuckDB":{t:"c",md:`# DuckDB
An in-process SQL engine that reads CSV and Parquet files as tables. No server, one binary. The [[Data warehouse]] hour runs on it.
- \`duckdb -c "select * from 'workspace/data/scores.csv' limit 5"\`
- group by for per-player numbers, window functions (\`lag\`, \`row_number\`) for streaks and rankings
Learn SQL: [SQLBolt](https://sqlbolt.com), [Mode](https://mode.com/sql-tutorial/). Docs: [duckdb.org](https://duckdb.org/docs/)
#concept`},
"Python":{t:"c",md:`# Python
Used for the parts SQL is bad at: a script, a chart, a loop over files. The [[Template repo]] has \`workspace/python/scores.py\`, standard library only, one new concept per file.
- The official tutorial: [docs.python.org](https://docs.python.org/3/tutorial/)
- Practice: [Exercism](https://exercism.org/tracks/python), [Kaggle Learn](https://www.kaggle.com/learn)
- Environments and packages: [uv](https://docs.astral.sh/uv/)
#concept`},
"Template repo":{t:"c",md:`# Template repo
A GitHub template you fork with "Use this template". It contains: [[AGENTS.md]], a CLAUDE.md that imports it, five skills in the [[Agent Skills standard]] (Obsidian notes, Mermaid diagrams, [[DuckDB]] SQL, [[Python]] for data, Vibe Code Camp progress), the scorekeeper [[Subagent]], one [[Hook]] that backs up data, the [[Terminal companion]], sample data with tested queries, and a starter [[Vault]].
- \`bash scripts/setup.sh\` installs gh, uv, DuckDB, Obsidian, links the skills, initialises the vault.
Resources: [[Resources]]
#concept`},
"Terminal companion":{t:"c",md:`# Terminal companion
\`uv run vibe\`, standard library only.
- \`status\`: which of the eight are done
- \`done <n> "what I built"\`: marks it and writes the note into the vault
- \`map\`: rebuilds Map.md, a Mermaid flowchart of your progress, green for done
- \`export\` / \`import <code>\`: the same code the game uses under Roadmap
The point: your real progress ends up as real notes and a real diagram in your own vault, not in a browser tab.
#concept`},
"Resources":{t:"p",md:`# Resources
Real, current references. Everything in this vault points here.
- Agent instructions and skills: [agents.md](https://agents.md), [agentskills.io](https://agentskills.io), [Claude Code memory](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills), [community packs](https://github.com/wshobson/agents)
- Claude Code: [quickstart](https://code.claude.com/docs/en/quickstart), [common workflows](https://code.claude.com/docs/en/common-workflows), [hooks](https://code.claude.com/docs/en/hooks-guide), [MCP](https://code.claude.com/docs/en/mcp), [subagents](https://code.claude.com/docs/en/sub-agents), [headless](https://code.claude.com/docs/en/headless), [best practices](https://code.claude.com/docs/en/best-practices)
- SQL and data: [DuckDB docs](https://duckdb.org/docs/), [SQLBolt](https://sqlbolt.com), [Mode SQL tutorial](https://mode.com/sql-tutorial/), [Kaggle Learn](https://www.kaggle.com/learn)
- Python: [official tutorial](https://docs.python.org/3/tutorial/), [Exercism](https://exercism.org/tracks/python), [uv](https://docs.astral.sh/uv/)
- Obsidian and diagrams: [help](https://help.obsidian.md), [links](https://help.obsidian.md/links), [graph view](https://help.obsidian.md/plugins/graph), [Mermaid](https://mermaid.js.org/intro/)
- Shipping: [git tutorial](https://git-scm.com/docs/gittutorial), [GitHub CLI](https://cli.github.com/manual/), [GitHub Pages](https://docs.github.com/en/pages/quickstart)
#people`},
"Claude Code":{t:"c",md:`# Claude Code
The terminal tool that does the building. You describe, it writes files in the folder you opened it in.
- Reads [[CLAUDE.md]] at the start of every session in that folder.
- Loads [[Skills]] when relevant.
- Runs [[Hook]] scripts at lifecycle events.
- Talks to outside systems through [[MCP]].
- Runs unattended in [[Headless mode]] and delegates to a [[Subagent]].
Docs: [overview](https://code.claude.com/docs/en/overview)
#concept`},
"CLAUDE.md":{t:"c",md:`# CLAUDE.md
A markdown file in your project folder that Claude Code reads automatically at the start of every session. Your standing instructions for that project.
- Put your [[Playbook]] rules here: single file, keep scores, one-line summary.
- Lives with the code, so it gets versioned by [[Git]].
Docs: [memory](https://code.claude.com/docs/en/memory)
#concept`},
"Skills":{t:"c",md:`# Skills
Reusable instruction files Claude loads on its own when the task matches. Like a [[CLAUDE.md]] but scoped to a kind of work rather than a folder.
- Example: "how I like my game builds" as a skill, reused across projects.
- The [[Playbook]] from [[Centre of Excellence]] becomes one.
Docs: [skills](https://code.claude.com/docs/en/skills)
#concept`},
"Playbook":{t:"c",md:`# Playbook
The things you keep repeating, written down once:
- single-file architecture, no external dependencies
- laptop-readable
- scores are a system of record, never reset without sign-off
- close every change with a one-line summary
Stored as [[CLAUDE.md]] for one project or as a [[Skills]] file for all of them. Born in [[Centre of Excellence]].
#concept`},
"Prompt specificity":{t:"c",md:`# Prompt specificity
"Make it cooler" gives the agent permission to change anything. "Add a purple badge, keep the stats, touch nothing else" gives it a scope.
- Say what to add.
- Say what to keep.
- Say what not to touch.
Anything you say more than twice goes in the [[Playbook]].
#concept`},
"Single-file MVP":{t:"c",md:`# Single-file MVP
One HTML file, no libraries. Double-click to play, send to anyone, nothing to install.
- Removes the environment problem entirely on night one.
- Makes [[Git]] diffs readable.
- The game itself was built this way, including the 3D campus.
Used in [[Innovation Hub]].
#concept`},
"Schema":{t:"c",md:`# Schema
The fixed shape of your data file: which columns, in which order, with which names.
- The chart in [[Data warehouse]] depends on it.
- Rename a column, break the chart. That is not fragility, that is a contract.
- Versioned with [[Git]] like everything else.
#concept`},
"Git":{t:"c",md:`# Git
Version control. A [[Commit]] is a named snapshot; the history is a list of them; [[Rollback]] takes you back to any one.
- Claude Code can set it up and write the commit messages.
- Push to GitHub and the project exists off the laptop.
Introduced in [[Business continuity]].
#concept`},
"Commit":{t:"c",md:`# Commit
A named, immutable snapshot of the whole folder. You commit after every change you would be sad to lose. See [[Git]] and [[Rollback]].
#concept`},
"Rollback":{t:"c",md:`# Rollback
Going back to an earlier [[Commit]]. The reason [[Business continuity]] exists. Once you have done it once on purpose you stop being afraid of the agent.
#concept`},
"Hook":{t:"c",md:`# Hook
A small script [[Claude Code]] runs automatically at a defined moment, for example after every file edit.
- Not a suggestion. It runs every time.
- Tonight's example: copy the [[Data warehouse]] file to a backup folder.
Docs: [hooks guide](https://code.claude.com/docs/en/hooks-guide)
#concept`},
"MCP":{t:"c",md:`# MCP
Model Context Protocol. An open standard so any tool can plug into Claude the same way. USB, but for tools.
- In [[Claude Code]]: an MCP server for calendar, files, mail, databases.
- In the Claude app the same idea is called [[Connectors]].
Docs: [MCP](https://code.claude.com/docs/en/mcp)
#concept`},
"Connectors":{t:"c",md:`# Connectors
The app-side name for [[MCP]] integrations: Gmail, Google Calendar, Drive and so on, switched on per conversation. Same capability, different door. Used in [[Integration layer]].
#concept`},
"Obsidian":{t:"c",md:`# Obsidian
A note app that stores plain markdown files in a folder. No lock-in, readable by you and by Claude.
- Notes link with double square brackets.
- The [[Graph view]] draws those links.
- Point [[Claude Code]] at the vault folder and it can read and write notes. See [[Claude and Obsidian]].
Site: [obsidian.md](https://obsidian.md)
#concept`},
"Graph view":{t:"c",md:`# Graph view
Every note is a node, every link is an edge. What you are looking at right now, built in [[Single-file MVP]] style. In [[Obsidian]] it is one click. Notes with many links sit in the middle; tonight that is [[Tonight]].
#concept`},
"Claude and Obsidian":{t:"c",md:`# Claude and Obsidian
The long-term memory setup.
- The vault is a folder of markdown, so [[Claude Code]] can open it like any project.
- Put a [[CLAUDE.md]] in the vault root: "one note per topic, link generously, date the entries".
- After a session: "write a note about what we built tonight and link it to the relevant notes."
- Next week Claude reads the vault before starting, so it remembers what you decided.
Memory is files with links. See [[Vault]].
#concept`},
"Rolinda's questions":{t:"p",md:`# Rolinda's questions
The check at the end of every workstream. Explain it to [[Rolinda]] in one sentence without saying "AI".
- Innovation Hub: "So what did you actually do?"
- Centre of Excellence: "Why did 'more impactful' break it?"
- Data warehouse: "Where do the numbers live?"
- Business continuity: "What happens if you delete it by accident?"
- Integration layer: "Can it see my email now?"
- Vault: "Is that a mind map?"
If she nods, done. If she frowns, not done.
#people`},
"Lotte":{t:"p",md:`# Lotte
Chief of Staff. Apprentice for the evening, owner of the campus and of this vault. Likes fantasy games and spreadsheets, which is why the [[Data warehouse]] hour exists. See [[Tonight]].
#people`},
"Tom":{t:"p",md:`# Tom
Site Reliability Engineer and Executive Sponsor. Guide for the evening, on call during [[Business continuity]], available for one panicked message per week afterwards.
#people`},
"Rolinda":{t:"p",md:`# Rolinda
Head of Hospitality Operations. Knows nothing about AI, which makes her the most useful person in the room; see [[Rolinda's questions]]. Insufferable on the subject of wine; see [[Beverage stack]].
#people`},
"Beverage stack":{t:"p",md:`# Beverage stack
Rolinda's pairings, one per workstream.
- 18:00 Bourgogne Chardonnay, 11°C, "lekker arrogant aan de wang hangt en goed tegen de huig galoppeert", gougères
- 19:00 same bottle, opening up, Marcona almonds
- 20:00 Sancerre, chalky finish, chèvre by ash content
- 21:00 Barolo, decanted 19:30, bureaucratic tannins, charcuterie
- 21:30 Grüner Veltliner, peppery, cross-functional, truffle crisps
- 22:00 grower Champagne, zero dosage, 72% chocolate
- 22:30 Tokaji Aszú, 5 puttonyos, Roquefort
- 23:00 Armagnac 1998, last orders
Ties to [[Workstreams]].
#people`}
};
