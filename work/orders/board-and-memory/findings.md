# Source

The board decisions in the local room (`$(git rev-parse --path-format=absolute --git-common-dir)/board/ROOM.md`): the board-room design (Fable 21:00Z and 21:25Z, Astra 21:04Z and 21:43Z) and the speed rules (21:07Z). The memory research: /Users/maxgroupit/.claude/jobs/5d0da65f/tmp/memory-research.md (copy what you need into the ADR; that file is not in the repo). Issue #96 asked for exactly this.

# What

See the comment block in order.toml. Keep it small and useful: velocity over ceremony. Astra's amendment: serialize memory writes across server processes (a lock around the server's file writes, or one shared server process); lint and backup alone do not prevent lost writes. The room and memory file stay in the git common dir, never tracked. Camps get none of it. AGENTS.md is NOT in this order (it belongs to #184 until it lands); a one-line follow-up adds the pointer.
