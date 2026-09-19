// Source configuration for the game: the numbers and colours a fork changes
// first. The build concatenates every file in src/config/ ahead of the game
// modules, so these names are in scope everywhere below. The journey level
// (name, difficulty, theme) arrives separately as CONFIG, injected from
// config/camp.toml; the theme presets themselves live in vibemap/themes.py.
// See docs/CONFIG.md.

// How large the island is around the walker. Meshes keep their size, so the
// world grows rather than the walker shrinking; speed, camera, fog and sky
// distances scale with it in their own modules so the feel stays the same.
const WORLD_SCALE=1.6;
// The island's radius in data units, before the scale.
const R=20;
// Each plot has an annex 6 to 8 data units outward, hidden until that stop is
// done. Its radius, scaled with the world.
const ANNEX_R=3.2*WORLD_SCALE;

// The archipelago: the four islands sit in one scene on the corners of a
// square, ISLAND_GAP apart, joined by bridges across the water. The gap is in
// the same scaled units as the island data, and has to stay wider than two
// islands with all their annexes out, or two shores would touch.
const ISLAND_GAP=58*WORLD_SCALE;
// A bridge deck: half its walkable width, and the radius of the rest platform
// at its midpoint. Both are absolute, because the walker does not scale with
// the world.
const BRIDGE_W=3,BRIDGE_REST_R=5;

// Tom's palette: the five hues the whole product uses, on OLED black. A fork
// that recolours the island starts here.
const PALETTE={
  red:"#D32F2F",orange:"#FF8C1A",yellow:"#FFBF00",green:"#00A86B",blue:"#0067A5",
  greenBright:"#00D084",blueBright:"#0088CC",orangeBright:"#F04923",
  black:"#000000",surface:"#0A0A0A",text:"#F1F1F8",muted:"#8B93A7",
};

// The pixel companion that follows the walker (src/game/19b-pet.js). The
// frames are the vendored sets the terminal paints, so only its placement is
// a number here. FOLLOW and LAG are what make it a companion rather than a
// shadow: it settles that far behind the walker, and reaches the spot with an
// exponential ease of that rate per second. HEIGHT is in world units against
// a walker about 2.4 units tall.
const PET={FOLLOW:2.2,LAG:4.5,HEIGHT:1.05,BOB:.06,WALK_AT:.55,FPS:8};
