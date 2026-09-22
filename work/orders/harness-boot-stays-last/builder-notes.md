# Boot order recovery

Builder: codex-root. Starting revision: 25f0994.

The two optional-folder cases reproduced the ordering defect, with and without a game module numbered after boot. A third regression reproduced the missing-boot build incorrectly succeeding. Initial targeted result: three failures.

The build now requires boot and moves it after all discovered modules. The current game remains byte-identical to origin/main, and the packaged build script was regenerated with sync_fork_source. All 27 build tests pass; build --check passes.

Full verification waits for baseline fork integration fix #175 and browser capacity. Independent review still needs the actual browser proof from c4. No commit or PR yet.
