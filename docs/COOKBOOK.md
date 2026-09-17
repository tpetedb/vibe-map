# Cookbook

Recipes are prompts you paste into your provider plus a definition of done. The general ones work for everyone; the persona ones are tuned to a field of work. Switch persona with `uv run vibe persona <id>`; the vault note *Cookbook* mirrors your persona's section.

## Your provider

| provider | run a prompt from a script | docs |
|---|---|---|
| Claude Code | `claude -p "..."` | https://code.claude.com/docs/en/quickstart |
| OpenAI Codex CLI | `codex exec "..."` | https://learn.chatgpt.com/docs/non-interactive-mode |
| Gemini CLI | `gemini -p "..."` | https://github.com/google-gemini/gemini-cli |
| GitHub Copilot CLI | `copilot -p "..."` | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli |
| OpenCode | `opencode run "..."` | https://opencode.ai/docs/cli/ |

## General recipes

### Start the evening

Everything installed, the vault open, the game running.

```bash
brew install just
just setup
just start
```

**Done when:** The onboarding screen shows every core tool green.

### Claim a workstream

Let the CLI check your work and award the XP.

```bash
uv run vibe status
uv run vibe check 1
uv run vibe done 1 "a scoring board that ranks the team by coffee"
```

**Done when:** The vault has a dated note for the workstream and Tonight lists it as done.

### Break something on purpose, then come back

A branch is a sandbox. Nothing on main can be hurt from a play branch.

```bash
just break sandbox
# ask the agent for anything, however wild
uv run vibe explain
just rescue
```

**Done when:** You are back on main, the play branch still exists, and explain told you what happened.

### Ask the council

Four mentors answer, review each other, a chairman decides.

```bash
uv run vibe council "Should I learn git before Python?"
open vault/Camp
```

**Done when:** A Council note in the vault with a verdict and three steps for tonight.

### Change the voice

Serious, academic, plain, or one the model writes for you.

```bash
uv run vibe theme boardroom
just build
uv run vibe theme rainforest --create --brief "a jungle expedition, plain tone, no drinks"
```

**Done when:** The title screen reads in the new voice after a rebuild.

## Chief of Staff

*running the leadership team's week.*

**Your game (workstream 1).** A calendar dungeon: meetings are rooms, each room has a monster (a decision that keeps getting postponed), and you clear the week by making three decisions before Friday.

**Your dataset (workstream 3).** `workspace/data/examples/meetings.csv`, columns `date, meeting, attendees, minutes, decisions`. Write it with `uv run vibe persona chief-of-staff`. Question to answer: Which meeting costs the most minutes per decision?

**Rolinda asks.** Which meeting should be an email, and can you prove it with the numbers?

### The week in one page

Workstream 2. Turn a folder of meeting notes into a one-page brief.

```text
Read every .md file in notes/, list the decisions made, the open decisions with an owner, and the three risks. Write brief.md. Do not invent anything that is not in the notes.
```

**Done when:** brief.md exists and every line traces to a note.

### Meeting cost dashboard

Workstream 3. A chart of minutes per decision by meeting.

```text
Using workspace/data/meetings.csv, write workspace/sql/cost_per_decision.sql in DuckDB and a Python script that draws a bar chart to python/out/. Explain the one SQL construct I have not seen.
```

**Done when:** The chart opens and the worst meeting is obvious.

### Monday morning agent

Workstream 8. An agent that drafts the weekly agenda every Monday at 07:30.

```text
Write a script that runs the provider in print mode with the prompt in prompts/agenda.md and writes agenda-<date>.md. Then show me the crontab line for Monday 07:30.
```

**Done when:** A file appears on Monday without you touching the keyboard.

## CEO, outdoor cleaning company

*crews, routes, weather and invoices.*

**Your game (workstream 1).** Pressure-washer tycoon: send crews to dirty facades, dodge rain, keep the vans fuelled, and beat last month's revenue before the season ends.

**Your dataset (workstream 3).** `workspace/data/examples/jobs.csv`, columns `date, client, crew, hours, revenue_eur, rain`. Write it with `uv run vibe persona cleaning-ceo`. Question to answer: Which crew earns the most per hour, and does rain change it?

**Rolinda asks.** Which client pays you the least per hour, and why are you still going there?

### Quote in thirty seconds

Workstream 3. A script that turns a photo description into a quote.

```text
Write quote.py: I type the facade size in square metres and the dirt level (1 to 3); it prints a quote using the rates in rates.toml. Add a test.
```

**Done when:** Three quotes printed, one test green.

### Rain plan

Workstream 5. Reschedule tomorrow's jobs when the forecast says rain.

```text
Read data/jobs.csv and the weather in weather.json; list the jobs to move, who to call, and draft the message in Dutch. Do not send anything.
```

**Done when:** A draft per client, nothing sent.

### Invoice reminder loop

Workstream 8. Every Friday, list unpaid invoices older than 30 days.

```text
Write a script that reads invoices.csv, prints the overdue ones sorted by amount, and runs from cron on Friday 09:00.
```

**Done when:** The list appears on Friday, the crontab line is in the vault.

## Managing director, university faculty

*programmes, budgets, accreditation and staff.*

**Your game (workstream 1).** Faculty builder: enrol students, fund labs, survive an accreditation visit, and keep the professors from leaving for industry.

**Your dataset (workstream 3).** `workspace/data/examples/enrolments.csv`, columns `year, programme, students, budget_keur, staff`. Write it with `uv run vibe persona university-md`. Question to answer: Which programme grows fastest per staff member?

**Rolinda asks.** If one programme doubles next year, what breaks first, and where is that in the numbers?

### Accreditation binder index

Workstream 2. An index of every document the visit will ask for.

```text
Read docs/ and produce index.md grouped by the accreditation standard each document supports; flag standards with no document. Do not write the documents.
```

**Done when:** Every standard has a document or a red flag.

### Students per staff trend

Workstream 3. A line chart per programme, 2023 to 2026.

```text
Using workspace/data/enrolments.csv, write workspace/sql/ratio.sql in DuckDB and a Python chart. One sentence on what the trend implies.
```

**Done when:** Chart in python/out/, sentence in the vault.

### Board memo with citations

Workstream 6. A memo where every number links to its source file.

```text
Write memo.md for the board: three findings, each with the file and line it came from. Refuse to state a number you cannot cite.
```

**Done when:** Every number has a citation; you checked two.

## Teacher educator (pabo)

*lesson plans, student teachers, classroom observations.*

**Your game (workstream 1).** Classroom quest: thirty first-graders, one lesson plan, and a fire drill at 10:15. Keep attention above zero and finish the reading circle.

**Your dataset (workstream 3).** `workspace/data/examples/lessons.csv`, columns `date, group, subject, minutes, attention, rating`. Write it with `uv run vibe persona pabo-teacher`. Question to answer: Which subject holds attention longest, and in which group?

**Rolinda asks.** Which lesson would you drop, and what does the attention column say about why?

### Lesson plan from a learning goal

Workstream 2. A 45-minute plan with materials and a check for understanding.

```text
Write a lesson plan for group 1A on 'counting to 20' following the template in templates/lesson.md. Include one differentiation for fast finishers. Cite the curriculum goal it serves.
```

**Done when:** The plan fits the template and names the goal.

### Observation notes to feedback

Workstream 6. Turn raw observation notes into structured feedback.

```text
Read observations/*.md and write feedback.md per student teacher: two strengths, one next step, one question. Keep their own words where possible.
```

**Done when:** Each student teacher has a file; nothing invented.

### Attention chart

Workstream 3. Attention by subject and group from lessons.csv.

```text
Write workspace/sql/attention.sql and a Python chart from data/lessons.csv. Explain group by in one comment.
```

**Done when:** The chart matches your gut feeling, or you learned something.

## Data engineer

*pipelines, warehouses, orchestration and tests.*

**Your game (workstream 1).** Pipeline defense: rows flow from left to right, schema drift attacks at night, and you place tests and quarantine tables to keep the gold layer clean until the CEO's dashboard loads.

**Your dataset (workstream 3).** `workspace/data/examples/pipeline_runs.csv`, columns `run_at, pipeline, layer, rows, seconds, status`. Write it with `uv run vibe persona data-engineer`. Question to answer: Which layer failed last night, and what did the row counts say before it did?

**Rolinda asks.** If the silver run says zero rows, what did the bronze run say, and why did nobody get paged?

### Two-file task pattern

Workstream 3. A pipeline task as a .py plus a .yaml sidecar with tests.

```text
Create tasks/orders_silver.py and tasks/orders_silver.yaml (source, target, schedule, owner). The task reads bronze from DuckDB, dedupes, writes silver. pytest with a fixture CSV.
```

**Done when:** uv run pytest is green and the yaml validates.

### Schema drift guard

Workstream 4. A hook that refuses a commit when a CSV header changes.

```text
Write a pre-commit style Claude Code hook (PostToolUse on Edit and Write) that compares data/*.csv headers to schema.json and prints the diff. Show me the settings.json block.
```

**Done when:** Renaming a column produces a loud message.

### Nightly run report

Workstream 8. Headless agent summarises last night's runs into the vault.

```text
Write a script that runs the provider in print mode over data/pipeline_runs.csv and writes vault/Camp/Runs.md with a table and one paragraph. Schedule it at 07:00.
```

**Done when:** Runs.md is updated by the schedule, not by you.

## Interior stylist

*clients, mood boards, budgets and suppliers.*

**Your game (workstream 1).** Room by room: a client hands you an empty apartment and a budget; place furniture, match a palette, and hit the reveal before the movers arrive.

**Your dataset (workstream 3).** `workspace/data/examples/projects.csv`, columns `client, room, style, budget_eur, spent_eur, status`. Write it with `uv run vibe persona interior-stylist`. Question to answer: Which style goes over budget most often?

**Rolinda asks.** Which style makes you money and which one makes you sorry, and can the table show it?

### Mood board brief

Workstream 2. A structured brief from a messy client email.

```text
Read client-email.txt and write brief.md: rooms, style words, must-haves, budget per room, three open questions for the client. Keep their words.
```

**Done when:** The client says yes to the brief in one reply.

### Budget tracker

Workstream 3. Spent versus budget per client and style, with a chart.

```text
Using workspace/data/projects.csv, write workspace/sql/over_budget.sql and a Python chart of spent versus budget per style. One sentence on the worst offender.
```

**Done when:** The chart shows the style that overruns.

### Supplier follow-up

Workstream 5. A weekly list of items ordered but not delivered.

```text
Read orders.csv, list items older than 14 days without a delivery date, and draft one message per supplier. Nothing is sent.
```

**Done when:** Drafts exist, nothing sent, the list is right.
