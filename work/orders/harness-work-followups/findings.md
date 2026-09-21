# Source

Issue 149, the harness half. Each was found by the reviewer of pull request 144 and left on purpose.

### W1 A stray that is only staged passes `check`
Stage a change to another team's file, restore the working copy to base: `changed()` does not see it until it is committed. Compare the index to base as well as the working tree.

### W2 One unchecked diff
The `git diff` inside `changed()` does not pass `must=True`, so a failed diff reads as "nothing differs".

### W3 Names read without -z
`changed()`, `diff_names()` and the folder check in `load_order` split on newlines; `dirty()` already uses `-z`. A quoted or non-ASCII name must not slip.

### W4 touched.json is never pruned
Drop an agent's entry when the order lands or after a bounded number of entries; say which in the file's docstring.

### W5 AGENTS.md still says a hook "holds" an agent
The ADR, `work/README.md` and `CLAUDE.md` say "reminder". One sentence.
