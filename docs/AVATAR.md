# The avatar, collectibles and wearables

The walker is a view of what the learner has done. It can walk, sit at a free
seat, open a laptop, collect objects and wear rewards. The pose and meshes are
rebuilt from saved state whenever the island is rebuilt.

## What the player does

Walk over a collectible to pick it up. Open **Backpack** for three tabs:

- **Inventory** groups the collected objects by island and links each idea to
  the tech tree.
- **Achievements** says what unlocked and what remains.
- **Wardrobe** equips one earned item per slot. A second item in the same slot
  replaces the first.

Walk to a free chair and use the prompt to sit. The walker opens the laptop;
moving away stands up again. Mentors use the same seating rules, so the view
does not place two people in one chair.

## Saved state

`S.items`, `S.ach` and `S.wear` are the complete record. Pose, nearby seats,
laptop light and meshes are derived scene state. A progress code carries the
three lists between the browser and `.vibe/state.json` without replacing
things already earned on the other side.

Collectibles and wearable definitions live in `vibemap/data/items.json`.
Positions are relative to an island feature, never fixed world coordinates,
so world scale and a rebuilt island do not change what an item belongs to.

## Terminal counterpart

`vibe import <code>` carries collected items, achievements and worn items into
the camp. `vibe export` carries them back. `vibe pet` is the terminal companion
rather than a second avatar; it reads the companion choice from the same camp
configuration.

## Accessibility

Backpack is a labelled keyboard-reachable sheet. Inventory, achievements and
wardrobe are text lists with explicit collected, locked, unlocked and equipped
words. Colour and the 3D mesh are supporting cues. Toasts announce a pickup or
achievement, and quiet mode keeps the same event record without showing the
temporary toast.

## Responsible code and checks

- `src/game/18-avatar.js` owns poses, achievements, wearables and Backpack.
- `src/game/19-items.js` places seats and collectibles and records pickups.
- `vibemap/data/items.json` names the portable item data.
- `tests/test_game_avatar.py` checks sitting, pickup, achievements, progress
  codes and visible wearables through the running game.
