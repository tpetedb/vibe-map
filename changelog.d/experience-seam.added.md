- The islands are an experience behind a small contract, and four golden
  pictures prove nothing moved. `src/game/24-experience.js` registers
  `EXPERIENCES.islands` with the seven things ADR 0015 lets core ask of a view
  (`name`, `build`, `dispose`, `tick`, `goTo`, `where`, `listing`), each of
  them delegating to what the game already does; `activeExperience()` reads
  the preference (`S.settings.experience`, the islands by default, a
  `?experience=` parameter winning for tests) and never writes it. Nothing
  calls the registry yet, so boot, the panels and the frame loop are
  unchanged. `listing()` is the whole archipelago as plain data, which is what
  the non-3D twin will be built from. `tests/golden/` holds one picture per
  island, taken at the fitted view with a fixed seed and a fixed hour and
  compared by region, so every later change can show it left the islands
  alone.
