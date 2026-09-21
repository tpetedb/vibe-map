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
  island, taken at the fitted view with a fixed seed and a fixed frame clock
  once the scene has come to rest, and compared by region. An unchanged tree
  gives the recorded picture pixel for pixel on the machine that made it, two
  machines differ by a hundredth of a colour level, and the tolerance is ten
  times that: 0.1 on the worst of 160 regions, 0.002 on their mean. The campus
  grass moved by one level on one channel fails it, and so does the well taken
  off the campus; a recolour and the missing well are tests of their own, so
  the guard cannot go blind to them unnoticed. What it cannot see: a change
  below that (the stone of the well alone moved by thirty levels on one
  channel passes, and so does its roof a ninth narrower), and anything that is
  not in the picture, which is text and fonts, the HUD, ambient motion past
  where it starts, the companion, every zoom level and window but one, the day
  and the night sky, and the buildings of the five stops the record leaves
  undelivered.
