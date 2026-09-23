- `docs/CONTRACTS.md` is the tracked list of what other agents depend on (HUD
  elements, state and progress code keys, configuration keys, CLI exit codes,
  test helpers, generated files, data shapes), one dated line per contract
  with the pull request that made it, checked against the code. It replaces
  the contracts block at the top of issue #95.
- `docs/CONFIG.md` and ADR 0001 describe how the build finds its modules
  today, by folder and file name with boot last, instead of a `GAME_ORDER`
  list that no longer exists.
- ADR 0016 is accepted, says what `touched.json` keeps and when it goes, and
  its patch-id rule reads as several sentences.
- `docs/SKILLS.md` gives `work-order` its trigger phrases, marks both
  product-only skills, lists every skill that pre-approves commands, and
  names the backup hook's real folder and the work-order hooks and roles.
- `tests/test_docs_followups.py` holds these documents to the code: every
  recipe (inline, indented or in a fenced block), skill, helper, constant
  placed in a file, head placeholder, path and element they name has to
  exist, and each skill's pre-approved tools are the ones its frontmatter
  grants.
