"""Personas: the same course, tuned to the learner's field of work.

A persona changes the example game, the sample dataset, Rolinda's question
and the recipes. It never changes the workstreams themselves: every persona
still ships a game, writes AGENTS.md, queries a CSV, learns git, connects a
tool, links a vault, publishes, and schedules an agent.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Recipe:
    """One thing to build in under an hour, provider-agnostic."""

    title: str
    goal: str
    prompt: str
    done: str
    workstream: int


@dataclass(frozen=True, slots=True)
class Dataset:
    """A small, realistic CSV the persona would recognise."""

    filename: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    question: str

    def to_csv(self) -> str:
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(self.columns)
        w.writerows(self.rows)
        return buf.getvalue()


@dataclass(frozen=True, slots=True)
class Persona:
    id: str
    label: str
    field: str
    game_idea: str
    dataset: Dataset
    rolinda: str
    recipes: tuple[Recipe, ...] = field(default_factory=tuple)
    # Shelves of the tech tree this field leans on, offered as a preset when
    # the learner picks what to learn. Empty means no preset, so: everything.
    interests: tuple[str, ...] = field(default_factory=tuple)


PERSONAS: dict[str, Persona] = {
    "chief-of-staff": Persona(
        id="chief-of-staff",
        label="Chief of Staff",
        field="running the leadership team's week",
        game_idea=(
            "A calendar dungeon: meetings are rooms, each room has a monster "
            "(a decision that keeps getting postponed), and you clear the week "
            "by making three decisions before Friday."
        ),
        dataset=Dataset(
            filename="meetings.csv",
            columns=("date", "meeting", "attendees", "minutes", "decisions"),
            rows=(
                ("2026-09-07", "Leadership weekly", "6", "55", "2"),
                ("2026-09-08", "Budget review", "4", "90", "1"),
                ("2026-09-09", "Vendor pitch", "3", "45", "0"),
                ("2026-09-10", "Board prep", "5", "120", "3"),
                ("2026-09-14", "Leadership weekly", "6", "50", "4"),
                ("2026-09-15", "Hiring sync", "3", "30", "1"),
                ("2026-09-16", "Offsite planning", "7", "75", "0"),
                ("2026-09-17", "Board prep", "5", "60", "2"),
            ),
            question="Which meeting costs the most minutes per decision?",
        ),
        rolinda="Which meeting should be an email, and can you prove it with the numbers?",
        recipes=(
            Recipe(
                "The week in one page",
                "Turn a folder of meeting notes into a one-page brief.",
                "Read every .md file in notes/, list the decisions made, the open "
                "decisions with an owner, and the three risks. Write brief.md. "
                "Do not invent anything that is not in the notes.",
                "brief.md exists and every line traces to a note.",
                2,
            ),
            Recipe(
                "Meeting cost dashboard",
                "A chart of minutes per decision by meeting.",
                "Using workspace/data/examples/meetings.csv, write "
                "workspace/sql/cost_per_decision.sql in DuckDB and a Python "
                "script that draws a bar chart to "
                "workspace/python/out/. Explain the one SQL construct I have not seen.",
                "The chart opens and the worst meeting is obvious.",
                3,
            ),
            Recipe(
                "Monday morning agent",
                "An agent that drafts the weekly agenda every Monday at 07:30.",
                "Write a script that runs the provider in print mode with the "
                "prompt in prompts/agenda.md and writes agenda-<date>.md. Then "
                "show me the crontab line for Monday 07:30.",
                "A file appears on Monday without you touching the keyboard.",
                8,
            ),
        ),
        interests=("agents", "docs", "knowledge"),
    ),
    "cleaning-ceo": Persona(
        id="cleaning-ceo",
        label="CEO, outdoor cleaning company",
        field="crews, routes, weather and invoices",
        game_idea=(
            "Pressure-washer tycoon: send crews to dirty facades, dodge rain, "
            "keep the vans fuelled, and beat last month's revenue before the "
            "season ends."
        ),
        dataset=Dataset(
            filename="jobs.csv",
            columns=("date", "client", "crew", "hours", "revenue_eur", "rain"),
            rows=(
                ("2026-09-01", "Van der Berg", "A", "6", "780", "no"),
                ("2026-09-01", "Gemeente Delft", "B", "8", "1200", "no"),
                ("2026-09-02", "Hotel Zuid", "A", "4", "520", "yes"),
                ("2026-09-03", "Van der Berg", "B", "7", "910", "no"),
                ("2026-09-04", "Bakkerij Smit", "A", "3", "390", "no"),
                ("2026-09-07", "Gemeente Delft", "B", "8", "1200", "yes"),
                ("2026-09-08", "Hotel Zuid", "A", "5", "650", "no"),
                ("2026-09-09", "Parkeergarage Oost", "B", "9", "1350", "no"),
            ),
            question="Which crew earns the most per hour, and does rain change it?",
        ),
        rolinda="Which client pays you the least per hour, and why are you still going there?",
        recipes=(
            Recipe(
                "Quote in thirty seconds",
                "A script that turns a photo description into a quote.",
                "Write quote.py: I type the facade size in square metres and the "
                "dirt level (1 to 3); it prints a quote using the rates in "
                "rates.toml. Add a test.",
                "Three quotes printed, one test green.",
                3,
            ),
            Recipe(
                "Rain plan",
                "Reschedule tomorrow's jobs when the forecast says rain.",
                "Read workspace/data/examples/jobs.csv and the weather in "
                "weather.json; list the "
                "jobs to move, who to call, and draft the message in Dutch. "
                "Do not send anything.",
                "A draft per client, nothing sent.",
                5,
            ),
            Recipe(
                "Invoice reminder loop",
                "Every Friday, list unpaid invoices older than 30 days.",
                "Write a script that reads invoices.csv, prints the overdue ones "
                "sorted by amount, and runs from cron on Friday 09:00.",
                "The list appears on Friday, the crontab line is in the vault.",
                8,
            ),
        ),
        interests=("shell", "data", "agents"),
    ),
    "university-md": Persona(
        id="university-md",
        label="Managing director, university faculty",
        field="programmes, budgets, accreditation and staff",
        game_idea=(
            "Faculty builder: enrol students, fund labs, survive an "
            "accreditation visit, and keep the professors from leaving for "
            "industry."
        ),
        dataset=Dataset(
            filename="enrolments.csv",
            columns=("year", "programme", "students", "budget_keur", "staff"),
            rows=(
                ("2023", "Data Science BSc", "180", "1450", "14"),
                ("2023", "Public Policy MSc", "95", "900", "9"),
                ("2024", "Data Science BSc", "215", "1600", "15"),
                ("2024", "Public Policy MSc", "88", "880", "9"),
                ("2025", "Data Science BSc", "260", "1750", "16"),
                ("2025", "Public Policy MSc", "101", "950", "10"),
                ("2026", "Data Science BSc", "290", "1900", "17"),
                ("2026", "Public Policy MSc", "110", "990", "10"),
            ),
            question="Which programme grows fastest per staff member?",
        ),
        rolinda="If one programme doubles next year, what breaks first, and where is that in the numbers?",
        recipes=(
            Recipe(
                "Accreditation binder index",
                "An index of every document the visit will ask for.",
                "Read docs/ and produce index.md grouped by the accreditation "
                "standard each document supports; flag standards with no "
                "document. Do not write the documents.",
                "Every standard has a document or a red flag.",
                2,
            ),
            Recipe(
                "Students per staff trend",
                "A line chart per programme, 2023 to 2026.",
                "Using workspace/data/examples/enrolments.csv, write "
                "workspace/sql/ratio.sql in DuckDB and a Python chart. One "
                "sentence on what the trend implies.",
                "Chart in workspace/python/out/, sentence in the vault.",
                3,
            ),
            Recipe(
                "Board memo with citations",
                "A memo where every number links to its source file.",
                "Write memo.md for the board: three findings, each with the "
                "file and line it came from. Refuse to state a number you "
                "cannot cite.",
                "Every number has a citation; you checked two.",
                6,
            ),
        ),
        interests=("docs", "knowledge", "agents"),
    ),
    "pabo-teacher": Persona(
        id="pabo-teacher",
        label="Teacher educator (pabo)",
        field="lesson plans, student teachers, classroom observations",
        game_idea=(
            "Classroom quest: thirty first-graders, one lesson plan, and a "
            "fire drill at 10:15. Keep attention above zero and finish the "
            "reading circle."
        ),
        dataset=Dataset(
            filename="lessons.csv",
            columns=("date", "group", "subject", "minutes", "attention", "rating"),
            rows=(
                ("2026-09-07", "1A", "reading", "45", "high", "4"),
                ("2026-09-07", "1B", "maths", "40", "medium", "3"),
                ("2026-09-08", "2A", "reading", "50", "low", "2"),
                ("2026-09-09", "1A", "maths", "45", "high", "5"),
                ("2026-09-10", "2A", "world", "60", "medium", "4"),
                ("2026-09-14", "1B", "reading", "45", "high", "4"),
                ("2026-09-15", "2A", "maths", "40", "low", "2"),
                ("2026-09-16", "1A", "world", "55", "high", "5"),
            ),
            question="Which subject holds attention longest, and in which group?",
        ),
        rolinda="Which lesson would you drop, and what does the attention column say about why?",
        recipes=(
            Recipe(
                "Lesson plan from a learning goal",
                "A 45-minute plan with materials and a check for understanding.",
                "Write a lesson plan for group 1A on 'counting to 20' following "
                "the template in templates/lesson.md. Include one differentiation "
                "for fast finishers. Cite the curriculum goal it serves.",
                "The plan fits the template and names the goal.",
                2,
            ),
            Recipe(
                "Observation notes to feedback",
                "Turn raw observation notes into structured feedback.",
                "Read observations/*.md and write feedback.md per student "
                "teacher: two strengths, one next step, one question. Keep "
                "their own words where possible.",
                "Each student teacher has a file; nothing invented.",
                6,
            ),
            Recipe(
                "Attention chart",
                "Attention by subject and group from lessons.csv.",
                "Write workspace/sql/attention.sql and a Python chart from "
                "workspace/data/examples/lessons.csv. Explain group by in one comment.",
                "The chart matches your gut feeling, or you learned something.",
                3,
            ),
        ),
        interests=("agents", "docs", "knowledge"),
    ),
    "data-engineer": Persona(
        id="data-engineer",
        label="Data engineer",
        field="pipelines, warehouses, orchestration and tests",
        game_idea=(
            "Pipeline defense: rows flow from left to right, schema drift "
            "attacks at night, and you place tests and quarantine tables to "
            "keep the gold layer clean until the CEO's dashboard loads."
        ),
        dataset=Dataset(
            filename="pipeline_runs.csv",
            columns=("run_at", "pipeline", "layer", "rows", "seconds", "status"),
            rows=(
                ("2026-09-15T02:00", "orders", "bronze", "120000", "84", "ok"),
                ("2026-09-15T02:05", "orders", "silver", "119400", "140", "ok"),
                ("2026-09-15T02:12", "orders", "gold", "3120", "22", "ok"),
                ("2026-09-15T02:00", "customers", "bronze", "40000", "31", "ok"),
                ("2026-09-15T02:04", "customers", "silver", "39980", "58", "warn"),
                ("2026-09-16T02:00", "orders", "bronze", "125500", "88", "ok"),
                ("2026-09-16T02:05", "orders", "silver", "0", "3", "fail"),
                ("2026-09-16T02:00", "customers", "bronze", "40210", "30", "ok"),
            ),
            question="Which layer failed last night, and what did the row counts say before it did?",
        ),
        rolinda="If the silver run says zero rows, what did the bronze run say, and why did nobody get paged?",
        recipes=(
            Recipe(
                "Two-file task pattern",
                "A pipeline task as a .py plus a .yaml sidecar with tests.",
                "Create tasks/orders_silver.py and tasks/orders_silver.yaml "
                "(source, target, schedule, owner). The task reads bronze from "
                "DuckDB, dedupes, writes silver. pytest with a fixture CSV.",
                "uv run pytest is green and the yaml validates.",
                3,
            ),
            Recipe(
                "Schema drift guard",
                "A hook that refuses a commit when a CSV header changes.",
                "Write a pre-commit style Claude Code hook (PostToolUse on Edit "
                "and Write) that compares data/*.csv headers to schema.json and "
                "prints the diff. Show me the settings.json block.",
                "Renaming a column produces a loud message.",
                4,
            ),
            Recipe(
                "Nightly run report",
                "Headless agent summarises last night's runs into the vault.",
                "Write a script that runs the provider in print mode over "
                "workspace/data/examples/pipeline_runs.csv and writes "
                "vault/Camp/Runs.md with a "
                "table and one paragraph. Schedule it at 07:00.",
                "Runs.md is updated by the schedule, not by you.",
                8,
            ),
        ),
        interests=("data", "shell", "git", "agents"),
    ),
    "interior-stylist": Persona(
        id="interior-stylist",
        label="Interior stylist",
        field="clients, mood boards, budgets and suppliers",
        game_idea=(
            "Room by room: a client hands you an empty apartment and a budget; "
            "place furniture, match a palette, and hit the reveal before the "
            "movers arrive."
        ),
        dataset=Dataset(
            filename="projects.csv",
            columns=("client", "room", "style", "budget_eur", "spent_eur", "status"),
            rows=(
                ("Jansen", "living", "japandi", "6000", "5400", "done"),
                ("Jansen", "bedroom", "japandi", "3500", "3900", "done"),
                ("De Wit", "kitchen", "industrial", "9000", "4200", "in progress"),
                ("Bakker", "office", "scandi", "2500", "2450", "done"),
                ("Bakker", "living", "scandi", "7000", "1200", "in progress"),
                ("Meijer", "nursery", "soft modern", "3000", "0", "planned"),
                ("De Wit", "living", "industrial", "8000", "8600", "done"),
                ("Visser", "hallway", "japandi", "1500", "1500", "done"),
            ),
            question="Which style goes over budget most often?",
        ),
        rolinda="Which style makes you money and which one makes you sorry, and can the table show it?",
        recipes=(
            Recipe(
                "Mood board brief",
                "A structured brief from a messy client email.",
                "Read client-email.txt and write brief.md: rooms, style words, "
                "must-haves, budget per room, three open questions for the "
                "client. Keep their words.",
                "The client says yes to the brief in one reply.",
                2,
            ),
            Recipe(
                "Budget tracker",
                "Spent versus budget per client and style, with a chart.",
                "Using workspace/data/examples/projects.csv, write "
                "workspace/sql/over_budget.sql and a Python chart of spent "
                "versus budget per style. One sentence on the "
                "worst offender.",
                "The chart shows the style that overruns.",
                3,
            ),
            Recipe(
                "Supplier follow-up",
                "A weekly list of items ordered but not delivered.",
                "Read orders.csv, list items older than 14 days without a "
                "delivery date, and draft one message per supplier. Nothing is "
                "sent.",
                "Drafts exist, nothing sent, the list is right.",
                5,
            ),
        ),
        interests=("agents", "knowledge", "formats"),
    ),
}

DEFAULT_PERSONA = "chief-of-staff"


def get_persona(persona_id: str) -> Persona:
    """Return a persona or raise ValueError naming the valid ids."""
    try:
        return PERSONAS[persona_id]
    except KeyError:
        raise ValueError(
            f"unknown persona {persona_id!r}; one of: {', '.join(PERSONAS)}"
        ) from None
