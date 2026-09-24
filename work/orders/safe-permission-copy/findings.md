# Source

Issue #186 (Codex gameplay tester). Workstream 1's Definition of done says: "If Claude asked a permission question you did not understand, answer yes and tell Tom; understanding permissions is workstream 4." It is in src/body.html (line ~179) and docs/SYLLABUS.md (line ~165); game/vibe-map.html, docs/site/syllabus.html and vibemap/data/fork_source/src/body.html are generated copies.

# What

Replace the instruction with safe guidance in the same voice, for example: if Claude asks permission for something you do not understand, pause: read what it wants to run or change, and ask Tom before you say yes; understanding permissions in depth is workstream 4. Keep both copies identical in meaning. Regenerate the derived outputs. Add tests/test_safe_copy.py: a deterministic guard over the source and built files that fails on "answer yes" style instructions next to "permission", and asserts the new guidance is present in the first lesson. Touch nothing else in src/body.html (Team Codex's Galaxy walking work lands in #183; keep the diff to this sentence).
