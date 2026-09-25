# .agents/memory/

The shared memory is not kept here: Codex cannot write under `.agents/`, so the
records live in the runtime store, `<git common dir>/board/memory.jsonl`, shared
by every worktree and both teams and never committed. `tools/board.py memory
add|search|index` writes and reads them under one lock; `work/BOARD.md` and the
skill `shared-memory` give the schema, the caps and what is never stored.
