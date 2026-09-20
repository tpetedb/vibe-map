<!-- CONTRIBUTING.md is the long form of this list. Delete a line that does
not apply to your change rather than leaving it unticked with no word. -->

## What changed, and why

Closes #

## How it was tested

<!-- The command you ran and what it said. For a game change, the screenshot
you looked at (tests/out/). -->

## Before you ask for a review

- [ ] `just verify` is green (ruff, pytest with Playwright, the build check)
- [ ] One changelog fragment under `changelog.d/`, and `CHANGELOG.md` untouched
- [ ] Nothing generated was hand-edited: `just build` after `src/`, `just tree`
      after a topic, `tools/sync_template.py` and `tools/sync_fork_source.py`
      after the files they mirror
- [ ] A test for every behaviour that changed, and it fails without the fix
- [ ] No em dashes, no emoji, here or in the code
- [ ] A new browser test file is in exactly one shard of `ci.yml`

## Seen, not done

<!-- Anything you noticed and left alone, so it becomes an issue instead of
being forgotten. -->
