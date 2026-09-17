# workspace

Yours. Everything you build during the course goes here, and the checks look here:

| Workstream | What lands here |
|---|---|
| 1, Innovation Hub | `game/index.html`, the game you asked the agent for |
| 3, Data Warehouse | `data/scores.csv`, `sql/*.sql`, `python/*.py` |
| an artifact on the island | `artifacts/<id>/`, the thing the sheet's Do it for real section asks you to build |
| the rest | whatever the lesson says, plus anything else you make |

Every artifact sets one task of under twenty minutes, written from the official documentation of the thing. Build it in `artifacts/<id>/`, then run `vibe check --artifact <id>`; the check looks at what is there and says so when a tool it wanted is not installed.

Nothing outside this folder depends on what is in it. Delete a file, start over, keep three versions: your call. The one exception is `data/scores.csv` once it exists: it is your system of record, and the tools only read it.
