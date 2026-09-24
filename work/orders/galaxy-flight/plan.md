# Galaxy phase 4: flight slice

The first ship slice replaces the Chart's instant Land action with a three-second autopilot approach. The camera remains fixed on the chart. A small procedural ship follows a calm arc, with no warp, flashing, roll or shake. The existing palette and materials keep the ship within the game's visual language.

A native modal dialog makes Skip the only keyboard stop during flight. Enter, Space, touch and Escape all reach the same arrival path. Reduced motion, including a system preference enabled during flight, cuts to arrival. A renderer-free list lands immediately. Arrival focuses the walkable canvas, or the destination heading in list mode, and announces the destination. It never focuses an actionable lesson while a travel key may still be held. The transient ship is disposed when arriving or leaving the experience; no progress format changes.

The flight clock uses elapsed monotonic wall time, so a busy renderer cannot stretch a three-second journey into a minute. The destination list and real lesson panels remain authoritative. The ship's last landed place is transient presentation state, independent of list focus.

## Following orders, not included here

1. Age jump range: agree the visible range rule against the existing topic prerequisite graph before adding any gate. Every unavailable destination must say exactly what unlocks it; preserve access to already learned material and the complete list twin.
2. Echo jumps: map secondary origins to explicit destination choices, with sourced origin text and a keyboard/touch equivalent. Reuse this flight and arrival lifecycle rather than a second transport implementation.
3. Phase 5 structures and phase 6 accessibility/design review remain the roadmap's separate slices. This order does not claim phase 4 is complete.
