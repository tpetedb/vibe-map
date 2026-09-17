# ADR 0005: A mini-game earns its place by teaching something the learner keeps

Status: Accepted, 2026-09-17

## Context

Six of the eight campus workstreams carried a small interactive panel. They came from the first evening, when the game was a joke for a wine night, and they were written to be funny before they were written to teach.

Two of them taught nothing. Workstream 1 span up a mascot with a random name and three random stats (Speed, Insight, Charm) on a twenty-sided roll. Workstream 3 logged twenty-sided rolls into a histogram and called it the enterprise data warehouse. Both are dice with a corporate sticker on them: the player presses a button, a random number appears, and the lesson next to it is about shipping an MVP and about a CSV schema. The mascot also leaked into the rest of the game, because the prompt panel in workstream 2 and the closing message in workstream 9 read its random stats.

The brief for this cycle is explicit: no fantasy, professional look, and every stop leaves something real behind. A panel that rolls dice is the clearest example of the thing the brief is against, and it also breaks the promise that the game is a manual you can read afterwards.

The other four panels do teach: a vague change request against a precise one, a tagged release and a rollback, a connector that goes on and off, and a graph of linked notes.

## Decision

We will keep a mini-game only when the thing it demonstrates is the thing the lesson beside it is about, and when the player could describe what they learned to someone else.

- **Cut**: the mascot generator (workstream 1) and the roll ledger (workstream 3), with the state they carried (`S.mascot`, `S.rolls`) and the references to them in the finale message.
- **Rebuilt, workstream 1**: the three sentences. The player types what the game is, who plays it and how you win; the panel writes out the exact prompt to paste into Claude Code, with Tom's one guardrail already attached, and counts the sentences. What the player keeps is the shape of a first prompt.
- **Rebuilt, workstream 2**: the same change, asked for two ways. One demo component, two change requests. The precise one adds a badge and touches nothing else; the vague one is free to rename the title, change the colour, swap the font and drop a column, and says so. It no longer depends on the mascot.
- **Rebuilt, workstream 3**: the column names are the contract. The same three rows and the same DuckDB query; renaming `score` to `points` produces the binder error DuckDB actually prints, and renaming it back makes the query green again.
- **Kept as they are**: the release ledger with rollback (workstream 4), the connectors (workstream 5), the note graph (workstream 6). The graph was drawn only by the playthrough tool, never when a player opened the stop; opening workstream 6 now draws it.

Every one of these is deterministic. Nothing in a mini-game is random any more.

## Consequences

- The title screen and the panels can be screenshotted for the played instance without a mascot or a twenty-sided die in the frame.
- `S.mascot` and `S.rolls` are gone from the game's state. They never crossed the progress code (version 2 carries stops, path, artifacts), so no code changes version and an old save simply carries two keys nobody reads.
- The finale message now reports stops delivered, releases tagged and integrations live, which is the state a player can point at.
- Three panels are new surface area, so each has a smoke test that drives the real buttons: the prompt builder, the renamed column and the scoped change request.
- Mini-games are now held to the same bar as the lessons. A future panel that cannot answer "what does the player keep" does not ship.
