# galaxy-grow-first-lesson

Issue #209 (found by Codex playing the deployed build at e2e0f50): with Settings Vault = Grow and 0 topics done, Galaxy's Journey marks Unix as the next topic, but its Learn button opens the vault card with LOCK_WHY ("Not unlocked yet: finish the stop, meet the mentor or inspect the artifact that leads here") instead of the lesson. Vault = Full shows the lesson. Grow unlocks notes through island play (computeUnlocked() in src/game/60-vault.js), so a Galaxy-only learner has no way in.

Do: let the active experience name topics that are always readable in Grow (an optional hook on the experience contract, e.g. `readable()`; Galaxy returns its next topic and those it marks available; the islands return nothing), and have computeUnlocked() add them. Galaxy's Learn button then opens the lesson. Red first: a browser test in tests/test_game_galaxy.py that sets Grow, 0 topics, clicks the real Learn button of the next topic and expects the lesson text, failing on main. Keep the islands' Grow behaviour; keep the contract test in tests/test_game_experience.py green (the hook is optional). Browser runs only after /Users/maxgroupit/.claude/jobs/5d0da65f/tmp/slot-wait.sh 4. Changelog fragment changelog.d/galaxy-grow-first-lesson.fixed.md. PR body starts with the tag line and says "Closes #209".

builder:
