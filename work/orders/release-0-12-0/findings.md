# release-0-12-0

Build this only on main after car L (#208) has landed: first `just sync-main`. Then `just release 0.12.0` (tools/changelog.py release plus work.py sweep), and edit the assembled 0.12.0 section in CHANGELOG.md until it reads as one changelog: Galaxy (the playable journey, walking on planets, the sourced origins) is the headline; group what the fragments say twice; drop internal process noise a learner would not care about into one short "Maintainers" line if the section uses one (see how 0.11.0 did it). Keep released sections untouched. Rebuild (`just build`, the sync tools), run every criterion, commit by explicit path, push, open the PR with the tag line first and "Closes #210".

builder:
