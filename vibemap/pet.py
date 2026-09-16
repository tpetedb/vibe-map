"""A small companion that lives in the terminal.

The sprites, the idle animation and the deterministic roll are ported from
claude-buddy by Romesh Niriella (MIT, https://github.com/btcromesh/claude-buddy),
itself extracted from the short-lived /buddy feature of Claude Code (April
2026, removed in 2.1.97). The crab is ours. Same name, same creature: the
roll is a seeded PRNG over the learner's name, and every field can be
overridden in vibe.toml under [pet].
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.text import Text

from vibemap.palette import BLUE, GREEN, MUTED, ORANGE, YELLOW

RARITIES = ("common", "uncommon", "rare", "epic", "legendary")
RARITY_WEIGHTS = {"common": 60, "uncommon": 25, "rare": 10, "epic": 4, "legendary": 1}
RARITY_FLOOR = {"common": 5, "uncommon": 15, "rare": 25, "epic": 35, "legendary": 50}
RARITY_COLOURS = {
    "common": MUTED,
    "uncommon": GREEN,
    "rare": BLUE,
    "epic": ORANGE,
    "legendary": YELLOW,
}
SPECIES = (
    "duck", "goose", "blob", "cat", "dragon", "octopus", "owl", "penguin",
    "turtle", "snail", "ghost", "axolotl", "capybara", "cactus", "robot",
    "rabbit", "mushroom", "chonk", "crab",
)  # fmt: skip
# The upstream list; the roll indexes into it so a name gives the same species
# here as in claude-buddy. The crab is only ever chosen on purpose.
_ROLLABLE = SPECIES[:-1]
EYES = ("·", "*", "×", "◉", "@", "°")
HATS = ("none", "crown", "tophat", "propeller", "halo", "wizard", "beanie", "tinyduck")
STAT_NAMES = ("DEBUGGING", "PATIENCE", "CHAOS", "WISDOM", "SNARK")
SALT = "friend-2026-401"
WIDTH = 12

# Three idle frames per species, five rows of twelve columns; {E} is the eye.
# Row 0 is the hat row: a hat replaces it when the frame leaves it blank.
BODIES: dict[str, tuple[tuple[str, ...], ...]] = {
    "duck": (
        ("            ", "    __      ", "  <({E} )___  ", "   (  ._>   ", "    `--´    "),
        ("            ", "    __      ", "  <({E} )___  ", "   (  ._>   ", "    `--´~   "),
        ("            ", "    __      ", "  <({E} )___  ", "   (  .__>  ", "    `--´    "),
    ),
    "goose": (
        ("            ", "     ({E}>    ", "     ||     ", "   _(__)_   ", "    ^^^^    "),
        ("            ", "    ({E}>     ", "     ||     ", "   _(__)_   ", "    ^^^^    "),
        ("            ", "     ({E}>>   ", "     ||     ", "   _(__)_   ", "    ^^^^    "),
    ),
    "blob": (
        ("            ", "   .----.   ", "  ( {E}  {E} )  ", "  (      )  ", "   `----´   "),
        ("            ", "  .------.  ", " (  {E}  {E}  ) ", " (        ) ", "  `------´  "),
        ("            ", "    .--.    ", "   ({E}  {E})   ", "   (    )   ", "    `--´    "),
    ),
    "cat": (
        ("            ", "   /\\_/\\    ", "  ( {E}   {E})  ", "  (  ω  )   ", "  (\")_(\")   "),
        ("            ", "   /\\_/\\    ", "  ( {E}   {E})  ", "  (  ω  )   ", "  (\")_(\")~  "),
        ("            ", "   /\\-/\\    ", "  ( {E}   {E})  ", "  (  ω  )   ", "  (\")_(\")   "),
    ),
    "dragon": (
        ("            ", "  /^\\  /^\\  ", " <  {E}  {E}  > ", " (   ~~   ) ", "  `-vvvv-´  "),
        ("            ", "  /^\\  /^\\  ", " <  {E}  {E}  > ", " (        ) ", "  `-vvvv-´  "),
        ("   ~    ~   ", "  /^\\  /^\\  ", " <  {E}  {E}  > ", " (   ~~   ) ", "  `-vvvv-´  "),
    ),
    "octopus": (
        ("            ", "   .----.   ", "  ( {E}  {E} )  ", "  (______)  ", "  /\\/\\/\\/\\  "),
        ("            ", "   .----.   ", "  ( {E}  {E} )  ", "  (______)  ", "  \\/\\/\\/\\/  "),
        ("     o      ", "   .----.   ", "  ( {E}  {E} )  ", "  (______)  ", "  /\\/\\/\\/\\  "),
    ),
    "owl": (
        ("            ", "   /\\  /\\   ", "  (({E})({E}))  ", "  (  ><  )  ", "   `----´   "),
        ("            ", "   /\\  /\\   ", "  (({E})({E}))  ", "  (  ><  )  ", "   .----.   "),
        ("            ", "   /\\  /\\   ", "  (({E})(-))  ", "  (  ><  )  ", "   `----´   "),
    ),
    "penguin": (
        ("            ", "  .---.     ", "  ({E}>{E})     ", " /(   )\\    ", "  `---´     "),
        ("            ", "  .---.     ", "  ({E}>{E})     ", " |(   )|    ", "  `---´     "),
        ("  .---.     ", "  ({E}>{E})     ", " /(   )\\    ", "  `---´     ", "   ~ ~      "),
    ),
    "turtle": (
        ("            ", "   _,--._   ", "  ( {E}  {E} )  ", " /[______]\\ ", "  ``    ``  "),
        ("            ", "   _,--._   ", "  ( {E}  {E} )  ", " /[______]\\ ", "   ``  ``   "),
        ("            ", "   _,--._   ", "  ( {E}  {E} )  ", " /[======]\\ ", "  ``    ``  "),
    ),
    "snail": (
        ("            ", " {E}    .--.  ", "  \\  ( @ )  ", "   \\_`--´   ", "  ~~~~~~~   "),
        ("            ", "  {E}   .--.  ", "  |  ( @ )  ", "   \\_`--´   ", "  ~~~~~~~   "),
        ("            ", " {E}    .--.  ", "  \\  ( @  ) ", "   \\_`--´   ", "   ~~~~~~   "),
    ),
    "ghost": (
        ("            ", "   .----.   ", "  / {E}  {E} \\  ", "  |      |  ", "  ~`~``~`~  "),
        ("            ", "   .----.   ", "  / {E}  {E} \\  ", "  |      |  ", "  `~`~~`~`  "),
        ("    ~  ~    ", "   .----.   ", "  / {E}  {E} \\  ", "  |      |  ", "  ~~`~~`~~  "),
    ),
    "axolotl": (
        ("            ", "}~(______)~{", "}~({E} .. {E})~{", "  ( .--. )  ", "  (_/  \\_)  "),
        ("            ", "~}(______){~", "~}({E} .. {E}){~", "  ( .--. )  ", "  (_/  \\_)  "),
        ("            ", "}~(______)~{", "}~({E} .. {E})~{", "  (  --  )  ", "  ~_/  \\_~  "),
    ),
    "capybara": (
        ("            ", "  n______n  ", " ( {E}    {E} ) ", " (   oo   ) ", "  `------´  "),
        ("            ", "  n______n  ", " ( {E}    {E} ) ", " (   Oo   ) ", "  `------´  "),
        ("    ~  ~    ", "  u______n  ", " ( {E}    {E} ) ", " (   oo   ) ", "  `------´  "),
    ),
    "cactus": (
        ("            ", " n  ____  n ", " | |{E}  {E}| | ", " |_|    |_| ", "   |    |   "),
        ("            ", "    ____    ", " n |{E}  {E}| n ", " |_|    |_| ", "   |    |   "),
        (" n        n ", " |  ____  | ", " | |{E}  {E}| | ", " |_|    |_| ", "   |    |   "),
    ),
    "robot": (
        ("            ", "   .[||].   ", "  [ {E}  {E} ]  ", "  [ ==== ]  ", "  `------´  "),
        ("            ", "   .[||].   ", "  [ {E}  {E} ]  ", "  [ -==- ]  ", "  `------´  "),
        ("     *      ", "   .[||].   ", "  [ {E}  {E} ]  ", "  [ ==== ]  ", "  `------´  "),
    ),
    "rabbit": (
        ("            ", "   (\\__/)   ", "  ( {E}  {E} )  ", " =(  ..  )= ", "  (\")__(\")  "),
        ("            ", "   (|__/)   ", "  ( {E}  {E} )  ", " =(  ..  )= ", "  (\")__(\")  "),
        ("            ", "   (\\__/)   ", "  ( {E}  {E} )  ", " =( .  . )= ", "  (\")__(\")  "),
    ),
    "mushroom": (
        ("            ", " .-o-OO-o-. ", "(__________)", "   |{E}  {E}|   ", "   |____|   "),
        ("            ", " .-O-oo-O-. ", "(__________)", "   |{E}  {E}|   ", "   |____|   "),
        ("   . o  .   ", " .-o-OO-o-. ", "(__________)", "   |{E}  {E}|   ", "   |____|   "),
    ),
    "chonk": (
        ("            ", "  /\\    /\\  ", " ( {E}    {E} ) ", " (   ..   ) ", "  `------´  "),
        ("            ", "  /\\    /|  ", " ( {E}    {E} ) ", " (   ..   ) ", "  `------´  "),
        ("            ", "  /\\    /\\  ", " ( {E}    {E} ) ", " (   ..   ) ", "  `------´~ "),
    ),
    # Ours: claws up, a snap, a scuttle.
    "crab": (
        ("            ", " \\/      \\/ ", "  ({E}    {E})  ", "  (______)  ", " /\\/\\  /\\/\\ "),
        ("            ", " \\_      _/ ", "  ({E}    {E})  ", "  (______)  ", " /\\/\\  /\\/\\ "),
        ("            ", " \\/      \\/ ", "  ({E}    {E})  ", "  (______)  ", "  /\\/\\/\\/\\  "),
    ),
}  # fmt: skip

HAT_LINES = {
    "none": "",
    "crown": "   \\^^^/    ",
    "tophat": "   [___]    ",
    "propeller": "    -+-     ",
    "halo": "   (   )    ",
    "wizard": "    /^\\     ",
    "beanie": "   (___)    ",
    "tinyduck": "    ,>      ",
}

FACES = {
    "duck": "({E}>", "goose": "({E}>", "blob": "({E}{E})", "cat": "={E}ω{E}=",
    "dragon": "<{E}~{E}>", "octopus": "~({E}{E})~", "owl": "({E})({E})",
    "penguin": "({E}>)", "turtle": "[{E}_{E}]", "snail": "{E}(@)",
    "ghost": "/{E}{E}\\", "axolotl": "}{E}.{E}{", "capybara": "({E}oo{E})",
    "cactus": "|{E}  {E}|", "robot": "[{E}{E}]", "rabbit": "({E}..{E})",
    "mushroom": "|{E}  {E}|", "chonk": "({E}.{E})", "crab": "\\({E}  {E})/",
}  # fmt: skip

ADJECTIVES = (
    "Tiny", "Fluffy", "Brave", "Sneaky", "Cosmic", "Dizzy", "Fuzzy", "Mighty",
    "Wobbly", "Crispy", "Sparkly", "Grumpy", "Sleepy", "Zippy", "Bouncy", "Spooky",
    "Jolly", "Rusty", "Stormy", "Lucky", "Peppy", "Zany", "Quirky", "Sassy",
)  # fmt: skip
NOUNS = (
    "Bean", "Nugget", "Sprout", "Biscuit", "Noodle", "Pebble", "Pickle", "Muffin",
    "Waffle", "Squish", "Pudding", "Crumble", "Tater", "Dumpling", "Scraps", "Widget",
    "Pixel", "Nibble", "Scooter", "Snickers", "Wobbles", "Patches", "Buttons", "Pip",
)  # fmt: skip

# Frame index per tick; -1 is a blink. Half a second per tick upstream.
IDLE_SEQUENCE = (0, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 2, 0, 0, 0)

_M32 = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return (a * b) & _M32


def _mulberry32(seed: int):
    """The upstream PRNG, bit for bit, so a name rolls the same creature."""
    a = seed & _M32

    def rng() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & _M32
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) ^ t) & _M32
        return ((t ^ (t >> 14)) & _M32) / 4294967296

    return rng


def _fnv1a(s: str) -> int:
    h = 2166136261
    for ch in s.encode("utf-16-le")[::2]:
        h ^= ch
        h = _imul(h, 16777619)
    return h & _M32


def _pick(rng, items):
    return items[int(rng() * len(items))]


@dataclass(frozen=True, slots=True)
class Pet:
    species: str
    name: str
    eye: str
    hat: str
    rarity: str
    shiny: bool
    stats: dict[str, int]

    @property
    def colour(self) -> str:
        return YELLOW if self.shiny else RARITY_COLOURS[self.rarity]

    @property
    def stars(self) -> str:
        return "*" * (RARITIES.index(self.rarity) + 1)

    @property
    def face(self) -> str:
        return FACES[self.species].replace("{E}", self.eye)


def roll(user_id: str) -> Pet:
    """The creature a name gets, deterministic and the same as upstream."""
    rng = _mulberry32(_fnv1a(user_id + SALT))
    total = sum(RARITY_WEIGHTS.values())
    r = rng() * total
    rarity = "common"
    for candidate in RARITIES:
        r -= RARITY_WEIGHTS[candidate]
        if r < 0:
            rarity = candidate
            break
    species = _pick(rng, _ROLLABLE)
    eye = _pick(rng, EYES)
    hat = "none" if rarity == "common" else _pick(rng, HATS)
    shiny = rng() < 0.01
    floor = RARITY_FLOOR[rarity]
    peak = _pick(rng, STAT_NAMES)
    dump = _pick(rng, STAT_NAMES)
    while dump == peak:
        dump = _pick(rng, STAT_NAMES)
    stats: dict[str, int] = {}
    for stat in STAT_NAMES:
        if stat == peak:
            stats[stat] = min(100, floor + 50 + int(rng() * 30))
        elif stat == dump:
            stats[stat] = max(1, floor - 10 + int(rng() * 15))
        else:
            stats[stat] = floor + int(rng() * 40)
    name_rng = _mulberry32(_fnv1a(user_id + SALT + "-name"))
    name = f"{_pick(name_rng, ADJECTIVES)} {_pick(name_rng, NOUNS)}"
    return Pet(species, name, eye, hat, rarity, shiny, stats)


def resolve(
    user_id: str,
    *,
    species: str = "",
    name: str = "",
    eye: str = "",
    hat: str = "",
) -> Pet:
    """The rolled pet with any overrides from vibe.toml applied.

    Raises:
        ValueError: when an override names a species, eye or hat that does
            not exist.
    """
    base = roll(user_id)
    if species and species not in SPECIES:
        raise ValueError(f"unknown species {species!r}; one of {', '.join(SPECIES)}")
    if eye and eye not in EYES:
        raise ValueError(f"unknown eye {eye!r}; one of {' '.join(EYES)}")
    if hat and hat not in HATS:
        raise ValueError(f"unknown hat {hat!r}; one of {', '.join(HATS)}")
    return Pet(
        species or base.species,
        name or base.name,
        eye or base.eye,
        hat or base.hat,
        base.rarity,
        base.shiny,
        base.stats,
    )


def sprite(pet: Pet, index: int = 0, *, blink: bool = False) -> list[str]:
    """One frame, five rows of twelve columns, hat applied."""
    frames = BODIES[pet.species]
    eye = "-" if blink else pet.eye
    rows = [row.replace("{E}", eye) for row in frames[index % len(frames)]]
    if pet.hat != "none" and not rows[0].strip():
        rows[0] = HAT_LINES[pet.hat]
    return rows


def frame(pet: Pet, tick: int) -> list[str]:
    """The idle animation: fidget on some ticks, blink on one."""
    step = IDLE_SEQUENCE[tick % len(IDLE_SEQUENCE)]
    return sprite(pet, 0, blink=True) if step == -1 else sprite(pet, step)


def stroll(tick: int, width: int, *, period: int = 24) -> int:
    """A left-to-right offset that turns around at the edges, in columns."""
    span = max(0, width - WIDTH)
    if span == 0:
        return 0
    pos = tick % (2 * period)
    frac = pos / period if pos < period else (2 * period - pos) / period
    return int(round(frac * span))


def render(pet: Pet, tick: int = 0, *, stats: bool = True, offset: int = 0) -> Text:
    """A rich Text of the pet, its name, rarity and optionally the stats."""
    pad = " " * offset
    out = Text()
    out.append(f"{pad}{pet.name}", style=f"bold {pet.colour}")
    out.append(f"  {pet.stars}", style=pet.colour)
    if pet.shiny:
        out.append("  shiny", style=f"bold {YELLOW}")
    out.append(f"\n{pad}{pet.species} · {pet.rarity}\n", style=MUTED)
    for row in frame(pet, tick):
        out.append(f"{pad}{row}\n", style=pet.colour)
    if stats:
        out.append(f"{pad}face: {pet.face}\n", style=MUTED)
        for stat in STAT_NAMES:
            value = pet.stats[stat]
            filled = round(value / 100 * 20)
            out.append(f"{pad}{stat:<10} ", style=MUTED)
            out.append(chr(0x2588) * filled, style=pet.colour)
            out.append(chr(0x2591) * (20 - filled) + f" {value}\n", style=MUTED)
    return out


def gallery() -> list[tuple[str, list[str]]]:
    """Every species at frame 0 with the default eye, for `vibe pet --all`."""
    return [
        (s, sprite(Pet(s, s, EYES[0], "none", "common", False, {}), 0)) for s in SPECIES
    ]
