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
  lamp:"#FDE68A",window:"#FFD36B",lava:"#FF4500",timber:"#7B5128",deck:"#D9A76A",
  stone:"#9CA3AF",snow:"#F8FAFC",ink:"#1F2937",
};


// The camera. The fitted view is derived, not fixed: the distance that puts
// the whole island inside the frame comes from the island's radius and the
// field of view, so a narrow window pushes the camera back instead of cropping
// the island. pitch is the angle above the horizon in radians, follow is how
// much of the walker's position the fitted frame takes, drift caps how far
// that may pull the island off centre, ahead is the look-ahead along the walk
// and ease is how fast the frame catches up. glide is the seconds the camera
// takes from the title's orbit, or from a fast travel, down to the walker.
// far is the far plane in island units; the near plane follows the distance
// (nearK times it), which is what keeps ground decals from flickering when
// the camera is a long way out.
//
// zoom is one level from min to max. At -1 the camera is `near` units from
// the walker at nearPitch and frames the walker; at 0 it is the fitted view
// and frames the island; at 1 it is `far` times the fit at farPitch and
// frames the archipelago. start is where a fresh browser begins: close enough
// that the walker and the companion read on a phone. step is one press of a
// key or a button, wheel is levels per wheel pixel, pinch is how much stronger
// a trackpad pinch is than the wheel it arrives as, ease is per second.
const CAM={fov:46,pitch:.72,margin:1.03,follow:.5,drift:4.5,ahead:.45,ease:3.2,glide:1.4,far:520,nearK:.03,
  zoom:{min:-1,max:1,start:-.62,near:17,nearPitch:.6,far:2.5,farPitch:.98,step:.25,wheel:.0014,pinch:6,ease:7}};

// A name plate never draws smaller than minPx CSS pixels tall, up to grow
// times its own size, which is what makes it legible from the fitted view,
// and never larger than maxPx, so one next to a close camera stays a label;
// past fadeZoom on the way out to the archipelago the plates fade away. gap is
// the breathing room, in pixels, inside which a nearer plate wins over a
// farther one instead of both being drawn on top of each other.
const PLATE={minPx:22,maxPx:34,grow:4,fadeZoom:.35,gap:3};

// The ground's texture: how many tufts an island gets, and how much darker
// than the world's own grass colour they are.
const GROUND={tufts:240,shade:.9};

// Tone mapping: ACES with a little exposure, so bright grass and a lamp at
// night roll off instead of clipping to the same flat value.
const EXPOSURE=1.06;

// The light rig, one entry per sky stage; WORLDS[*].sky carries the horizon
// colour for the same nine. az and el are the bearing and the height of the
// sun (of the moon from stage four) in degrees, sun is its colour, i its
// intensity, zen the top of the sky dome over the world's horizon colour, and
// hemi and amb the fill that keeps a night lit like a night. fig is the share
// of their own colour the figures glow with: a night dark enough to make the
// lamps worth having is also dark enough to lose the walker in, and the people
// are what the player is looking for.
const SKY_RIG=[
  {az:35,el:52,sun:"#FFF6E0",i:1.18,zen:"#3E8FD8",hemi:.44,amb:.12,hs:"#CFE9FF",hg:"#4A7A3A",fig:0},
  {az:20,el:34,sun:"#FFE3AE",i:1.06,zen:"#5C9BD6",hemi:.4,amb:.11,hs:"#D7E4F5",hg:"#4A6E3C",fig:0},
  {az:5,el:17,sun:"#FF9E5E",i:.9,zen:"#7A6FA8",hemi:.34,amb:.1,hs:"#E3C6C0",hg:"#4A4038",fig:0},
  {az:-8,el:7,sun:"#F2704F",i:.56,zen:"#4C3E7A",hemi:.3,amb:.1,hs:"#9E86A8",hg:"#33303A",fig:.1},
  {az:-140,el:30,sun:"#9FB6F0",i:.36,zen:"#232A5C",hemi:.24,amb:.09,hs:"#4A5688",hg:"#1E2434",fig:.2},
  {az:-150,el:38,sun:"#9FB6F0",i:.32,zen:"#141A44",hemi:.2,amb:.08,hs:"#3A4470",hg:"#181D2C",fig:.24},
  {az:-160,el:44,sun:"#A8BCF5",i:.29,zen:"#0B1130",hemi:.17,amb:.075,hs:"#2E3660",hg:"#141824",fig:.27},
  {az:-170,el:49,sun:"#A8BCF5",i:.27,zen:"#070B24",hemi:.15,amb:.07,hs:"#262D52",hg:"#101320",fig:.29},
  {az:180,el:53,sun:"#B4C6FF",i:.25,zen:"#04061C",hemi:.13,amb:.065,hs:"#1E2446",hg:"#0C0F1A",fig:.3},
];

// The pixel companion that follows the walker (src/game/19b-pet.js). The
// frames are the vendored sets the terminal paints, so only its placement is
// a number here. FOLLOW and LAG are what make it a companion rather than a
// shadow: it settles that far behind the walker, and reaches the spot with an
// exponential ease of that rate per second. SIDE keeps it off to the walker's
// right, because straight behind is straight under his nameplate from this
// camera and the companion would spend the walk hidden by his back. PX is
// world units per sprite pixel, so the packs keep their sizes against each
// other and against a walker about 2.6 units tall: a duck of sixteen pixels
// stands 1.6 high, a turtle of eight stands 0.8. On screen a sprite pixel is
// always a whole number of device pixels and never fewer than MIN_TEXEL, so
// the art stays crisp at every zoom. LEASH
// is how far it may fall behind before it stops going round and comes
// straight to the walker. CHEER is the seconds it celebrates a claimed stop,
// NIGHT how far the sprite is tinted towards the moonlight at the last stage.
const PET={FOLLOW:1.8,SIDE:1.9,LAG:4.5,PX:.1,BOB:.06,WALK_AT:.55,FPS:8,
  MIN_TEXEL:1,LEASH:9,CHEER:2.4,NIGHT:.55};
