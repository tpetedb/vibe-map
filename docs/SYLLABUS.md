# Vibe Code Camp: the syllabus

Four evenings, thirty-two stops, one glass per stop. Evening 1 is the core; Evenings 2 to 4 go into history, how the models work, determinism, and the terminal. Optimised for a MacBook with Apple silicon and Chrome. This is the written version of everything in the game, with every command, so the parts we do not reach on the night can be done alone. Cast: Lotte (Chief of Staff, apprentice), Tom (Site Reliability Engineer, guide), Rolinda (Head of Hospitality Operations, sommelier, and the only person allowed to ask plain questions).

## The rule of the evening

Every workstream ends the same way: Lotte explains what just happened to Rolinda in one sentence without the word "AI". If Rolinda nods, it is done.

## The pairings

18:00 Bourgogne Chardonnay, unoaked, 11°C, gougères. 19:00 same bottle opening up, Marcona almonds. 20:00 Sancerre, chèvre by ash content. 21:00 Barolo decanted at 19:30, charcuterie. 21:30 Grüner Veltliner, truffle crisps. 22:00 grower Champagne, zero dosage, 72% chocolate. 22:30 Tokaji Aszú with Roquefort. 23:00 Armagnac, last orders. Rolinda's note on the Chardonnay, verbatim: "lekker arrogant aan de wang hangt en goed tegen de huig galoppeert."

## Before the evening: Pre-flight: set up the machine

Twenty minutes, alone, before the night. Everything here is boring on purpose so the evening itself is not.

### 1. Install Claude Code

Open Terminal (Cmd+Space, type Terminal). Paste this and press Enter. It installs the native build, which updates itself in the background:

```
curl -fsSL https://claude.ai/install.sh | bash
```

Then confirm it worked. It should print a version number followed by (Claude Code):

```
claude --version
```

### 2. Log in

Start it once. Your browser opens, you sign in with your Claude account (Pro, Max, Team or Enterprise), and the credentials are stored. You will not be asked again.

```
claude
```

Type /exit to leave. If you ever need to switch accounts, type /login inside a session.

### 3. Install git and jq

git is the save-point system for workstream 4, jq is a tiny helper the hook uses. On a Mac:

```
xcode-select --install
brew install jq
```

If brew is not installed, the first line still gives you git; ask Claude to install Homebrew for you on the night, it takes two minutes.

### 4. Install Obsidian

Download from obsidian.md, open it once, close it. Do not create anything yet.

### 5. Think of a game

One small game you would enjoy having on your laptop. A card duel, a dungeon room, a scoring board that ranks the team by coffee consumption. Three sentences, in your head.

**Definition of done.** Terminal shows a version for claude --version, and git --version prints something. That is the whole pre-flight.

Sources: [Claude Code quickstart](https://code.claude.com/docs/en/quickstart), [Obsidian](https://obsidian.md)

## 18:00: Ship an MVP

The goal of this hour is one thing: a playable game exists before the Chardonnay warms up. We explain almost nothing. That is the design.

### Concept: the agentic loop

Claude Code is not a chat box. You give it a goal in plain language, it reads and writes files in the folder you started it in, runs commands, looks at the result, and keeps going until the goal is met. The folder you start it in is its whole world, so start it in an empty one.

### Do this

1. Make a folder and step into it:
   ```
   mkdir -p ~/vibe && cd ~/vibe
   ```
2. Start Claude Code:
   ```
   claude
   ```
3. On Pro and Max plans the session starts in auto mode: Claude edits files and runs most commands without asking each time, and a classifier reviews risky actions. Press Shift+Tab at any time to cycle to a mode that asks first. Tonight, auto is fine.
4. Say your three sentences out loud to Tom first. Then type them, with the one guardrail added. A template:
   ```
   Build a small browser game as a single file called index.html, no external libraries, no frameworks. The game: [your three sentences]. Keep score. When done, tell me how to open it.
   ```
5. When it says it is done, open the file:
   ```
   open index.html
   ```
6. Play it. Send it to someone. That is the OKR.

### One more thing, then stop

Ask for exactly one change, in one sentence, and watch it land. Then leave it alone. The next hour is about why that worked or did not.

**Definition of done.** index.html exists in ~/vibe, it opens in a browser, and you can play it. If Claude asked a permission question you did not understand, answer yes and tell Tom; understanding permissions is workstream 4.

**Why it matters.** You now know the loop: describe, wait, look, adjust. Everything after this is about making the loop reliable instead of lucky.

**Try this.** If the first result is broken, do not fix it yourself. Paste the error, or describe what you see, and let it iterate. Say what is wrong, not how to fix it.

Sources: [Quickstart](https://code.claude.com/docs/en/quickstart), [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)

## 19:00: Specificity, CLAUDE.md and your first skill

This is the hour that separates people who vibe code from people who got lucky once.

### Concept 1: the model has no line of sight into your head

It only has what is in the folder and what you typed. "Make it more impactful" is a request it will fulfil according to its own idea of impact. "Give the mascot a purple badge, keep the stats, do not touch the score" has a scope, a keep-list and a do-not-touch list. That is the entire craft.

### Do this: break it, then fix it

1. Ask for the vague thing and watch what happens:
   ```
   make it more impactful
   ```
2. Now ask for one precise thing. State what to add, what to keep, what not to touch:
   ```
   Add a purple badge to the main character. Keep all stats and the score exactly as they are. Do not change anything else. Reply with one line describing what you changed.
   ```
3. Compare. The second one is a change request. The first was a mood.

### Concept 2: CLAUDE.md, the note it reads every session

Every session starts with a blank memory. CLAUDE.md is a plain markdown file in your project folder that Claude reads at the start of every session. It is where you write down what you would otherwise re-explain: build commands, conventions, "always do X" rules. Target under 200 lines, concrete enough to verify. "Keep it one file" beats "keep it simple".

1. Let Claude draft one from what it sees in the folder:
   ```
   /init
   ```
2. Then add your own rules. Ask Claude to add them, or open the file yourself with /memory. A good starting set:
   ```
   # Rules for this project
   - Single file: index.html only, no external libraries
   - Readable on a laptop, minimum font size 14px
   - Scores are a system of record: never reset or reformat stored scores without asking
   - After every change, reply with one line saying what changed
   ```
3. Confirm it loaded. Start a new session and run:
   ```
   /context
   ```
4. Your CLAUDE.md should be listed under Memory files. If it is not there, Claude cannot see it.

### Concept 3: skills, procedures that load on demand

CLAUDE.md is for facts that apply every session. A skill is a folder with a SKILL.md for a repeatable procedure, loaded only when it is relevant or when you type /skill-name. Personal skills live in ~/.claude/skills/ and work in every project.

1. Create one for adding features to your game:
   ```
   mkdir -p ~/.claude/skills/add-feature
   ```
2. Ask Claude to write ~/.claude/skills/add-feature/SKILL.md with this content, or paste it yourself:
   ```
   ---
   description: Add a feature to the game safely. Use when the user asks to add, change or extend gameplay.
   ---
   
   When adding a feature:
   1. Restate the request in one sentence and list what will NOT change.
   2. Make the change in index.html only.
   3. Open index.html and check it still loads without console errors.
   4. Reply with one line: what changed, and one sentence: what to test.
   ```
3. Use it:
   ```
   /add-feature give the enemy a health bar
   ```
4. Or just ask normally. Claude loads it automatically when the description matches.

### Bonus: auto memory

If you tell Claude "remember that I prefer British spelling", it saves that to its own notes for this project and loads them next time. Run /memory to see and edit everything it has saved. Everything is plain markdown you can delete.

**Definition of done.** /context lists your CLAUDE.md. /add-feature appears when you type / in a session. A vague prompt now gets a clarifying question or a scoped change instead of a rewrite.

**Why it matters.** CLAUDE.md for what is always true, skills for how to do a thing, your prompt for what to do right now. Once those three are separated you stop re-onboarding the agent every evening.

**Try this.** Rolinda's test: read your CLAUDE.md to her. Every line she can verify ("is it one file? yes/no") is a good line. Every line she has to interpret is a bad one.

Sources: [How Claude remembers your project](https://code.claude.com/docs/en/memory), [Skills](https://code.claude.com/docs/en/skills), [Best practices](https://code.claude.com/docs/en/best-practices)

## 20:00: Persisted scores and a dashboard

Time to feed the spreadsheet person. The game learns to remember, the data gets a home, and the home turns out to matter more than the game.

### Concept: a fixed home and a fixed shape

A browser page cannot write files to your disk on its own, so the pattern is: the game stores every finished round in the browser (localStorage), and offers an Export button that downloads a CSV. Once that CSV has a fixed name and fixed columns, anything can be built on top of it. Rename one column and everything downstream breaks. That is not a bug, that is what a schema is.

### Do this

1. Add persistence with an explicit schema:
   ```
   Every time a round ends, save a record to localStorage with exactly these fields: played_at (ISO timestamp), player (string), score (integer), duration_s (integer). Add an "Export CSV" button that downloads all records as scores.csv with those four columns in that order and a header row. Do not change gameplay.
   ```
2. Play three rounds, export, and move the file to the one place the check looks (from your camp folder):
   ```
   mv ~/Downloads/scores.csv workspace/data/scores.csv
   head -1 workspace/data/scores.csv
   ```
   That header line must read `played_at,player,score,duration_s`, exactly.
3. Now ask for analysis on top of the file, not the game:
   ```
   Write workspace/python/analyze.py that reads workspace/data/scores.csv, prints number of rounds, mean score, best score, longest streak of improving scores, and saves a bar chart of score per round to chart.png. Use only the Python standard library plus matplotlib. Then run it.
   ```
4. Open the chart:
   ```
   open chart.png
   ```
5. Break the schema on purpose. Rename the score column in `workspace/data/scores.csv` to points, run analyze.py again, watch it fail. Rename it back.

### What Lotte will notice

The game is now a front end. The CSV is the thing. Any spreadsheet, script or chart can read it, and Claude can build the next one in a minute because the shape is known. This is the same idea as a table in a database: the columns are a contract.

**Definition of done.** `workspace/data/scores.csv` has the header row `played_at,player,score,duration_s` and at least three rows. There is a query in `workspace/sql/` and a script in `workspace/python/` that read it. `uv run vibe check 3` is green.

**Why it matters.** Every useful tool you build for work will be this pattern: something produces a file with a fixed shape, something else reads it. Meeting notes to action list, calendar export to weekly summary. Learn to name the columns first.

**Try this.** Add a fifth column, difficulty, in both the game and the script, in one prompt. Notice you have to say both places.

Sources: [Common workflows](https://code.claude.com/docs/en/common-workflows)

## 21:00: Git, rollback, and one hook

Fear of breaking things is what stops people from experimenting. This hour removes the fear.

### Concept 1: commits are named snapshots

git keeps a history of your folder. A commit is a snapshot with a message. You can look at old ones, compare them, and go back. Claude Code makes this conversational, you never have to memorise commands.

1. Turn the folder into a repository and take the first snapshot:
   ```
   initialise git in this folder, add a .gitignore that excludes backups/ and .DS_Store, and commit everything with the message "first playable"
   ```
2. Make a change (any feature), then:
   ```
   commit my changes with a descriptive message
   ```
3. Look at the history:
   ```
   show me the last 5 commits
   ```
4. Now break it on purpose. Ask for something destructive: "replace all text in the game with Comic Sans and remove the score". Confirm it is ruined.
5. Roll back:
   ```
   discard all uncommitted changes and restore the last commit
   ```
6. Open index.html. It is fine again. Tom can stop pretending to be paged.

### Concept 2: two undo buttons

Inside a session, Claude Code also keeps its own checkpoints: /rewind takes the files back to an earlier point in the conversation. That is for "the last ten minutes went wrong". git is for "I want this to survive closing the laptop". Use both.

### Concept 3: hooks, things that happen every time

CLAUDE.md is advice. Claude reads it and tries. A hook is a shell command Claude Code runs at a fixed moment in its lifecycle, whether Claude wants to or not. PostToolUse fires after a tool ran, PreToolUse fires before and can block. Hooks live in a settings file, and the /hooks menu shows what is registered.

1. Create the project settings file. Ask Claude, or write .claude/settings.json yourself:
   ```
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Edit|Write",
           "hooks": [
             {
               "type": "command",
               "command": "mkdir -p backups && cp scores.csv backups/scores-$(date +%Y%m%d-%H%M%S).csv 2>/dev/null || true"
             }
           ]
         }
       ]
     }
   }
   ```
2. The matcher means: only after the Edit or Write tools. The command copies scores.csv into backups/ with a timestamp, and the || true means a missing file does not count as an error.
3. Check it registered:
   ```
   /hooks
   ```
4. Ask Claude to edit any file. Then look in backups/. A copy appeared without anyone asking for it.
5. The other kind: a hook that blocks. Ask Claude to add a PreToolUse hook that refuses any Edit or Write to scores.csv, exits with code 2 and prints a reason. Then ask it to edit scores.csv and watch it get refused and explain why.

### Optional, if the Barolo allows

Put the folder somewhere other than the laptop: "create a private GitHub repository for this project and push it". Claude will ask you to sign in to GitHub the first time.

**Definition of done.** git log shows at least three commits. Ruining and restoring works. /hooks lists your PostToolUse hook and backups/ fills up when files change.

**Why it matters.** Advice can be ignored, enforcement cannot. When something must happen every single time, it is a hook, not a sentence in CLAUDE.md. And with git underneath, no experiment is expensive.

**Try this.** Ask Claude to add a Notification hook that shows a macOS notification when it needs your input, so you can walk to the kitchen while it works.

Sources: [Hooks guide](https://code.claude.com/docs/en/hooks-guide), [Checkpointing and /rewind](https://code.claude.com/docs/en/checkpointing), [Quickstart: git section](https://code.claude.com/docs/en/quickstart)

## 21:30: Connectors and MCP

Until now Claude could only see the folder. This hour it reaches your calendar, your files, your mail. This is the part that quietly changes a work week.

### Concept: MCP is the plug

The Model Context Protocol is an open standard for giving an AI model tools. An MCP server is a program or a hosted service that exposes tools: search an issue tracker, read a calendar, drive a browser. Claude Code connects to servers; the Claude app calls the same thing connectors. Same idea, different door.

### Do this: a server that needs no account

1. From your shell, not inside a session, add the Claude Code documentation server. The name claude-code-docs is one you choose:
   ```
   claude mcp add --transport http claude-code-docs https://code.claude.com/docs/mcp
   ```
2. Check it connected:
   ```
   claude mcp list
   ```
3. Start a session and force it through the new server so you can see it happen:
   ```
   Use the claude-code-docs server to look up what a PostToolUse hook is
   ```
4. The tool call in the output is labelled with the server name. That label is how you know it went out, not from memory.

### Scopes: where it is saved

By default the server is local: only you, only this project. Add --scope user to have it in every project, or --scope project to write it to .mcp.json in the folder so anyone who clones the project gets it too. Inside a session, /mcp shows the panel and lets you authenticate or reconnect.

### Do this: something you actually use

1. Connectors you add at claude.ai (Settings, Connectors) load automatically in Claude Code when you are signed in with the same account. Connect Google Calendar or Google Drive there.
2. Or, for a hosted service with a sign-in, add it and authenticate in the /mcp panel:
   ```
   claude mcp add --transport http notion https://mcp.notion.com/mcp
   # then inside a session: /mcp → notion → Authenticate
   ```
3. Then ask something only the connection can answer:
   ```
   What is on my calendar Thursday? Draft an agenda for the 10:00 as a markdown file called thursday-agenda.md
   ```
4. When done experimenting, unplug what you do not need. Every connected server uses some of Claude's context window:
   ```
   claude mcp remove claude-code-docs
   ```

**Definition of done.** claude mcp list shows at least one Connected server. A prompt that needs it produces a tool call labelled with the server name.

**Why it matters.** The chat window is not the boundary. Once Claude can read the systems your work lives in, the tools you build stop being toys: a meeting note to action list, a week of calendar to a summary, a thread to three decisions.

**Try this.** Rolinda's question, answered properly: it can only see what you connected, only while it is connected, and claude mcp remove unplugs it. Say that sentence back to her.

Sources: [Connect to MCP servers](https://code.claude.com/docs/en/mcp-quickstart), [MCP reference](https://code.claude.com/docs/en/mcp)

## 22:00: Obsidian and the graph

The last hour is the prettiest, and the one that gives everything before it a place to live.

### Concept: a vault is a folder of markdown, links are just text

An Obsidian vault is a normal folder on disk. Every note is a .md file. A link from one note to another is the text [[Note name]]. The graph view draws a circle per note and a line per link; the more notes point at a note, the bigger it gets. Because it is all plain files, Claude can read and write the vault directly, and you can read it without any AI at all.

### Do this

1. In Obsidian: bottom left, Vault profile, Manage vaults, Create new vault. Name it vibe-vault, put it in your home folder.
2. Start Claude Code inside the vault:
   ```
   cd ~/vibe-vault && claude
   ```
3. Give it the conventions once, as a CLAUDE.md in the vault root:
   ```
   Create CLAUDE.md with these rules: every note is markdown; link related notes with [[wikilinks]]; each note starts with a one-line summary; project notes live in Projects/, people in People/, tools in Tools/.
   ```
4. Now capture tonight:
   ```
   Create Projects/Vibe Code Camp game.md summarising what we built tonight (single-file game, scores.csv schema, git, hooks). Create Tools/Claude Code.md, Tools/CLAUDE.md and skills.md, Tools/Hooks.md, Tools/MCP.md, Tools/Obsidian.md, each with a short explanation in my words and a "how to" section. Create People/Tom.md and People/Rolinda.md. Link everything that is related with [[wikilinks]] and make sure every note links to at least two others.
   ```
5. Open the graph: click the graph icon in the left ribbon, or Cmd+P and type "graph". Hover a node to highlight its links. Click one to open it.
6. Local graph: with a note open, Cmd+P, "Open local graph", to see only what connects to that note.
7. Colour it: graph settings (cog top right), Groups, New group, search path:Tools, pick a colour. Do the same for Projects and People.

### This is your long-term memory

Next week, when Lotte builds the meeting-note tool, she starts Claude Code in the vault, and it can read Tools/Hooks.md to remember how she likes hooks written. Every project adds notes, every note adds links, the graph grows. Nothing is locked in: it is a folder of text files she owns. Put the vault in git too, and ignore the .obsidian folder.

**Definition of done.** The graph shows at least ten nodes in three colours, and clicking any node opens a note Claude wrote that reads like Lotte, not like a manual.

**Why it matters.** Memory is files with links. You own it, it compounds, and both you and the agent can read it. That is the whole knowledge moat, and it cost one prompt.

**Try this.** Ask Claude, inside the vault: "what did we decide about scores?" and watch it find the answer by reading the notes, not by remembering.

Sources: [Obsidian: graph view](https://help.obsidian.md/plugins/graph), [Obsidian: internal links](https://help.obsidian.md/links), [Obsidian: manage vaults](https://help.obsidian.md/manage-vaults)

## 22:30: GitHub and GitHub Pages, a real URL

The goal: the game exists somewhere other than your laptop, at an address you can send to anyone.

### Concept: remote and static hosting

A remote is a copy of your git history on GitHub. GitHub Pages serves the files in a repository as a website. A single-file game needs nothing else: no server, no build step. Claude Code can do every step from the terminal using the GitHub CLI.

### Do this

1. Install the GitHub CLI and log in:
   ```
   brew install gh && gh auth login
   ```
2. In Claude Code: "create a public GitHub repo called vibe from this folder and push it."
3. Then: "enable GitHub Pages for this repo from the main branch, root folder, and tell me the URL." If Claude cannot flip the setting, open the repo on github.com, Settings, Pages, choose main and root, save.
4. Open the URL on your phone. Send it to someone who was not there.

Definition of done: the game loads on a device that is not your laptop.

Rolinda's question: "Can my mother open it on her iPad?"

Pairing: Tokaji Aszú, 5 puttonyos, Roquefort.

Docs: https://docs.github.com/en/pages/quickstart · https://cli.github.com/manual/gh_repo_create · https://code.claude.com/docs/en/common-workflows

## 23:00: Headless Claude on a schedule, and a subagent

The goal: a note in your vault changes without you at the keyboard.

### Concept: headless mode and subagents

`claude -p "prompt"` runs Claude Code non-interactively: it takes the prompt, works in the folder, prints the result, exits. That makes it composable like any command-line tool, so it can run from launchd, cron, CI or a webhook. A subagent is a second Claude the first one delegates to, with its own instructions and context, defined as a markdown file in `.claude/agents/`. Use it for a job you want done the same way every time.

### Do this

1. From the project folder, once by hand:
   ```
   claude -p "read workspace/data/scores.csv and append a one-paragraph summary of tonight's best runs to vault/Camp/Scores.md"
   ```
2. In Claude Code: "create a subagent called scorekeeper that only does that job, and document it in the vault."
3. Then: "schedule the scorekeeper to run every morning at 08:00 with launchd." Read the plist it writes; it should call `claude -p` with `--output-format text`. Load it with `launchctl load`.
4. Tomorrow morning: open the vault. The note updated itself.

Definition of done: a vault note changed while you slept.

Rolinda's question: "So it works while you sleep?"

Pairing: Armagnac, last orders.

Docs: https://code.claude.com/docs/en/headless · https://code.claude.com/docs/en/sub-agents · https://code.claude.com/docs/en/cli-reference

## Provider-agnostic instructions: AGENTS.md and the Agent Skills standard

Two open standards keep your setup portable. AGENTS.md is a plain Markdown file at the repo root that tells any coding agent how to build, test and change the project; 30+ agents read it (Codex, Cursor, Copilot, Gemini CLI, Aider, Zed) and it is stewarded by the Linux Foundation's Agentic AI Foundation: https://agents.md. Claude Code reads CLAUDE.md, so make CLAUDE.md one line, `@AGENTS.md`, and keep Claude-only extras (hooks, subagents) below it: https://code.claude.com/docs/en/memory.

Agent Skills is the open format behind skills: a folder with a SKILL.md (name, description, instructions), loaded only when relevant: https://agentskills.io. The cross-tool folder is `.agents/skills/`; Claude Code reads `.claude/skills/`, so the template symlinks them. Community packs: https://github.com/wshobson/agents.

## The template repo and the terminal companion

Fork the template with "Use this template" on GitHub. It ships AGENTS.md, a one-line CLAUDE.md, five skills (Obsidian notes, Mermaid diagrams, DuckDB SQL, Python for data, Vibe Code Camp progress), the scorekeeper subagent, a data-backup hook, sample scores with tested DuckDB queries, a starter vault, and `vibemap/cli.py`.

```
bash scripts/setup.sh                 # gh, uv, DuckDB, Obsidian, skill links, vault
uv run vibe status        # which of the eight are done
uv run vibe done 1 "shipped the coffee scoreboard"
uv run vibe map           # Mermaid progress map in vault/Camp/Map.md
uv run vibe export        # code to paste into the game (Roadmap, Import)
```

## SQL and Python, in the 20:00 hour

The data hour now runs on DuckDB (https://duckdb.org/docs/), which reads a CSV as a table with no server. Run `workspace/sql/top_runs.sql`, then `workspace/sql/per_player.sql` (group by), then `workspace/sql/streaks.sql` (window functions, `lag()`), then `python3 workspace/python/scores.py`. Zero-to-SQL: https://sqlbolt.com. Analytics SQL: https://mode.com/sql-tutorial/. Python: https://docs.python.org/3/tutorial/ and https://exercism.org/tracks/python.

## The campaign: four evenings, four islands

Evening 1 is the eight workstreams above. Evenings 2 to 4 are below, one island each in the game. Split them over as many nights as you like; the game, the CLI and the vault keep the state. Mentors (real people from the field) stand on the islands; talking to them and choosing "tell me more" or "not now" builds your path, which the CLI writes into the vault.

### Evening 2: History, and how these models actually work

Cold storage: the archive. Eighty years in eight stops, with the people who did it.

#### Stop 1: Neurons and backprop (1943 to 1989)

_McCulloch-Pitts, Rosenblatt, Rumelhart-Hinton-Williams, LeCun's zip codes_

Everything you use tonight descends from three ideas. In 1943 McCulloch and Pitts described a neuron as a threshold that sums its inputs. In 1958 Rosenblatt built one (the perceptron) and it learned to classify. It stalled for two decades because one layer cannot learn XOR, and nobody knew how to train more layers. In 1986 Rumelhart, Hinton and Williams popularised backpropagation: compute the error at the output, push it backwards through the layers, nudge every weight a little in the direction that reduces it. In 1989 LeCun applied it to real data: handwritten zip codes for the US Postal Service, with a convolutional network. That paper is small enough to reproduce on a laptop in an afternoon, and Karpathy did.

The concept that survives to today: a model is a pile of numbers (weights), a loss function says how wrong it is, and gradient descent changes the numbers to be less wrong. Nothing you will meet later changes this; it only gets bigger.

Do this:
1. Watch the first 40 minutes of Karpathy's micrograd lecture: a working backprop engine in 100 lines of Python.
2. Ask Claude Code: "reproduce LeCun 1989 in a notebook using Karpathy's repo as reference, and explain each cell in one line".
3. Write one vault note: what a weight is, what a loss is, what a gradient is. Three sentences.
4. Talk to Hinton and LeCun on this island.

Sources: [Rumelhart, Hinton, Williams 1986 (Nature)](https://www.nature.com/articles/323533a0) · [Karpathy's lecun1989 reproduction](https://github.com/karpathy/lecun1989-repro) · [micrograd lecture, Zero to Hero](https://karpathy.ai/zero-to-hero.html)

Rolinda's question: "So it is just numbers being adjusted until they stop being wrong?"

#### Stop 2: The ImageNet moment (2012)

_Fei-Fei Li's dataset, AlexNet, and why GPUs mattered_

By 2010 the ideas were 20 years old and the field had moved on. What changed was data and hardware. Fei-Fei Li's group built ImageNet: 14 million labelled images, and a yearly competition. In 2012 Krizhevsky, Sutskever and Hinton entered a deep convolutional net trained on two gaming GPUs and beat every other entry by a margin nobody had seen. The paper is AlexNet. Within two years every entry was a neural net, and the same three ingredients (big data, parallel hardware, gradient descent) became the recipe for everything since, including language.

Why it matters for you: the reason your MacBook can run a decent language model today is that the whole stack, from chips to frameworks, was rebuilt around this recipe. Apple silicon's unified memory is why a 7B model fits on a laptop at all.

Do this:
1. Read the AlexNet abstract and the first figure. Ask Claude: "explain the two-GPU split in this figure as if I run a hotel".
2. Open Apple's Activity Monitor, GPU tab, then run a small local model (Stop 6) and watch the GPU light up. That is the same idea, 14 years later.
3. Talk to Fei-Fei Li here.

Sources: [AlexNet paper (NeurIPS 2012)](https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html) · [ImageNet](https://www.image-net.org) · [Karpathy on being the ImageNet reference human](https://karpathy.ai/)

Rolinda's question: "Why did it need a competition? Could nobody just say it worked?"

#### Stop 3: Attention Is All You Need (2017)

_Tokens, embeddings, attention, next-token prediction: the transformer, without hand-waving_

A language model does one thing: given the text so far, predict a probability for every possible next token. A token is a chunk of text (roughly three quarters of a word). Each token becomes a vector of numbers (an embedding). The transformer's trick, from Vaswani and colleagues at Google in 2017, is attention: every position looks at every other position and decides how much to weigh it, in parallel, on a GPU. Stack that 30 to 100 times, train on trillions of tokens to predict the next one, and you get a base model. Chat happens later (Stop 5). Everything you type to Claude is tokenised, attended over, and answered one token at a time; that is why long context costs money and why the model can lose the thread.

Deterministic or not: the forward pass is deterministic. Sampling the next token from the probabilities is where randomness enters (temperature). This is why the same prompt gives different answers, and why Evening 3 is about putting checks around the output rather than hoping.

Do this:
1. Watch Karpathy's "Let's build GPT" (2h, worth it) or the general-audience "Deep dive into LLMs" on his channel.
2. Paste a paragraph into a tokenizer and count: ask Claude "how many tokens is this and why does 'Rolinda' split into pieces".
3. Ask Claude to draw the transformer block as a Mermaid diagram in your vault (the mermaid skill will do it).

Sources: [Attention Is All You Need (arXiv)](https://arxiv.org/abs/1706.03762) · [Let's build GPT, Zero to Hero](https://karpathy.ai/zero-to-hero.html) · [Karpathy's channel (general audience track)](https://www.youtube.com/@AndrejKarpathy)

Rolinda's question: "So it never knows what it is going to say, only what is likely next?"

#### Stop 4: Scaling laws and the Bitter Lesson

_Why bigger kept winning, and why the Claude Code team framed Sutton's essay_

In 2019 Rich Sutton wrote a one-page essay: seventy years of AI show that methods which leverage computation (search, learning) beat methods that leverage human cleverness, every time, in the long run. In 2020 Kaplan, Amodei and colleagues measured it: loss falls as a smooth power law in model size, data and compute. Those two documents explain the last six years: labs bought compute and let the model do the work. The Claude Code team keeps a framed copy of the Bitter Lesson on the wall and says it out loud: never bet against the model, build for the model six months from now.

What it means for your workflow: elaborate scaffolding around a model tends to become debt when the next model arrives. Keep your setup thin: instructions, checks, memory. That is the whole design of the template repo.

Do this:
1. Read the Bitter Lesson. It is one page. Write two sentences in the vault about what it implies for your AGENTS.md.
2. Skim the scaling-laws paper's figure 1. Ask Claude: "what is a power law, and why does a straight line on a log-log plot matter".
3. Talk to Sutton and Amodei on this island.

Sources: [The Bitter Lesson (Sutton, 2019)](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) · [Scaling Laws for Neural Language Models (Kaplan et al. 2020)](https://arxiv.org/abs/2001.08361) · [How the Claude Code team works (Cherny interview notes)](https://engineeredintelligence.substack.com/p/how-the-claude-code-team-works)

Rolinda's question: "If bigger always wins, why do you keep telling me to write rules for it?"

#### Stop 5: From base model to assistant

_Pretraining, supervised fine-tuning, RLHF, and Constitutional AI_

A base model completes text; it will happily continue a forum post with a worse forum post. Turning it into an assistant takes three more steps. Supervised fine-tuning: show it thousands of good question-answer pairs. Reinforcement learning from human feedback: humans rank answers, a reward model learns the ranking, the model is optimised against it. Anthropic added Constitutional AI: instead of only human rankings, the model critiques and revises its own answers against a written list of principles, which is cheaper, more transparent, and where the word "constitution" in Claude's system comes from. Anthropic's Core Views page explains why they think this ordering (capability, then alignment work in the open) is the responsible bet.

Why you should care: the assistant behaviour you rely on is trained, not programmed. It is a distribution, not a rule engine. Rules you write (AGENTS.md, hooks) are how you add the rule engine back on top.

Do this:
1. Read the Constitutional AI abstract and the Core Views page.
2. Ask Claude: "show me a prompt where a base model and an assistant model would diverge", then reflect on which one you would want in a hook.
3. Talk to Dario Amodei here.

Sources: [Constitutional AI (Bai et al. 2022)](https://arxiv.org/abs/2212.08073) · [Core Views on AI Safety (Anthropic)](https://www.anthropic.com/news/core-views-on-ai-safety) · [Training language models to follow instructions (InstructGPT, 2022)](https://arxiv.org/abs/2203.02155)

Rolinda's question: "So somebody wrote down rules it argues with itself about?"

#### Stop 6: Open weights versus closed models, on your own Mac

_Licences, Llama, Mistral, Qwen, Gemma; run a local model with Ollama on Apple silicon_

"Open source" is doing a lot of work in this field. Most open models are open weights: you can download the numbers and run them, but the training data and code are not published and the licence may restrict use (Llama's is not OSI-approved; Mistral and Qwen ship Apache-2.0 models; Gemma has its own terms). Closed models (Claude, GPT, Gemini) are API-only and generally stronger at the frontier. LeCun is the loudest voice for open weights; Anthropic's position is that frontier models need controlled release. Both positions have serious arguments; you should be able to state each.

On your MacBook: Apple silicon shares memory between CPU and GPU, so a 7 to 8 billion parameter model in 4-bit runs comfortably on 16 GB. Ollama makes it one command. Once it runs, you can point OpenCode or any AGENTS.md-aware agent at it and see what the gap to a frontier model feels like in practice.

Do this:
1. brew install ollama && ollama run llama3.2 (or qwen2.5:7b). Ask it the same three questions you asked Claude today. Note the differences in the vault.
2. Read one licence: the Llama licence and the Apache-2.0 text. Write one sentence on what you may not do with each.
3. Ask Claude: "steelman the open-weights position, then steelman the controlled-release position, 150 words each".
4. Talk to LeCun here.

Sources: [Ollama](https://ollama.com) · [Ollama model library](https://ollama.com/library) · [Open Source AI Definition (OSI)](https://opensource.org/ai/open-source-ai-definition) · [Apple silicon and unified memory (Apple)](https://developer.apple.com/documentation/apple-silicon)

Rolinda's question: "Is the one on your laptop the same thing as Claude, just smaller?"

#### Stop 7: What they cannot do, and why

_Hallucination, context windows, tokeniser quirks, and interpretability_

Four failure modes explain most of what goes wrong. Hallucination: the model predicts a plausible token sequence, and plausibility is not truth; a made-up citation is the model doing its job well. Context: it only sees what is in the window, so "remember what we said last week" needs a file (this is the whole point of the vault). Tokeniser quirks: it cannot reliably count letters or do arithmetic because it never sees letters or digits, only chunks. Non-determinism: sampling, plus floating-point on parallel hardware, means the same input can produce different output. Interpretability research (Chris Olah's team at Anthropic, and Distill before it) is the attempt to look inside: find the features and circuits that light up for a concept, so failures become explainable rather than folklore.

The engineering response is Evening 3: do not trust, instrument. Tests, linters, hooks, evals.

Do this:
1. Ask Claude for a citation on an obscure topic, then verify it. Write in the vault what happened.
2. Ask Claude to count the letter r in "strawberry" and then to explain why the answer might have been wrong in older models.
3. Skim one Transformer Circuits article (the one on features in a real model). Ask Claude to summarise the method in five lines.

Sources: [Transformer Circuits (Anthropic interpretability)](https://transformer-circuits.pub) · [Distill (2016 to 2021 archive)](https://distill.pub) · [Karpathy on tokenisation (Zero to Hero)](https://karpathy.ai/zero-to-hero.html)

Rolinda's question: "So when it is confidently wrong, that is not a bug you can fix?"

#### Stop 8: Karpathy's ladder

_Build a tiny language model yourself, with Claude as the tutor_

The best way to make the last seven stops stick is to build the smallest possible version. Karpathy's makemore trains a character-level model on a list of names in a few hundred lines. You do not need to write it: you need to run it, break it, and ask questions. Claude Code is an excellent tutor for this because the code is public and it can explain any line.

Definition of done for Evening 2: a notebook in your repo that trains makemore on a list of Dutch first names (ask Claude to fetch a public list), and a vault note that explains, in your words, tokens, embeddings, attention, loss and sampling. If you can explain those five words to Rolinda, you understand more than most people using these tools.

Do this:
1. git clone https://github.com/karpathy/makemore into a scratch folder; run it on the bundled names.
2. In Claude Code: "swap the dataset for Dutch first names and add a cell that samples ten new names".
3. Write the five-word vault note. Link it to every stop on this island.
4. Talk to Karpathy here before you leave.

Sources: [makemore](https://github.com/karpathy/makemore) · [nn-zero-to-hero repo](https://github.com/karpathy/nn-zero-to-hero) · [Zero to Hero course page](https://karpathy.ai/zero-to-hero.html)

Rolinda's question: "Can it make up a name that sounds Dutch but is not real? That is a bit spooky."

### Evening 3: From vibes to determinism

The sandbox: where you stop trusting and start instrumenting. Dotfiles, tests, hooks, CI, evals.

#### Stop 1: The vibe dial

_Karpathy's vibe coding, Cherny's instrumented coding, and knowing which end you are on_

In February 2025 Karpathy coined "vibe coding": fully give in to the vibes, forget the code exists, accept all, paste errors back in. It works for throwaway projects and for learning, which is why Evening 1 started there. Boris Cherny, who built Claude Code, describes the other end: start in plan mode, iterate on the plan, then let the model one-shot the implementation; treat CLAUDE.md as an accumulating record of mistakes; and above all give Claude a way to verify its own work, which he says improves quality two to three times. The skill is not choosing a side; it is knowing which end of the dial a task needs and moving deliberately.

The rule of thumb: if you would be embarrassed to lose it, or someone else depends on it, turn the dial toward checks. Everything on this island is a check.

Do this:
1. Write the dial into your AGENTS.md: which folders are vibe-only (scratch/), which need tests before merge.
2. Read Karpathy's original post and Cherny's thread. Note in the vault the one sentence from each you disagree with.
3. Talk to Karpathy and Cherny on this island.

Sources: [Karpathy's vibe coding post](https://x.com/karpathy/status/1886192184808149383) · [How Boris uses Claude Code (thread)](https://x.com/bcherny/status/2007179832300581177) · [Building Claude Code with Boris Cherny (Pragmatic Engineer)](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)

Rolinda's question: "So the fun version is allowed, as long as I know it is the fun version?"

#### Stop 2: Dotfiles and dotfolders

_What .git, .gitignore, .env, .venv, .claude, .agents, .github and ~/.config actually are_

A leading dot hides a file from ls; that is the entire mechanism. The convention is that dotfiles hold configuration and dotfolders hold machinery. In a project: .git/ is the whole history (never edit by hand), .gitignore lists what git should not track, .env holds secrets and must be in .gitignore, .venv/ is a Python environment, .claude/ is Claude Code's config (settings, hooks, skills, agents), .agents/ is the cross-tool skills folder, .github/workflows/ holds CI. In your home folder: ~/.zshrc runs when a terminal opens, ~/.gitconfig is your git identity, ~/.config/ is where modern tools (Ghostty, starship) keep settings, ~/.claude/ is your personal Claude config across projects.

Why they matter for consistency: every one of these is text, so every one can be versioned, diffed, and shared. A dotfiles repo is how experienced people make a new Mac feel like the old one in ten minutes (Evening 4, Stop 8).

Do this:
1. Run ls -la in the template repo and in your home folder. Ask Claude to explain every dot entry in one line each; put the list in the vault.
2. Check that .env and .venv/ are in .gitignore. Commit a change to .gitignore and read the diff.
3. Open ~/.claude/settings.json and the project's .claude/settings.json. Ask Claude which wins when they disagree, then verify in the docs.

Sources: [Claude Code settings and precedence](https://code.claude.com/docs/en/settings) · [gitignore documentation](https://git-scm.com/docs/gitignore) · [XDG base directory spec (why ~/.config)](https://specifications.freedesktop.org/basedir-spec/latest/)

Rolinda's question: "Why is it all hidden if it is important?"

#### Stop 3: Deterministic checks

_Tests, linters and formatters: the cheapest way to make an agent behave_

A model cannot be made deterministic; the checks around it can. Three tools do most of the work. A test runner (pytest) asserts that a function returns what you expect; if the agent breaks it, the test says so, not you. A linter (ruff check) catches unused imports, undefined names, and style drift; a formatter (ruff format) removes every argument about whitespace. Run all three before every commit and the agent's freedom is bounded exactly where you want it. In the template, workspace/python/scores.py gets its first test tonight.

The habit Cherny recommends: give the agent the command that verifies its work and tell it to run it. Put that command in AGENTS.md under Commands. It will run it without being asked.

Do this:
1. uv pip install pytest ruff. Ask Claude: "write tests for workspace/python/scores.py that cover the mean and the best score, then run them".
2. Ask Claude to introduce a bug on purpose and show the failing test. Then ask it to fix it. Watch the loop.
3. Add to AGENTS.md: "Before finishing, run: ruff check && ruff format && pytest". Start a new session and see it obey.

Sources: [pytest getting started](https://docs.pytest.org/en/stable/getting-started.html) · [ruff](https://docs.astral.sh/ruff/) · [Claude Code best practices (verification)](https://code.claude.com/docs/en/best-practices)

Rolinda's question: "So the test is the thing that does not have opinions?"

#### Stop 4: Hooks as gates

_PreToolUse and PostToolUse, permissions, and refusing edits that skip the checks_

Evening 1 used a hook to back up data. Tonight hooks become gates. A PreToolUse hook runs before Claude uses a tool and can allow, deny, or ask; a PostToolUse hook runs after and can run your formatter or tests; a Stop hook runs when Claude thinks it is finished and can send it back if the tests fail. Combined with the permissions system (which commands are allowed without asking) you get a policy that does not depend on the model's mood. This is how teams at Anthropic keep dozens of parallel agents from doing damage.

Design rule: hooks are for things that must happen every time. Instructions in AGENTS.md are for things that should usually happen. Do not write a rule where you need a gate.

Do this:
1. Add a PostToolUse hook on Edit|Write that runs ruff format on the changed file (the hooks guide has the exact shape).
2. Add a Stop hook that runs pytest -q and returns a non-zero exit with a message when tests fail. Ask Claude to break a test and watch it get sent back.
3. Read the permissions page and add Bash(pytest*) to the allow list so it never asks for that.

Sources: [Hooks guide](https://code.claude.com/docs/en/hooks-guide) · [Hooks reference](https://code.claude.com/docs/en/hooks) · [Permissions](https://code.claude.com/docs/en/permissions)

Rolinda's question: "So this is the part where it is not allowed to be lazy?"

#### Stop 5: Plan, spec, small changes

_The Cherny workflow: plan mode, a spec, a to-do list, one PR at a time_

Most bad agent output comes from a bad first prompt. The fix is procedural. Start in plan mode (Shift+Tab twice in Claude Code): the model reads, proposes, and does not edit. Go back and forth until the plan is right. Then switch to auto-accept and let it execute. For anything bigger than a bug fix, ask it to write a spec first, then a plan, then a to-do list, and walk through it. Keep pull requests small enough to review in five minutes; Anthropic runs a first-pass automated review on every PR and a human still approves the merge.

Two commands to memorise: /compact when the context gets long and slow, /rewind (or checkpoints) to go back to before a bad step without losing the conversation.

Do this:
1. Start a task in plan mode and refuse to leave it until the plan lists every file it will touch.
2. Ask Claude to write a spec for "players can have a nickname" in docs/specs/, then implement from the spec in a fresh session.
3. Open a PR with the GitHub CLI and ask Claude to review it before you merge: gh pr create, then "review PR #1 for correctness and missing tests".

Sources: [Common workflows (plan mode, resume, images)](https://code.claude.com/docs/en/common-workflows) · [Checkpointing and rewind](https://code.claude.com/docs/en/checkpointing) · [How to use Claude Code like the people who built it (Every)](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it)

Rolinda's question: "So you make it explain the plan first, like a contractor?"

#### Stop 6: CI: the check that runs without you

_GitHub Actions on every push, so the main branch is always green_

Local checks depend on someone remembering to run them. Continuous integration runs them on a server on every push and shows a red or green mark on the commit. A minimal workflow file in .github/workflows/ci.yml checks out the code, installs Python, runs ruff and pytest. Once it exists, "is main green?" is a fact, not a feeling, and the agent can be told to keep it green. This is also where DuckDB queries can be smoke-tested against the sample data so the schema contract from Evening 1 is enforced.

Do this:
1. Ask Claude: "add a GitHub Actions workflow that runs ruff and pytest on push and pull request, Python 3.12, using uv". Push it. Watch the Actions tab.
2. Break a test, push, see red. Fix, push, see green. Take a screenshot for the vault.
3. Add branch protection so main cannot be merged to while red (Settings, Branches).

Sources: [GitHub Actions quickstart](https://docs.github.com/en/actions/quickstart) · [uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/) · [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Rolinda's question: "So the computer checks the computer's work before you look at it?"

#### Stop 7: Repetitive tasks, reliably

_Headless runs, schedules, idempotency, and when a subagent beats a prompt_

Evening 1 scheduled one headless job. The engineering questions arrive the second morning: what if it runs twice, what if the input is empty, what if it half-finishes. The answers are old: make jobs idempotent (running twice yields the same result), write output to a temporary file and move it into place, log every run with a timestamp, and fail loudly. A subagent with a narrow system prompt and a fixed tool list is more predictable than a general session for a repetitive job, because it cannot wander. Batch work ("do this for every file in data/") is where claude -p with --output-format json shines: you get a parsable result per item.

Do this:
1. Rewrite the scorekeeper job so it writes to Scores.md.tmp and renames at the end. Run it twice; diff the vault.
2. Ask Claude to add a logs/ line per run with start time, end time, and exit code. Check it after tomorrow's 08:00 run.
3. Try one batch: for f in data/*.csv; do claude -p "summarise $f in one line" --output-format text; done.

Sources: [Headless / programmatic use](https://code.claude.com/docs/en/headless) · [Subagents](https://code.claude.com/docs/en/sub-agents) · [launchd (Apple)](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)

Rolinda's question: "What happens if it runs while I am editing the same file?"

#### Stop 8: Evals: measure the agent, not the vibe

_A tiny harness that scores your prompts and skills on fixed cases_

Once you have rules, hooks and CI, the last question is whether your instructions are actually improving the output. An eval is a fixed set of inputs with expected outputs, run through the model, scored. It can be five cases in a CSV. The point is not statistics; it is that when you change AGENTS.md or a skill, you can see whether things got better or worse instead of guessing. Anthropic's own guidance on building evals is short and practical. Combine with claude -p and you have a loop: change the instruction, run the five cases, compare.

Definition of done for Evening 3: tests, a formatter hook, a Stop gate, green CI, an idempotent scheduled job, and a five-case eval for one skill. You now have a system that behaves, with a model inside it that does not.

Do this:
1. Write evals/cases.csv with five prompts and the answer you expect (yes/no or a short string).
2. Ask Claude to write evals/run.py that calls claude -p per case and prints a score. Run it before and after changing one rule.
3. Record both scores in the vault. That number is your first eval.

Sources: [Building evals (Anthropic docs)](https://docs.claude.com/en/docs/test-and-evaluate/develop-tests) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) · [Anthropic cookbook (evals examples)](https://github.com/anthropics/anthropic-cookbook)

Rolinda's question: "So you grade it like homework. Does it know?"

### Evening 4: Terminal, git and the toolbelt, on Apple silicon

Production: your machine, set up like someone who does this every day. Mac, Chrome, Ghostty, git, Claude everywhere.

#### Stop 1: The Mac, properly

_Homebrew, Apple silicon, Chrome, and the three settings that save an hour a week_

Everything on this island assumes a MacBook with Apple silicon and Chrome as the default browser, because that is what you have and it makes every instruction exact. Homebrew is the package manager; on Apple silicon it lives in /opt/homebrew, which is why some old guides fail. Rosetta is not needed for anything in this course. A Brewfile is a text list of everything you install, so the next Mac is one command away. Chrome is the browser Claude in Chrome and Claude Code's browser tools target, and it is the one whose DevTools you will use in Stop 6.

Do this:
1. Install Homebrew from brew.sh. Then brew bundle dump to write a Brewfile of what you already have; commit it to your dotfiles repo (Stop 8).
2. Set Chrome as default. In Chrome, sign in to Claude and pin the tab.
3. Ask Claude: "what is in /opt/homebrew/bin and why is it on my PATH", and put the answer in the vault.

Sources: [Homebrew](https://brew.sh) · [Homebrew Bundle (Brewfile)](https://docs.brew.sh/Brew-Bundle-and-Brewfile) · [Apple silicon developer docs](https://developer.apple.com/documentation/apple-silicon)

Rolinda's question: "Is this the part where it stops being a laptop and becomes a workstation?"

#### Stop 2: A terminal you enjoy

_Ghostty, zsh, starship, fzf, ripgrep, bat, eza, and Tom's configs_

Claude Code lives in a terminal, so the terminal is the room you work in all day. Ghostty (Mitchell Hashimoto, who built Terraform and Vagrant) is fast, native on macOS, GPU-rendered, and configured with one text file in ~/.config/ghostty/config. Around it: zsh with a prompt from starship, fzf for fuzzy history and file search, ripgrep instead of grep, bat instead of cat, eza instead of ls, zoxide for jumping between folders. None of these are required; all of them are the difference between tolerating the terminal and preferring it. Tom keeps his configs on GitHub; installing them is the fastest way to a good setup, and reading them is a good way to learn what each tool does.

Do this:
1. brew install --cask ghostty, then brew install starship fzf ripgrep bat eza zoxide.
2. Clone Tom's dotfiles (link below), read ghostty/config and .zshrc before you copy anything. Ask Claude to explain each line you do not understand.
3. Open Ghostty, run claude, and try Ctrl+R with fzf. That is the loop for the rest of your life.

Sources: [Ghostty](https://ghostty.org) · [Tom's dotfiles on GitHub](https://github.com/YOUR-USER/dotfiles) · [starship](https://starship.rs) · [fzf](https://github.com/junegunn/fzf) · [ripgrep](https://github.com/BurntSushi/ripgrep)

Rolinda's question: "Why does the terminal need to be pretty?"

#### Stop 3: Git, part one

_Fork, clone, branch, commit, push, pull request, learned by doing it to the template_

Git is a database of snapshots with names. A repository is the database; a commit is a snapshot; a branch is a movable name pointing at a commit; a remote is another copy of the database on another computer; a fork is your own copy on GitHub; a pull request is a request to merge your branch into someone else's. Every command tonight is one of those nouns plus a verb. You will do it by hand once, then let Claude do it, then check that you can still read what it did.

Do this:
1. Fork the template on GitHub, gh repo clone YOUR-USER/vibe, git switch -c feature/nickname.
2. Make one change by hand, git add -p (review every hunk), git commit, git push -u origin feature/nickname, gh pr create.
3. Ask Claude to do the same for a second change and read git log --oneline --graph afterwards.
4. Talk to Torvalds on this island.

Sources: [Git tutorial (official)](https://git-scm.com/docs/gittutorial) · [GitHub: fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) · [GitHub CLI manual](https://cli.github.com/manual/)

Rolinda's question: "So a branch is just a bookmark that moves?"

#### Stop 4: Git, part two

_Revert, reset, rebase, cherry-pick, worktrees, and how Cherny runs five agents at once_

Undo has flavours. git revert makes a new commit that undoes an old one (safe, shareable). git reset moves the branch name backwards (rewrites your local history; never on shared branches). git rebase replays your commits on top of someone else's, giving a straight line instead of a merge bubble; interactive rebase lets you squash five messy agent commits into one clean one. git cherry-pick copies a single commit across. Worktrees check out several branches into several folders from one repository, which is how you run several agents on the same repo at once; Cherny uses separate checkouts and numbers the tabs.

Do this:
1. On a throwaway branch: make three commits, git rebase -i HEAD~3, squash them into one. Then git reflog to see nothing was lost.
2. git worktree add ../vibe-2 feature/second, open a second Ghostty tab, run a second Claude there. Give each a different task.
3. Ask Claude to revert a commit by hash and explain the difference from reset in the commit message.

Sources: [git rebase](https://git-scm.com/docs/git-rebase) · [git worktree](https://git-scm.com/docs/git-worktree) · [Cherny on parallel checkouts (InfoQ)](https://infoq.com/news/2026/01/claude-code-creator-workflow/)

Rolinda's question: "If you can rewrite history, how do you know what actually happened?"

#### Stop 5: Claude Code, the power settings

_Plan mode, --continue, /compact, /rewind, permissions, memory, teleport between terminal, web and phone_

You have used Claude Code for three evenings; tonight you configure it. Personal memory in ~/.claude/CLAUDE.md applies to every project. Project memory in the repo's CLAUDE.md is versioned with the code. claude --continue resumes; /compact summarises a long session; /rewind goes back a step; plan mode keeps it from editing. Sessions can move between the terminal, the web and the iOS app (Cherny starts sessions from his phone in the morning). Set your permissions once so the routine commands never ask, and keep the dangerous ones asking.

Do this:
1. Write your personal ~/.claude/CLAUDE.md: how you like explanations, which commands are fine, what to never do. Ten lines.
2. Configure allowed tools in settings for Bash(pytest*), Bash(ruff*), Bash(git status*).
3. Try the desktop app and the web session once, so you know they exist when you need them.

Sources: [Memory (CLAUDE.md, imports, precedence)](https://code.claude.com/docs/en/memory) · [Settings](https://code.claude.com/docs/en/settings) · [CLI reference](https://code.claude.com/docs/en/cli-reference) · [How Boris uses Claude Code (curated tips)](https://howborisusesclaudecode.com/)

Rolinda's question: "So it has a memory now, but only if you write it down for it?"

#### Stop 6: Claude in Chrome

_A browser agent for the repetitive web tasks, and Claude Code driving Chrome_

Two different things share a name. Claude in Chrome is Anthropic's official extension: a side panel where Claude can read the page, click, fill forms and navigate, with site restrictions on banking and similar categories. Separately, Claude Code can connect to Chrome so the agent in your terminal can open pages, take screenshots and debug your own web app in a real browser. For a chief of staff the first one is the daily tool: expense portals, calendar juggling, form filling, research across tabs. For the game you built, the second one lets Claude see what it made.

Safety habit: an agent in your logged-in browser acts as you. Use it on tabs you would let a colleague touch, and read the permission prompt every time.

Do this:
1. Install Claude in Chrome from the Chrome Web Store (official listing linked below) and sign in.
2. Give it one repetitive task you did last week and watch it. Note in the vault what it got wrong.
3. In Claude Code, connect Chrome (docs below) and ask it to open workspace/game/index.html, play one round, and report the score it saw.

Sources: [Claude in Chrome (Chrome Web Store, official)](https://chromewebstore.google.com/detail/fcoeoabgfenejglbffodgkkbkcdhcgfn) · [Claude in Chrome (product page)](https://claude.com/chrome) · [Claude Code and Chrome](https://code.claude.com/docs/en/chrome)

Rolinda's question: "It can click things in my browser? As me?"

#### Stop 7: The other agents

_OpenCode, Codex CLI, Gemini CLI: same AGENTS.md, same .agents/skills, different engines_

This course is Anthropic-centric on purpose: one tool, learned deeply. The setup you built is not locked to it. AGENTS.md is read by OpenAI's Codex CLI, Google's Gemini CLI, Cursor, Copilot and OpenCode, an open-source terminal agent that can run against Claude, GPT, Gemini or a local Ollama model. Your skills in .agents/skills/ load in OpenCode and Codex unchanged. Try one alternative tonight, on the same repo, with the same instructions, and see what changes: usually the engine, rarely the workflow.

Do this:
1. brew install opencode (or the install script on opencode.ai). Run it in the template repo; confirm it picked up AGENTS.md and the skills.
2. Point it at your local Ollama model from Evening 2 and ask for the same test you asked Claude for in Evening 3. Compare.
3. Write the comparison in the vault: speed, correctness, what needed hand-holding.

Sources: [OpenCode](https://opencode.ai) · [AGENTS.md](https://agents.md) · [Agent Skills standard](https://agentskills.io) · [Gemini CLI](https://github.com/google-gemini/gemini-cli)

Rolinda's question: "So the rules are yours and the robot is replaceable?"

#### Stop 8: Your dotfiles repo

_Everything you configured tonight, versioned, so the next Mac is ten minutes_

The graduation project is a repository called dotfiles: your .zshrc, Ghostty config, starship config, .gitconfig, personal ~/.claude/CLAUDE.md, a Brewfile, and an install script that symlinks them into place. Tom's is the reference. When it exists, a new machine is: install Homebrew, clone dotfiles, run install. It is also the most honest record of how you actually work, and a good thing to let Claude read when it sets up a project for you.

Definition of done for the course: four islands built, a template repo you understand line by line, a vault with your own words in it, and a dotfiles repo. Rolinda can pour the last one.

Do this:
1. mkdir ~/dotfiles && cd ~/dotfiles && git init. Move the config files in and symlink them back (ask Claude to write install.sh using ln -sf).
2. Add the Brewfile from Stop 1. Push to GitHub, private if you prefer.
3. Write the final vault note: what you would tell yourself before Evening 1.

Sources: [Tom's dotfiles on GitHub](https://github.com/YOUR-USER/dotfiles) · [GitHub: dotfiles guide](https://dotfiles.github.io) · [Homebrew Bundle](https://docs.brew.sh/Brew-Bundle-and-Brewfile)

Rolinda's question: "And then you never have to do any of this again?"

### The mentors

**Boris Cherny**, Creator and head of Claude Code, Anthropic (Innovation Campus). Built Claude Code as an internal experiment at Anthropic in 2024; it became the company's main coding tool and then a product. Previously a principal engineer at Meta and author of Programming TypeScript. Runs five Claude sessions in his terminal and five to ten on the web, each in its own checkout. Sources: [Building Claude Code with Boris Cherny (Pragmatic Engineer)](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny) · [Inside the workflow of Claude Code's creator (InfoQ)](https://infoq.com/news/2026/01/claude-code-creator-workflow/) · [His thread on X](https://x.com/bcherny/status/2007179832300581177) · [How Boris uses Claude Code (curated)](https://howborisusesclaudecode.com/)

**Cat Wu**, Founding engineer and product lead, Claude Code (Innovation Campus). Co-built Claude Code from the first internal prototype and shaped it into a product used far beyond engineering. Talks about the workflows Anthropic's own engineers discovered: slash commands for feature development and first-pass code review, subagents for narrow jobs. Sources: [How to use Claude Code like the people who built it (Every, with Cat Wu and Boris Cherny)](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it)

**Andrej Karpathy**, Researcher, educator; ex OpenAI, ex Tesla AI (Cold Storage Cluster). Founding member of OpenAI, led Tesla Autopilot's AI team, taught Stanford's first deep-learning class, and now teaches the internet: the Zero to Hero series builds neural networks from scratch in code, and the general-audience talks explain LLMs without maths. Coined "vibe coding" in 2025 and "Software 3.0" for programming in natural language. Sources: [karpathy.ai](https://karpathy.ai/) · [Zero to Hero course](https://karpathy.ai/zero-to-hero.html) · [nn-zero-to-hero on GitHub](https://github.com/karpathy/nn-zero-to-hero) · [vibe coding post](https://x.com/karpathy/status/1886192184808149383)

**Yann LeCun**, Turing Award 2018; convolutional networks; Meta AI chief scientist (Cold Storage Cluster). Applied backpropagation to handwritten digits in 1989 and invented the convolutional network that read cheques and zip codes in production in the 1990s. Shared the 2018 Turing Award with Hinton and Bengio. Argues loudly for open-weight models and that autoregressive LLMs are not the road to human-level intelligence; his alternative is JEPA, predicting in representation space. Sources: [A Path Towards Autonomous Machine Intelligence (LeCun 2022, OpenReview)](https://openreview.net/pdf?id=BZ5a1r-kVsf) · [Backpropagation applied to handwritten zip code recognition (1989)](https://ieeexplore.ieee.org/document/6795724) · [Karpathy's reproduction](https://github.com/karpathy/lecun1989-repro)

**Geoffrey Hinton**, Backpropagation, deep learning; Nobel Prize in Physics 2024 (Cold Storage Cluster). Co-author of the 1986 paper that made backpropagation practical, teacher of Sutskever and Krizhevsky (AlexNet), Turing Award 2018, Nobel Prize in Physics 2024 for foundational work on learning in neural networks. Left Google in 2023 to speak freely about risks. Sources: [Learning representations by back-propagating errors (Nature 1986)](https://www.nature.com/articles/323533a0) · [Nobel Prize 2024, Hinton facts](https://www.nobelprize.org/prizes/physics/2024/hinton/facts/)

**Fei-Fei Li**, ImageNet; Stanford HAI co-director (Cold Storage Cluster). Built ImageNet from 2007: 14 million hand-labelled images, when most of the field thought data was a solved problem and algorithms were the bottleneck. The 2012 ImageNet competition result started the deep-learning era. Co-founded Stanford's Institute for Human-Centered AI. Sources: [ImageNet](https://www.image-net.org) · [Stanford HAI](https://hai.stanford.edu)

**Rich Sutton**, Reinforcement learning; the Bitter Lesson; Turing Award 2024 (Cold Storage Cluster). Co-wrote the standard reinforcement learning textbook, shared the 2024 Turing Award with Andrew Barto, and in 2019 wrote the one-page Bitter Lesson that the Claude Code team keeps on the wall. Sources: [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) · [Reinforcement Learning: An Introduction (free)](http://incompleteideas.net/book/the-book.html)

**Dario Amodei**, CEO and co-founder, Anthropic (Cold Storage Cluster). Co-author of the 2020 scaling-laws paper, former VP of research at OpenAI, co-founded Anthropic in 2021 with a safety-first thesis. Wrote Core Views on AI Safety and the essay Machines of Loving Grace on what could go right. Sources: [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361) · [Core Views on AI Safety](https://www.anthropic.com/news/core-views-on-ai-safety) · [Machines of Loving Grace](https://darioamodei.com/machines-of-loving-grace)

**Chris Olah**, Interpretability research lead, Anthropic (Sandbox Environment). Co-founder of Anthropic and of Distill, the journal that made machine learning explanations visual. Leads the work on looking inside models: finding features and circuits that correspond to concepts, including in production Claude models. Sources: [Transformer Circuits](https://transformer-circuits.pub) · [Distill](https://distill.pub)

**Mitchell Hashimoto**, Creator of Ghostty; co-founder of HashiCorp (Production Environment). Co-founded HashiCorp (Vagrant, Terraform), then spent his time building Ghostty: a terminal emulator that is fast, native on macOS, and configured with one plain text file. Writes carefully about how he uses AI agents in his own work. Sources: [Ghostty](https://ghostty.org) · [Ghostty configuration reference](https://ghostty.org/docs/config) · [mitchellh.com](https://mitchellh.com)

**Linus Torvalds**, Creator of Linux and git (Production Environment). Wrote git in 2005 in about two weeks after the Linux kernel lost its previous version-control tool. Designed it around content-addressed snapshots and cheap branching, which is why every command at Stops 3 and 4 makes sense once you know that model. Sources: [Pro Git (free book)](https://git-scm.com/book/en/v2) · [git internals chapter](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)

**The OpenCode team**, Open-source terminal coding agent (Production Environment). An open-source agent for the terminal that works with Claude, GPT, Gemini and local models, reads AGENTS.md and the Agent Skills standard. Useful as the second opinion that shows which parts of your setup are yours and which belong to the vendor. Sources: [OpenCode](https://opencode.ai) · [OpenCode on GitHub](https://github.com/sst/opencode)

## The tech tree: shelf by shelf

Forty-eight topics on eleven shelves: terminal and shell; version control and GitHub; config and formats; languages and code; data; web, networks and APIs; ship and run; agents and the harness; docs and versioning; knowledge and Obsidian; what is coming. Every topic has a depth of its own (basics, working knowledge, deep), so a shelf is something you come back to rather than a rank you pass. The full tree, with what each topic is, its real history, a five-minute try, docs and what it unlocks, is generated from `vibemap/tech.py` into [ROADMAP.md](ROADMAP.md); the same notes sit in the vault under Tech tree and in the game under Tree. Your level (Intern to Expert) is the XP ladder, not the tree.

Tom is available for one panicked message per week. Rolinda is available for wine.

## Reference

- Claude Code docs: https://code.claude.com/docs/en/overview
- Extending Claude Code (CLAUDE.md, skills, hooks, MCP, plugins): https://code.claude.com/docs/en/features-overview
- Obsidian help: https://help.obsidian.md
