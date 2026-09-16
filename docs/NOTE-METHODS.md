# Note-taking methods

Eight well-respected ways to keep notes, each one command away:

```sh
uv run grimoire vault method <id>
```

Each method gets a folder under `vault/Grimoire/Methods/<name>/`, templates under `vault/Grimoire/_templates/<id>/`, and a hub note `Method - <name>` linked from [[Tonight]]. Every claim below was checked against the author's own page on 2026-09-16; the URLs are at the end.

## At a glance

| Method (`id`) | Origin | Best for | Unit of note | How links work | The trap |
|---|---|---|---|---|---|
| Zettelkasten (`zettelkasten`) | Niklas Luhmann, Bielefeld; about 90,000 slips, 1951 to 1996 | research, long writing | one idea with a fixed id | by id, with a reason; a keyword register is the way in | collecting quotes instead of writing ideas in your own words |
| PARA (`para`) | Tiago Forte, Forte Labs | many concurrent projects | a project, area or resource note | folders by actionability; links optional | curating Resources, never opening Projects |
| Johnny.Decimal (`johnny-decimal`) | Johnny Noble, Australia; built 2010, published 2015 | files spread over mail, cloud and disk | one note per numbered ID | the JDex index says where each ID lives | an eleventh category |
| LYT (`lyt`) | Nick Milo, Linking Your Thinking; MOCs from 2020 | emergent structure | a small note, gathered by maps | Maps of Content, a Home note on top | maps before the squeeze |
| Evergreen notes (`evergreen`) | Andy Matuschak, notes.andymatuschak.org | notes that compound into writing | one claim, title as a complete phrase | dense associative links, no hierarchy | vague titles that let a note sprawl |
| Cornell notes (`cornell`) | Walter Pauk, Cornell University | lectures, talks, dense reading | one page: notes, cues, summary | the cue column ties notes to questions | skipping the cues; the page is only a transcript |
| Bullet Journal (`bullet-journal`) | Ryder Carroll, New York, 8 August 2013 | one running log of tasks, events, thoughts | a rapid-logged line | an index of collections; migration carries tasks forward | decorating instead of migrating |
| Daily notes and weekly review (`daily-weekly`) | Obsidian Daily notes plugin plus David Allen's GTD Weekly Review | the lowest-friction start | one note per day, one review per week | the review links the days it covered | daily notes without the review |

## The methods

**Zettelkasten.** One idea per slip, a fixed number per slip so a new slip can branch off an old one (57/12 became 57/12a), links by number, and a keyword register as the way in. Luhmann called the box "a kind of secondary memory, an alter ego". Templates: a zettel (id, one idea, links, source), a bibliography slip, a keyword entry.

**PARA.** Forte's four folders are ordered by actionability: Projects are "short-term efforts ... with a certain goal in mind", Areas "require ongoing attention", Resources are interests, Archives are anything inactive. Everything for the project you are working on sits in one place. Templates: a project note (outcome, deadline, next action), an area note, a resource note.

**Johnny.Decimal.** Ten areas (10-19, 20-29 ...), ten categories each (11, 12 ...), numbered IDs inside (15.22), and the JDex, "the master record of every ID", which says where the files live. Noble built it in 2010 to file a dance performance and keeps his JDex in a notes app. Templates: the JDex and a one-note-per-ID entry.

**LYT.** Milo's Map of Content is "a cluster of information that maps things in context with other things", drawn when you hit the "Mental Squeeze Point" and a topic no longer fits in your head. Maps are "non-restrictive, non-limiting" overlays; a Home note, "your launchpad and home base", lists them. Templates: an MOC and a Home note.

**Evergreen notes.** Matuschak's rules: evergreen notes should be atomic, concept-oriented and densely linked, organised by association rather than hierarchy, and written for yourself. A title that is a complete phrase "puts pressure on me to adequately support the claim in the body". Templates: an evergreen note with the title-as-claim rule, and a source note.

**Cornell notes.** Pauk's page has a 6-inch note-taking column, a 2.5-inch cue column and a 2-inch summary; the steps are Record, Questions, Recite, Reflect and Review ("at least ten minutes every week"). In Markdown the columns become sections, and folding the Notes heading is the recite step. Template: Notes, Cues, Summary.

**Bullet Journal.** Rapid logging: a dot for a task, O for an event, a dash for a note; X done, > migrated, < scheduled; signifiers such as * and ! to the left. A daily log rolls into a monthly log and a future log; an index lists the collections. Migration is the filter: "if it isn't worth the effort to rewrite, then it's probably not that important." Templates: a daily log with the key, a monthly log, an index.

**Daily notes and weekly review.** The Daily notes plugin "opens a note based on today's date, or creates it if it doesn't exist" and fills it from a template. Allen's Weekly Review runs Get Clear (collect, inbox to zero, empty your head), Get Current (action lists, calendar both ways, waiting-for, projects) and Get Creative (someday/maybe). Templates: a daily note with the review checklist, and a full weekly review.

## Bootstrap

```sh
uv run grimoire vault method zettelkasten
uv run grimoire vault method para
uv run grimoire vault method johnny-decimal
uv run grimoire vault method lyt
uv run grimoire vault method evergreen
uv run grimoire vault method cornell
uv run grimoire vault method bullet-journal
uv run grimoire vault method daily-weekly
```

Each command creates the folders (empty, with a `.gitkeep`), writes the templates, and writes the hub note: folder list, a five-step daily loop, one worked example, sources. In Obsidian, **Templates: Insert template** then finds them under `_templates/<id>/`.

## They coexist

Methods coexist because each lives under its own `Methods/<name>/` and `_templates/<id>/`, and each hub note hangs off [[Tonight]] like any other note. A sensible ladder for this course: `daily-weekly` on evening one, `cornell` for the lectures, and `evergreen` or `zettelkasten` once the vault starts to squeeze.

## Sources

- Luhmann, Communicating with Slip Boxes: https://luhmann.surge.sh/communicating-with-slip-boxes
- Niklas Luhmann-Archiv, Bielefeld: https://www.uni-bielefeld.de/fakultaeten/soziologie/forschung/luhmann-archiv/
- Ahrens, How to Take Smart Notes: https://takesmartnotes.com/
- Forte, The PARA Method: https://fortelabs.com/blog/para/
- Johnny.Decimal, Introduction: https://johnnydecimal.com/10-19-concepts/11-core/11.01-introduction/
- Johnny.Decimal, The JDex: https://johnnydecimal.com/10-19-concepts/11-core/11.05-the-index/
- Johnny.Decimal, About us: https://johnnydecimal.com/support/about-legal/about-us
- Linking Your Thinking: https://www.linkingyourthinking.com/
- LYT Kit, MOCs Overview: https://notes.linkingyourthinking.com/Cards/MOCs+Overview
- LYT Kit, Home: https://notes.linkingyourthinking.com/Home
- LYT Blog, Maps: https://blog.linkingyourthinking.com/maps/
- Matuschak, Evergreen notes: https://notes.andymatuschak.org/Evergreen_notes
- Matuschak, note titles as complete phrases: https://notes.andymatuschak.org/Prefer_note_titles_with_complete_phrases_to_sharpen_claims
- Matuschak, About these notes: https://notes.andymatuschak.org/About_these_notes
- Cornell LSC, The Cornell Note Taking System: https://lsc.cornell.edu/how-to-study/taking-notes/cornell-note-taking-system/
- Cornell LSC handout (PDF): https://lsc.cornell.edu/wp-content/uploads/2016/10/Cornell-NoteTaking-System.pdf
- Bullet Journal, Our story: https://bulletjournal.com/pages/story
- Bullet Journal, Rapid Logging: https://bulletjournal.com/blogs/faq/what-is-rapid-logging-understand-rapid-logging-bullets-and-signifiers
- Bullet Journal, How to: https://bulletjournal.com/pages/how-to-bullet-journal
- Obsidian Help, Daily notes: https://obsidian.md/help/plugins/daily-notes
- Obsidian Help, Templates: https://obsidian.md/help/plugins/templates
- David Allen Company, Weekly Review checklist (PDF): https://gettingthingsdone.com/wp-content/uploads/2014/10/Weekly_Review_Checklist.pdf
- David Allen Company, What is GTD: https://gettingthingsdone.com/what-is-gtd/
