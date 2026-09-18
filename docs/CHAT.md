# Chat: ask the game, answered by your own subscription

The game has a chat panel. Questions typed into it are answered by the coding
agent you already pay for, running on your own machine. Nothing is sent to us,
no key lives in the page, and there is no server anywhere.

Why it works this way, and what it refuses:
[ADR 0009](adr/0009-local-chat-bridge.md).

## Open it

In the game: the **Ask** button in the HUD, or the **C** key. The chip under the
heading says what the question is about, built from where you are standing:
the island, the stop whose sheet is open, and the mentor or artifact you are
next to.

Without a bridge the panel still answers, by searching the notes and stops that
are embedded in the game file. Every passage it finds is a link into the vault.

## Start the bridge (three lines)

The panel shows a pairing code. In a terminal, in your camp:

```
uv run vibe chat serve --pair ABCD2345
```

Then ask again. The bridge prints which provider answers and where it listens:

```
pairing code ABCD2345
bridge       http://127.0.0.1:7717
provider     Claude Code
```

Leave it running while you play; Ctrl-C stops it. Nothing is left listening
afterwards.

| Option | What it does |
|---|---|
| `--pair CODE` | binds the bridge to the code the panel shows. Without it the bridge makes a code and prints it, and you type that into the panel instead. |
| `--port N` | default 7717, the port the panel tries. `--port 0` takes a free one; type it into the panel's Port box. |
| `--provider claude\|codex\|gemini\|copilot\|opencode` | default: the provider in `config/camp.toml`. |
| `--origin URL` | one more allowed Origin, for your own hosted copy of the game. |
| `--timeout N` | seconds before an answer is given up on. Default 180. |

## The same question in the terminal

```
uv run vibe chat ask "where do the numbers live" --stop 3
uv run vibe chat ask "what is Karpathy on record for" --mentor karpathy
uv run vibe chat ask "what does the cafe teach" --artifact cafe
```

Same prompt, same course data, same provider. `vibemap/chat.py` builds it once.

## What the bridge will not do

- It binds `127.0.0.1` only. Nobody else on the network can reach it.
- It takes a question, never a command. The prompt is built from
  `vibemap/data/campaign.json` on the Python side; the page sends identifiers
  (a stop number, a mentor id) and the question, nothing else.
- Every request carries the pairing code. Ten wrong codes and it stops
  answering until you restart it.
- Only the game's own origins may talk to it: a local page, a `file://` page,
  the hosted copy, and whatever you add with `--origin`.
- One question at a time, a 16 KiB body, a 4000 character question, and a
  timeout that kills the provider process.

## When it does not answer

| What you see | What to do |
|---|---|
| "No bridge answered on port 7717" | Start it: `uv run vibe chat serve --pair <code>`. If you used `--port 0`, type the printed port into the panel's Port box. |
| "wrong pairing code" | The bridge is paired with a different code. Restart it with the code the panel shows, or type the bridge's code into the panel. |
| "is not installed" | The provider CLI is missing. The message carries the install command; `uv run vibe toolbelt` lists them all. |
| "a question is already being answered" | One at a time. Wait for the answer. |
