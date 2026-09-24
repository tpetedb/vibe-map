# The archipelago

The four evenings are one world. The active island is built in full; the other
three stay visible as silhouettes, connected by long bridges. Walking across a
bridge changes the active island without reloading the page. **World** remains
the fast route for a learner who does not want to walk.

## Opening and crossing a bridge

On normal and harder difficulties, completing any stop on either adjoining
island opens their bridge. This also lets an imported camp walk back to an
earlier island. A closed bridge has a barrier and a sign that says what is
missing. Beginner difficulty opens the bridges from the start.

Use the keyboard, tap-to-walk or the touch stick exactly as on land. The deck,
shore joins and middle rest platform are walkable ground. Crossing the middle
changes the island, moves the HUD and minimap to the new place and keeps the
learner's progress and inventory.

Zoom to the far framing to see the complete archipelago. The minimap shows all
four islands and all three bridges. The World button flies directly to the
next island and is an alternative to the same destination, not a different
state transition.

## Saved state

The current island and `doneW` live in the game's saved `S` object. Whether a
bridge is open is derived from difficulty and completed stops. Bridge meshes,
deck collision and island silhouettes belong to the scene and are rebuilt
from that data. No bridge geometry is persisted.

## Accessibility

Every closed crossing has a written reason in the scene. The World button
offers fast travel, the minimap gives the same geography in two dimensions and
reduced motion removes decorative movement without disabling walking. The
camera keeps the walker and bridge in frame at the supported zoom levels.

## Responsible code and checks

- `src/game/22-archipelago.js` builds silhouettes, bridges, barriers and their
  walkable surfaces.
- `src/game/30-input.js` and `src/game/31-animate.js` move the walker over land
  and bridge using the same input path.
- `src/game/32-minimap.js` draws the four-island map.
- `tests/test_game_bridges.py` walks the real deck frame by frame, checks there
  is no gap and proves the island changes at the crossing.

The design decision that keeps experiences behind one shared core is ADR 0015,
[`experiences share one core`](adr/0015-experiences-share-one-core.md).
