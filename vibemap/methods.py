"""Note-taking methods the learner can bootstrap into the vault.

Each method is a verified description (origin, idea, fit), a set of empty
folders under ``vault/Camp/Methods/<name>/``, Obsidian templates under
``vault/Camp/_templates/<id>/``, and the body of a hub note
``Method - <name>`` that the CLI writes and links from Tonight. The data lives
here; ``vibe vault method <id>`` does the writing.

Every claim about a method traces to the primary sources in its ``sources``
tuple; the hub note repeats those URLs so the learner can check them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Template:
    """One Obsidian template file.

    Attributes:
        filename: File name inside ``_templates/<method id>/``.
        body: Note text using the core Templates variables ``{{title}}``,
            ``{{date}}`` and ``{{time}}`` (a colon adds a Moment.js format).
    """

    filename: str
    body: str


@dataclass(frozen=True, slots=True)
class Method:
    """A note-taking method and everything needed to start it in the vault.

    Attributes:
        id: Lowercase-dashes identifier used on the command line.
        name: Display name; also the folder name under ``Methods/``.
        origin: Who, where and when, as verified against the sources.
        what: The idea and why people swear by it, in two or three sentences.
        when: The person or the work it suits, in one sentence.
        folders: Folders created empty under ``Methods/<name>/``.
        templates: Templates written to ``_templates/<id>/``.
        hub: Markdown body of the hub note ``Method - <name>``: no H1 (the CLI
            adds frontmatter and the title), the folder list, the daily loop,
            one worked example and a Sources section.
        sources: ``(label, url)`` pairs, the primary sources.
    """

    id: str
    name: str
    origin: str
    what: str
    when: str
    folders: tuple[str, ...]
    templates: tuple[Template, ...]
    hub: str
    sources: tuple[tuple[str, str], ...]


def _hub(body: str, sources: tuple[tuple[str, str], ...]) -> str:
    """Append the Sources section, the back links and the tag to a hub body."""
    lines = [body.rstrip(), "", "## Sources"]
    lines += [f"- {label}: {url}" for label, url in sources]
    lines += ["", "Back to [[Tonight]] · [[Resources]]", "", "#tech", ""]
    return "\n".join(lines)


def _front(tags: str) -> str:
    """The frontmatter block every template starts with."""
    return f'---\ntitle: "{{{{title}}}}"\ndate: "{{{{date}}}}"\ntags: [{tags}]\n---\n'


# ---- Zettelkasten ---------------------------------------------------------

_ZETTEL_SOURCES = (
    (
        "Luhmann, Communicating with Slip Boxes (translation)",
        "https://luhmann.surge.sh/communicating-with-slip-boxes",
    ),
    (
        "Niklas Luhmann-Archiv, Bielefeld University",
        "https://www.uni-bielefeld.de/fakultaeten/soziologie/forschung/luhmann-archiv/",
    ),
    ("Ahrens, How to Take Smart Notes", "https://takesmartnotes.com/"),
)

_ZETTEL_TEMPLATES = (
    Template(
        "Zettel.md",
        _front("zettelkasten")
        + """# {{title}}
id: {{date:YYYYMMDDHHmm}}

One idea, in your own words, in a paragraph you could paste into a draft.
To continue this zettel later, make a new one with a letter appended to the
id (Luhmann's 57/12 became 57/12a) rather than editing this one.

## Links
- continues [[ ]] because
- contradicts [[ ]] because

## Source
- [[Bibliography - ]] page

#zettelkasten
""",
    ),
    Template(
        "Bibliography.md",
        _front("zettelkasten, source")
        + """# {{title}}
Author, title, year, where to find it. Luhmann kept these slips apart from
the ideas so a source could be found by author or keyword.

## Page references
- p. : what is there, in a few words

## Zettels drawn from it
- [[ ]]

#zettelkasten
""",
    ),
    Template(
        "Keyword.md",
        _front("zettelkasten, register")
        + """# {{title}}
Register entry: the zettels that touch this keyword, newest first. One or two
entry points per keyword are enough; the links between zettels do the rest.

- {{date}} [[ ]]

#zettelkasten
""",
    ),
)

_ZETTEL_HUB = """\
Luhmann's slip box: one idea per slip, a fixed number per slip so new slips
can branch off old ones, and links by number so the box talks back. Notes go
in `Methods/Zettelkasten/`; the templates are in `_templates/zettelkasten/`.

## Folders
- `Zettels/`: one idea per note, numbered, linked
- `Bibliography/`: one note per source, the slip Luhmann kept separately
- `Register/`: one note per keyword listing the zettels that touch it

## Daily loop
1. Read with a pen: write page references on the source's bibliography note.
2. For each idea worth keeping, insert the Zettel template and write it in
   your own words, one idea, in a paragraph you could paste into a draft.
3. Keep the id the template stamps; to continue an existing zettel, append a
   letter to its id instead of starting a new branch.
4. Link it to at least one older zettel and say why (continues, contradicts,
   example of). Luhmann: "you can add as many references to them as you may
   want" because the numbers never move.
5. Add it under one or two keywords in the register. Never file by topic; the
   register and the links are the only way in, on purpose.

## Worked example

```markdown
# Links make a slip box a conversation partner
id: 202609162115

Luhmann's box surprised him because links by fixed number let a slip sit in
several trains of thought at once. The surprise is the point: a box that only
returns what you filed is a cupboard, not a partner.

## Links
- continues [[Fixed ids let notes branch without reordering]]
- contradicts [[Folders are enough for a small vault]] because folders give
  a note one home

## Source
- [[Bibliography - Luhmann, Communicating with slip boxes]] section 2
```
"""

# ---- PARA -----------------------------------------------------------------

_PARA_SOURCES = (("Forte, The PARA Method", "https://fortelabs.com/blog/para/"),)

_PARA_TEMPLATES = (
    Template(
        "Project.md",
        _front("para, project")
        + """# {{title}}

Outcome: what done looks like, in one sentence.
Deadline:
Area: [[Area - ]]

## Next action
- [ ] the very next physical step

## Notes
- {{date}}

## Resources
- [[Resource - ]]

#para
""",
    ),
    Template(
        "Area.md",
        _front("para, area")
        + """# {{title}}

Standard: what good looks like here. Ongoing, no end date.

## Active projects
- [[Project - ]]

## Notes
- {{date}}

#para
""",
    ),
    Template(
        "Resource.md",
        _front("para, resource")
        + """# {{title}}

Why this topic interests me, in one line.

## Notes
- {{date}}

## Used by
- [[Project - ]]

#para
""",
    ),
)

_PARA_HUB = """\
Four folders ordered by how actionable they are. Projects have a goal and an
end, Areas never end, Resources are interests, Archives are the cold store. A
note has one home: the work you are doing now. Notes go in `Methods/PARA/`;
the templates are in `_templates/para/`.

## Folders
- `Projects/`: one note per short-term effort with a goal and a deadline
- `Areas/`: one note per responsibility you maintain (health, team, taxes)
- `Resources/`: one note per topic you are interested in
- `Archives/`: finished projects, dropped areas, dead interests, kept whole

## Daily loop
1. Open the project you are working on today; everything for it is there.
2. Capture new material into that project note, or into the area or resource
   it belongs to. If it belongs to nothing yet, it goes in Resources.
3. Keep every project note's "Next action" line true before you close it.
4. When a project ends, move its note to Archives unchanged.
5. Every week, glance down Projects: fewer than you thought is fine; more
   than you can name is the signal to archive or merge.

## Worked example

```markdown
# Ship the game to a public URL

Outcome: workspace/game/index.html at a GitHub Pages URL a friend can open on a phone.
Deadline: 2026-09-23
Area: [[Area - Vibe Code Camp]]

## Next action
- [ ] enable Pages on the repo: branch main, folder /game

## Notes
- 2026-09-16 the Pages workflow is already in .github/workflows; only the
  repo setting is left

## Resources
- [[Resource - GitHub Pages]]
```
"""

# ---- Johnny.Decimal -------------------------------------------------------

_JD_SOURCES = (
    (
        "Johnny.Decimal, Introduction",
        "https://johnnydecimal.com/10-19-concepts/11-core/11.01-introduction/",
    ),
    (
        "Johnny.Decimal, The JDex",
        "https://johnnydecimal.com/10-19-concepts/11-core/11.05-the-index/",
    ),
    (
        "Johnny.Decimal, About us",
        "https://johnnydecimal.com/support/about-legal/about-us",
    ),
)

_JD_TEMPLATES = (
    Template(
        "JDex.md",
        _front("johnny-decimal, index")
        + """# {{title}}
The JDex: the master record of every ID. One line per ID, grouped by area and
category; each ID's own note holds its locations and keywords.

## 00-09 System
- 00.01 This index

## 10-19 Life admin
### 15 Travel
- 15.22 Travel insurance

## 20-29 Work
### 21
- 21.01

## 30-39 Learning
### 31
- 31.01

#johnny-decimal
""",
    ),
    Template(
        "ID.md",
        _front("johnny-decimal")
        + """# {{title}}
Name this note "AC.ID Name", for example "15.22 Travel insurance"; the title
is the index entry. The rest can stay blank, but locations help.

Location: where the real files live (mail, cloud, disk)
Keywords: the words you would search for

## Log
- {{date}}

#johnny-decimal
""",
    ),
)

_JD_HUB = """Ten areas, up to ten categories each, numbered IDs inside, and an index
(the JDex) that says where every ID lives. No level ever offers more than ten
choices. Notes go in `Methods/Johnny.Decimal/`; the templates are in
`_templates/johnny-decimal/`.

## Folders
- `00-09 System/`: the JDex and this method's own admin
- `10-19 Life admin/`, `20-29 Work/`, `30-39 Learning/`: starter areas;
  rename them, keep the ranges

## Daily loop
1. Before you make anything, find or create its ID in the JDex
   (area, category, id: for example 15.22 is area 10-19, category 15).
2. Name the file or note with the ID first: `15.22 Travel insurance`.
3. Put the ID's note in its category folder; in it, say where the real files
   live (mail, cloud, disk) and add the keywords you would search for.
4. Never add an eleventh category; if you want to, split an area instead.
5. Say the number out loud when you talk about the thing. If it does not
   roll off the tongue, the system has drifted; fix the JDex.

## Worked example

```markdown
# 15.22 Travel insurance

Location: Dropbox /15.22 (policy PDF); mail label 15.22
Keywords: insurance, policy, claim, travel

## Log
- 2026-09-16 renewed for a year; the claim line is on page 1 of the PDF
```
"""

# ---- LYT ------------------------------------------------------------------

_LYT_SOURCES = (
    ("Linking Your Thinking", "https://www.linkingyourthinking.com/"),
    (
        "LYT Kit, MOCs Overview",
        "https://notes.linkingyourthinking.com/Cards/MOCs+Overview",
    ),
    ("LYT Kit, Home", "https://notes.linkingyourthinking.com/Home"),
    ("LYT Blog, Maps", "https://blog.linkingyourthinking.com/maps/"),
)

_LYT_TEMPLATES = (
    Template(
        "MOC.md",
        _front("lyt, moc")
        + """# {{title}}

Why this map: the squeeze that made you draw it, in one line.

## Start here
- [[ ]]: why it is on this map

## Then
- [[ ]]:

## Related maps
- [[Home]]

#lyt
""",
    ),
    Template(
        "Home.md",
        _front("lyt, home")
        + """# {{title}}

Your launchpad and home base. Where would you like to go?

## Sensemaking
- [[Thinking MOC]]
- [[Daily notes]]

## Things
- [[Sources MOC]]
- [[Concepts MOC]]
- [[People MOC]]

## Action and reflection
- [[Efforts MOC]]

#lyt
""",
    ),
)

_LYT_HUB = """Small linked notes, and when a topic outgrows your head, a Map of Content:
a note that links the related notes in context. Maps are overlays, not
folders, so a note can sit on many maps; a Home note lists the maps. Notes go
in `Methods/LYT/`; the templates are in `_templates/lyt/`.

## Folders
- `Maps/`: the Home note and every MOC
- `Notes/`: the ideas, one per note
- `Sources/`: books, talks and articles, one note each

## Daily loop
1. Write the idea as its own note in `Notes/` and link it to whatever it
   touches while it is fresh.
2. Feel for Milo's "Mental Squeeze Point": when a cluster of notes is too big
   to hold in your head, that is the signal to make a map.
3. Insert the MOC template, pull the related notes onto it, and write one
   line per link saying why it is there.
4. Link the new map from Home and from any map it grew out of.
5. Revisit a map every time you open it: reorder, add a sentence, split it
   when it squeezes again. Maps are "non-restrictive, non-limiting".

## Worked example

```markdown
# Agents MOC

Why this map: after four evenings the agent notes stopped fitting in my head.

## Foundations
- [[Context window and prompts]]: everything else assumes this
- [[From base model to assistant]]: what the training adds

## Making them reliable
- [[Deterministic checks]]: the check that runs without you
- [[Evals - measure the agent, not the vibe]]

## Related maps
- [[Home]] · [[Terminal MOC]]
```
"""

# ---- Evergreen notes ------------------------------------------------------

_EVERGREEN_SOURCES = (
    (
        "Matuschak, Evergreen notes",
        "https://notes.andymatuschak.org/Evergreen_notes",
    ),
    (
        "Matuschak, Prefer note titles with complete phrases to sharpen claims",
        "https://notes.andymatuschak.org/Prefer_note_titles_with_complete_"
        "phrases_to_sharpen_claims",
    ),
    (
        "Matuschak, About these notes",
        "https://notes.andymatuschak.org/About_these_notes",
    ),
)

_EVERGREEN_TEMPLATES = (
    Template(
        "Evergreen.md",
        _front("evergreen")
        + """# {{title}}

The title is the claim, a complete phrase. One idea only; if a second one
shows up, it gets its own note. Write for yourself.

The argument, in a paragraph or two, until the title is earned.

Builds on: [[ ]]
Contradicts: [[ ]]
Leads to: [[ ]]
Source: [[Source - ]]

#evergreen
""",
    ),
    Template(
        "Source.md",
        _front("evergreen, source")
        + """# {{title}}
Who, what, year, where to find it.

## Reading notes
- {{date}} p. : the point, in my words

## Claims to grow into evergreen notes
- [[ ]]

#evergreen
""",
    ),
)

_EVERGREEN_HUB = """\
Notes written to last: one idea each, about a concept rather than a source
or a project, densely linked, filed by association, and titled with the claim
they make so the body has to earn the title. Notes go in
`Methods/Evergreen notes/`; the templates are in `_templates/evergreen/`.

## Folders
- `Evergreen/`: the notes that last; every title is a complete phrase
- `Sources/`: reading notes, the raw material evergreen notes distil

## Daily loop
1. Read and jot in a source note; do not try to make it pretty.
2. When a thought recurs, insert the Evergreen template and title it as the
   claim: "Fixed ids let notes branch without reordering", not "Note ids".
3. Write the body until it supports the title. If you cannot title it
   sharply, the thinking is muddy or it is two notes; split it.
4. Link it densely: what it builds on, what it contradicts, where it leads.
   Prefer links to folders; the ontology is the links.
5. Revise old evergreen notes whenever you pass through them. They are never
   finished.

## Worked example

```markdown
# A title that states the claim keeps a note to one idea

If the title is a full sentence, the body has one job: back it up. A title
like "Note ids" invites a list; "Fixed ids let notes branch without
reordering" invites an argument, and shows at once when the note has drifted
into a second topic.

Builds on: [[Evergreen notes should be atomic]]
Leads to: [[Questions make good provisional titles]]
Source: [[Source - Matuschak, working notes]]
```
"""

# ---- Cornell notes --------------------------------------------------------

_CORNELL_SOURCES = (
    (
        "Cornell Learning Strategies Center, The Cornell Note Taking System",
        "https://lsc.cornell.edu/how-to-study/taking-notes/cornell-note-taking-system/",
    ),
    (
        "Cornell LSC handout, The Cornell Note-taking System (PDF)",
        "https://lsc.cornell.edu/wp-content/uploads/2016/10/"
        "Cornell-NoteTaking-System.pdf",
    ),
)

_CORNELL_TEMPLATES = (
    Template(
        "Cornell.md",
        _front("cornell")
        + """# {{title}}
Source: · Date: {{date}}

## Notes
Record during the lecture or reading: telegraphic sentences, one per line.
-

## Cues
After, as soon as you can: a question or a cue word per block of notes.
-

## Summary
Afterwards, in your own words, one or two sentences for the whole note.

Recited: [ ] · Reflected: [ ] · Reviewed: [ ] (ten minutes a week)

#cornell
""",
    ),
)

_CORNELL_HUB = """\
Walter Pauk's page: a wide note-taking column, a narrow cue column and a
summary strip. In Markdown the columns become sections, and the cue section
is what turns every note into a self-test. Notes go in
`Methods/Cornell notes/`; the template is in `_templates/cornell/`.

## Folders
- `Lectures/`: one note per lecture, talk or meeting
- `Readings/`: one note per chapter or paper

## Daily loop
1. Record: during the lecture or reading, write telegraphic sentences under
   Notes. Do not stop to tidy.
2. Questions: as soon after as you can, write a question or a cue word under
   Cues for each block of notes. Writing the question is the studying.
3. Recite: fold the Notes heading away, read only the Cues, and answer aloud
   in your own words.
4. Reflect: ask what the facts mean, what principle they rest on and how they
   fit what you already know; write two sentences under Summary.
5. Review: ten minutes every week over all previous notes, cues first.

## Worked example

```markdown
# Evening 2, how these models actually work
Source: [[Evening 2]] · Date: 2026-09-16

## Notes
- base model predicts the next token; assistant = base + tuning on examples
- the context window is the whole short-term memory; nothing persists
- attention: every token looks at every other; cost grows with length

## Cues
- What turns a base model into an assistant?
- Why does a long prompt cost more than a short one?
- Where does memory live between two calls?

## Summary
An assistant is a base model plus training on examples of being helpful; all
it knows about you right now is in the context window, so the prompt is the
memory.
```
"""

# ---- Bullet Journal -------------------------------------------------------

_BUJO_SOURCES = (
    ("Bullet Journal, Our story", "https://bulletjournal.com/pages/story"),
    (
        "Bullet Journal, What is Rapid Logging?",
        "https://bulletjournal.com/blogs/faq/"
        "what-is-rapid-logging-understand-rapid-logging-bullets-and-signifiers",
    ),
    (
        "Bullet Journal, How to Bullet Journal",
        "https://bulletjournal.com/pages/how-to-bullet-journal",
    ),
)

_BUJO_TEMPLATES = (
    Template(
        "Daily log.md",
        _front("bullet-journal, daily")
        + """# {{title}}

Key: • task   x done   > migrated   < scheduled   o event   - note
Signifiers, to the left of a bullet: * priority   ! inspiration

• a task
o an event, with its time
- a note: a fact, an idea, an observation

#bullet-journal
""",
    ),
    Template(
        "Monthly log.md",
        _front("bullet-journal, monthly")
        + """# {{title}}

## Calendar page
One line per day: the date, then events and anything worth a mark.
- 01
- 02

## Task page
Tasks for the month. At month end migrate what still matters with >, strike
through the rest.
• a task

#bullet-journal
""",
    ),
    Template(
        "Index.md",
        _front("bullet-journal, index")
        + """# {{title}}
Topics and where they live; add a line whenever you start a collection.

- Future log: [[Future log {{date:YYYY}}]]
- Monthly logs: [[{{date:YYYY-MM}}]]
- Collections:
  - [[ ]]

#bullet-journal
""",
    ),
)

_BUJO_HUB = """\
Rapid logging: short entries with a bullet key, kept in a daily log, rolled
up monthly and yearly, found again through an index. The monthly migration,
where you rewrite what still matters and strike the rest, is the method.
Notes go in `Methods/Bullet Journal/`; the templates are in
`_templates/bullet-journal/`.

## Folders
- `Daily/`: one log per day
- `Monthly/`: one log per month, a calendar page and a task page
- `Future/`: the future log, one note per year
- `Collections/`: anything with a topic of its own (a trip, a reading list)

## Daily loop
1. Open today's daily log (the template carries the key) and rapid-log as
   the day happens: a dot for a task, o for an event, a dash for a note.
2. Keep entries short; a signifier to the left (* priority, ! inspiration)
   adds context without more words.
3. Close a task with x. If it needs another day, leave it; you migrate at
   the end of the month, not tonight.
4. At the start of each month set up the monthly log and migrate open tasks
   with >. Carroll: "if it isn't worth the effort to rewrite, then it's
   probably not that important. Get rid of it."
5. When a topic outgrows the daily log, give it a collection and list it in
   the index.

## Worked example

```markdown
# 2026-09-16

Key: • task   x done   > migrated   < scheduled   o event   - note
Signifiers, to the left of a bullet: * priority   ! inspiration

* • finish the PARA project note before 21:00
x • run the vault lint
o 20:00 Data Warehouse stop
- DuckDB reads a CSV straight from its path; no import step
! • try Cornell notes on Evening 2
```
"""

# ---- Daily notes and weekly review ----------------------------------------

_DAILY_SOURCES = (
    (
        "Obsidian Help, Daily notes core plugin",
        "https://obsidian.md/help/plugins/daily-notes",
    ),
    (
        "Obsidian Help, Templates core plugin",
        "https://obsidian.md/help/plugins/templates",
    ),
    (
        "David Allen Company, GTD Weekly Review checklist (PDF)",
        "https://gettingthingsdone.com/wp-content/uploads/2014/10/"
        "Weekly_Review_Checklist.pdf",
    ),
    (
        "David Allen Company, What is GTD",
        "https://gettingthingsdone.com/what-is-gtd/",
    ),
)

_DAILY_TEMPLATES = (
    Template(
        "Daily.md",
        _front("daily")
        + """# {{title}}

## Log
- {{time}}

## Tasks
- [ ]

## Learned
-

## Review (Fridays)
Run [[Weekly review {{date:YYYY-[W]WW}}]] top to bottom:
- [ ] Get Clear: collect loose ends, inbox to zero, empty your head
- [ ] Get Current: action lists, calendar back and forward, waiting for
- [ ] Get Creative: someday/maybe, one bold idea

#daily
""",
    ),
    Template(
        "Weekly review.md",
        _front("weekly-review")
        + """# {{title}}
Week of {{date}}. David Allen's checklist, every seven to ten days.

## Get Clear
- [ ] Collect loose papers and materials into the inbox
- [ ] Get "in" to zero: process every note, mail and message
- [ ] Empty your head: write down uncaptured projects, actions, waiting-fors

## Get Current
- [ ] Review action lists: mark off done, record further steps
- [ ] Review the past calendar for leftover actions and reference
- [ ] Review the upcoming calendar and capture what it triggers
- [ ] Review the waiting-for list: chase, or check off what arrived
- [ ] Review projects: at least one current action on each
- [ ] Review any relevant checklists

## Get Creative
- [ ] Review someday/maybe: promote what is now active, delete the rest
- [ ] Be creative and courageous: add one bold idea to the system

## Covered
- [[ ]] to [[ ]] (daily notes)

#weekly-review
""",
    ),
)

_DAILY_HUB = """The lowest-friction start: Obsidian opens or creates today's note, a
template gives it a shape, and once a week David Allen's checklist gets you
clear, current and creative. The daily note captures; the weekly review keeps
it from rotting. Notes go in `Methods/Daily notes and weekly review/`; the
templates are in `_templates/daily-weekly/`.

## Folders
- `Daily/`: one note per day, named YYYY-MM-DD by the plugin
- `Weekly/`: one review per week

## Daily loop
1. Open today's note: the calendar icon in the ribbon, or the "Open today's
   daily note" command. In Settings, Core plugins, Daily notes, point the
   template at `_templates/daily-weekly/Daily.md` and the new file location
   at this method's `Daily/` folder.
2. Log as you go: what happened, what you decided, what you learned, one
   line each; tasks as `- [ ]`.
3. Before you close the laptop, tick what is done and move the rest to
   tomorrow or to the project it belongs to.
4. On Friday, insert the Weekly review template in `Weekly/` and walk it top
   to bottom: Get Clear, Get Current, Get Creative.
5. Link the review to the daily notes it covered and to what it changed.

## Worked example

```markdown
# 2026-09-16

## Log
- 18:00 Innovation Hub: the game ships in one file; double-click works
- decided: keep the scores.csv columns as they are, sql/ depends on them

## Tasks
- [x] run the vault lint
- [ ] write the Cornell note for Evening 2

## Learned
- the Templates plugin takes Moment.js tokens after a colon: {{date:dddd}}

## Review (Fridays)
Run [[Weekly review 2026-W38]] top to bottom:
- [ ] Get Clear · [ ] Get Current · [ ] Get Creative
```
"""

# ---- Registry -------------------------------------------------------------

METHODS: dict[str, Method] = {
    "zettelkasten": Method(
        id="zettelkasten",
        name="Zettelkasten",
        origin=(
            "Niklas Luhmann, sociologist at Bielefeld University: about 90,000 "
            "slips written between 1951 and 1996, held by the Niklas "
            "Luhmann-Archiv since the university bought his estate in 2011."
        ),
        what=(
            "One idea per slip, a fixed number per slip so later slips can "
            "branch off it (57/12 becomes 57/12a), and slips that point at each "
            "other by number. Luhmann said the box became 'a kind of secondary "
            "memory, an alter ego' he could talk to, because the links surface "
            "connections the author had forgotten he made."
        ),
        when=(
            "Suits a researcher or writer who reads a lot and wants the notes "
            "to argue back years later."
        ),
        folders=("Zettels", "Bibliography", "Register"),
        templates=_ZETTEL_TEMPLATES,
        hub=_hub(_ZETTEL_HUB, _ZETTEL_SOURCES),
        sources=_ZETTEL_SOURCES,
    ),
    "para": Method(
        id="para",
        name="PARA",
        origin=(
            "Tiago Forte, Forte Labs; the canonical write-up is on fortelabs.com "
            "(post dated 2023-02-24, last updated 2026-04-15)."
        ),
        what=(
            "Four top-level folders ordered by actionability: Projects "
            "('short-term efforts ... with a certain goal in mind'), Areas "
            "('important parts of your work and life that require ongoing "
            "attention'), Resources (topics you are interested in) and Archives "
            "(anything inactive from the other three). People swear by it "
            "because a note has exactly one home, and that home is the work "
            "you are doing now rather than a subject taxonomy."
        ),
        when=(
            "Suits someone juggling many projects who wants everything for one "
            "project in one place."
        ),
        folders=("Projects", "Areas", "Resources", "Archives"),
        templates=_PARA_TEMPLATES,
        hub=_hub(_PARA_HUB, _PARA_SOURCES),
        sources=_PARA_SOURCES,
    ),
    "johnny-decimal": Method(
        id="johnny-decimal",
        name="Johnny.Decimal",
        origin=(
            "Johnny Noble, Australia: built in 2010 to file a dance performance, "
            "used privately for a decade, published at johnnydecimal.com in "
            "2015, now run full time with Lucy Butcher."
        ),
        what=(
            "Ten areas (10-19, 20-29 ...), each with up to ten categories (11, "
            "12 ...), each holding numbered IDs (15.22). Everything you own "
            "gets one short number you can say aloud, and an index (the JDex, "
            "one note per ID) records where the thing actually lives. It works "
            "because no level ever offers more than ten choices."
        ),
        when=(
            "Suits someone drowning in folders across mail, cloud and disk who "
            "wants one number to find anything."
        ),
        folders=(
            "00-09 System",
            "10-19 Life admin",
            "20-29 Work",
            "30-39 Learning",
        ),
        templates=_JD_TEMPLATES,
        hub=_hub(_JD_HUB, _JD_SOURCES),
        sources=_JD_SOURCES,
    ),
    "lyt": Method(
        id="lyt",
        name="LYT",
        origin=(
            "Nick Milo, Linking Your Thinking (linkingyourthinking.com); Maps "
            "of Content 'came alive in 2020 at the start of the age of linked "
            "notes', and the LYT Kit (now Ideaverse for Obsidian) ships a Home "
            "note and example maps."
        ),
        what=(
            "Notes stay small and linked; when a topic outgrows your head "
            "(Milo's 'Mental Squeeze Point') you write a Map of Content, 'a "
            "cluster of information that maps things in context with other "
            "things'. Maps are non-restrictive overlays, so one note can sit "
            "on several maps, and a Home note is the launchpad that lists them."
        ),
        when=(
            "Suits a thinker who wants structure to emerge from the notes "
            "rather than be imposed by folders."
        ),
        folders=("Maps", "Notes", "Sources"),
        templates=_LYT_TEMPLATES,
        hub=_hub(_LYT_HUB, _LYT_SOURCES),
        sources=_LYT_SOURCES,
    ),
    "evergreen": Method(
        id="evergreen",
        name="Evergreen notes",
        origin=(
            "Andy Matuschak, in his public working notes at "
            "notes.andymatuschak.org (undated; he calls them 'roughly my "
            "thinking environment')."
        ),
        what=(
            "Evergreen notes are written and revised over years, across "
            "projects. They should be atomic, concept-oriented, densely "
            "linked, filed by association rather than hierarchy, and written "
            "for yourself. The title is a complete phrase that states the "
            "claim, which 'puts pressure on me to adequately support the "
            "claim in the body'."
        ),
        when=(
            "Suits a writer or researcher who wants notes that compound into essays."
        ),
        folders=("Evergreen", "Sources"),
        templates=_EVERGREEN_TEMPLATES,
        hub=_hub(_EVERGREEN_HUB, _EVERGREEN_SOURCES),
        sources=_EVERGREEN_SOURCES,
    ),
    "cornell": Method(
        id="cornell",
        name="Cornell notes",
        origin=(
            "Walter Pauk, professor of education at Cornell University, in his "
            "book How to Study in College; Cornell's Learning Strategies Center "
            "still teaches it, and its handout adapts the 7th edition (2001)."
        ),
        what=(
            "The page is split into a 6-inch note-taking column, a 2.5-inch cue "
            "column and a 2-inch summary strip. Record during the lecture, "
            "write questions in the cue column afterwards, then recite with "
            "the notes covered, reflect, and review for ten minutes a week. It "
            "works because the cue column turns every page into a self-test."
        ),
        when=(
            "Suits a student, or anyone learning from lectures, talks and dense "
            "reading."
        ),
        folders=("Lectures", "Readings"),
        templates=_CORNELL_TEMPLATES,
        hub=_hub(_CORNELL_HUB, _CORNELL_SOURCES),
        sources=_CORNELL_SOURCES,
    ),
    "bullet-journal": Method(
        id="bullet-journal",
        name="Bullet Journal",
        origin=(
            "Ryder Carroll, a digital designer in New York; bulletjournal.com "
            "launched on 8 August 2013 with a tutorial video."
        ),
        what=(
            "Rapid logging: short entries with a bullet key (a dot for a task, "
            "O for an event, a dash for a note; X done, > migrated, < "
            "scheduled; signifiers such as * priority and ! inspiration). "
            "Entries live in a daily log, roll up into a monthly log and a "
            "future log, and an index lists every collection. Migration, "
            "rewriting what still matters, is the filter that keeps it honest."
        ),
        when=(
            "Suits someone who wants one running log for tasks, events and "
            "thoughts, and a monthly moment of triage."
        ),
        folders=("Daily", "Monthly", "Future", "Collections"),
        templates=_BUJO_TEMPLATES,
        hub=_hub(_BUJO_HUB, _BUJO_SOURCES),
        sources=_BUJO_SOURCES,
    ),
    "daily-weekly": Method(
        id="daily-weekly",
        name="Daily notes and weekly review",
        origin=(
            "Two halves: Obsidian's Daily notes core plugin (obsidian.md/help), "
            "which 'opens a note based on today's date, or creates it if it "
            "doesn't exist', and David Allen's GTD Weekly Review checklist "
            "(The David Allen Company, gettingthingsdone.com)."
        ),
        what=(
            "Every day gets one note, created by the plugin from a template, "
            "holding the log, the tasks and the ideas of the day. Once a week "
            "you run Allen's checklist in three moves: Get Clear (collect, "
            "inbox to zero, empty your head), Get Current (action lists, "
            "calendar back and forward, waiting-for, projects) and Get "
            "Creative (someday/maybe). The daily note is the capture; the "
            "weekly review is what keeps it from rotting."
        ),
        when=(
            "Suits anyone who wants the lowest-friction start and a ritual that "
            "scales with everything else on this menu."
        ),
        folders=("Daily", "Weekly"),
        templates=_DAILY_TEMPLATES,
        hub=_hub(_DAILY_HUB, _DAILY_SOURCES),
        sources=_DAILY_SOURCES,
    ),
}


def get_method(method_id: str) -> Method:
    """Return a method or raise ValueError naming the valid ids."""
    try:
        return METHODS[method_id]
    except KeyError:
        raise ValueError(
            f"unknown method {method_id!r}; one of: {', '.join(METHODS)}"
        ) from None
