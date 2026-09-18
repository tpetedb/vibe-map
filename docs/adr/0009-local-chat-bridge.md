# ADR 0009: In-game chat is answered by a loopback bridge the player starts, never by a key in the page

Status: Accepted, 2026-09-18

## Context

The game is one HTML file with no server, and the learner already pays for a coding agent: Claude Code, Codex, Gemini, Copilot or OpenCode, all of which answer in print mode from a terminal. A question asked inside the game ("what am I meant to build here", "what does this artifact teach") is exactly the question that subscription answers well, and the course already drives those CLIs from `vibe explain` and `vibe council`.

A browser page cannot reach a subscription that lives in a terminal. The three ways out are all bad in different ways. Shipping an API key in the page gives the key to anyone who opens the page and bills the author. Putting a hosted proxy behind the game turns a single-file game with no CDN (ADR 0001) into a service with a bill, a log of everyone's questions and an outage. Asking the learner to copy the question into their terminal and the answer back is what they are already doing, and is the thing worth removing.

That leaves a bridge on the learner's own machine, which is a listening socket, started by a learner who is on the second evening of learning to code. A listening socket that runs a coding agent is worth attacking: any page in any tab can send it a request, and the interesting thing behind it is not data but the ability to make a process run.

## Decision

`vibe chat serve` runs a loopback HTTP bridge (`vibemap/chat.py`, standard library only) with one endpoint that takes a question, and the game's chat panel talks to it.

- **The bridge takes questions, never commands.** The body carries a question and identifiers: a world, a stop number, a mentor id, an artifact id. The prompt is built on the Python side from `vibemap/data/campaign.json`, so no text from the page except the question itself reaches the provider, and nothing from the page selects what the provider is told to do. The question is one element of an argument list (`provider.argv(prompt)`, `shell=False`), so a semicolon or a backtick in a question is a semicolon or a backtick.
- **127.0.0.1 only.** Not `0.0.0.0`, not a hostname that might resolve outward. A bridge on the cafe wifi is somebody else's subscription.
- **A pairing code is the shared secret.** The panel shows eight characters from a 32 character alphabet, the player starts the bridge with `--pair CODE`, and every request carries the code in `X-Vibe-Code`, compared with `secrets.compare_digest`. Ten wrong codes and the bridge answers nothing until it is restarted, which turns the remaining 2^40 guesses into an attack the learner watches fail. Without a code a hosted copy of the game cannot talk to a stranger's bridge, which is the case the pairing exists for.
- **An Origin allowlist, checked before anything else.** Loopback on any port (the game served locally or by the test harness), `null` (a `file://` game), the hosted copy at `https://tpetedb.github.io`, plus any `--origin` the learner adds for their own fork. A request with no Origin is refused too: the page is never same origin with the bridge, so a missing Origin is not a browser asking.
- **One question at a time**, a 16 KiB body cap read off `Content-Length` before the socket is drained, a 4000 character question cap, and a timeout after which the provider process is killed. A subscription is metered and a learner is one person; a queue of one is also the honest shape of the panel.
- **The port is fixed at 7717 by default.** This is a deliberate deviation from "a random free port": the page has to find the bridge and cannot read a port off a terminal. `--port 0` takes a free one for anyone who prefers to type it into the panel.
- **No bridge is a supported state.** When nothing answers, the panel says so in three lines with the exact command and the code in it, and answers from the notes and stops already embedded in the game file. The feature degrades to a search rather than to an error.

## Consequences

- The learner's subscription, their key and their questions stay on their machine. We never see a question, we never pay for an answer, and there is nothing to leak because there is nothing stored.
- A page in another tab that guesses the port still has to guess the code, and gets ten tries. A page that guesses both can spend the learner's subscription on questions about the course; it cannot run a command, read a file or choose the prompt. That is the residual risk, and it is the reason the code is not four characters.
- The bridge only runs while the learner runs it. There is no daemon, no launch agent and no port left open after the terminal closes, which is also why the panel has to explain how to start one every time.
- `vibe chat ask` in the terminal builds the same prompt through the same code, so the two answers are the same answer and there is one place to change the prompt.
- Five providers means five print-mode invocations we do not control. `vibemap/providers.py` already carries them with the documentation link per entry; a provider that changes its flags breaks the chat the same way it breaks `vibe explain`, and in one place.
