"""The learner's progress: versioned, validated, one JSON file.

.vibe/state.json is written by the CLI and the TUI; the game keeps its own
copy in localStorage and the two exchange a progress code. Version 1 (no
version field) migrates on load; a newer version than this package knows is
refused with a clear message rather than patched around.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from vibemap import project, sprites

STATE_VERSION = 2
CODE_VERSION = 2
WORLDS = ("campus", "winter", "desert", "prod")
ROOT = project.root()
STATE_PATH = ROOT / ".vibe" / "state.json"


def _now() -> str:
    return dt.datetime.now().isoformat(timespec="minutes")


def check_pet(value: str) -> str:
    """A companion with no pixels is refused by name, never defaulted.

    Raises:
        ValueError: when the id is neither "none" nor a vendored set.
    """
    if value and value != "none" and value not in sprites.available():
        known = ", ".join(("none", *sprites.available()))
        raise ValueError(f"unknown pet {value!r}; one of {known}")
    return value


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    world: str = "campus"
    n: int
    at: str = Field(default_factory=_now)
    note: str = ""
    xp: int = 0


class CheckRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    at: str = Field(default_factory=_now)
    passed: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)


# The default name is a placeholder, shown as-is until the player types a name.
# It reads as an instruction and never as a person, which is the point.
PLACEHOLDER = "<your_name>"

# The log entry a progress code writes. The game claims, it never checks, so
# an imported stop is worth half until `vibe check` passes it (ADR 0004).
IMPORTED_NOTE = "done in the game, imported"


class State(BaseModel):
    """Everything the CLI remembers about the learner."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    version: int = STATE_VERSION
    name: str = PLACEHOLDER
    done_w: dict[str, list[int]] = Field(
        default_factory=lambda: {w: [] for w in WORLDS}, alias="doneW"
    )
    path: dict[str, str] = Field(default_factory=dict)
    log: list[LogEntry] = Field(default_factory=list)
    xp: int = 0
    badges: list[str] = Field(default_factory=list)
    checks: dict[str, CheckRecord] = Field(default_factory=dict)
    roadmap_done: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    artifacts_built: list[str] = Field(default_factory=list, alias="artifactsBuilt")
    mentors: list[str] = Field(default_factory=list)
    unlocked: list[str] = Field(default_factory=list)
    # The avatar: what was picked up on the islands, what that unlocked, and
    # what the walker is wearing. All three travel in the progress code.
    items: list[str] = Field(default_factory=list)
    ach: list[str] = Field(default_factory=list)
    wear: list[str] = Field(default_factory=list)
    # The pixel companion the game shows, an id of a vendored set or "none".
    # config/camp.toml [pet] is the camp's own choice; this is the game's copy,
    # so the progress code carries it both ways. Empty means no choice made.
    pet: str = ""
    # Shelves of the tech tree chosen in the game; empty means everything.
    # config/camp.toml is the source of truth, this is the game's copy so the
    # progress code can carry the choice both ways.
    interests: list[str] = Field(default_factory=list)

    _known_pet = field_validator("pet")(check_pet)

    @property
    def done(self) -> list[int]:
        return self.done_w.setdefault("campus", [])

    def is_done(self, world: str, n: int) -> bool:
        return n in self.done_w.get(world, [])

    def mark_done(self, world: str, n: int, *, note: str = "", xp: int = 0) -> bool:
        """Record a finished workstream; return False if it already was."""
        lst = self.done_w.setdefault(world, [])
        if n in lst:
            return False
        lst.append(n)
        self.log.append(LogEntry(world=world, n=n, note=note, xp=xp))
        self.xp += xp
        return True

    def undo(self, world: str, n: int) -> int:
        """Un-claim a workstream; return the XP handed back."""
        lst = self.done_w.get(world, [])
        if n not in lst:
            return 0
        lst.remove(n)
        xp = sum(e.xp for e in self.log if e.world == world and e.n == n)
        self.log = [e for e in self.log if not (e.world == world and e.n == n)]
        self.xp = max(0, self.xp - xp)
        self.checks.pop(f"{world}:{n}", None)
        return xp

    def awarded(self, world: str, n: int) -> int:
        """The XP this stop has already paid out, over every claim it carries."""
        return sum(e.xp for e in self.log if e.world == world and e.n == n)

    def is_verified(self, world: str, n: int) -> bool:
        """True when a check confirmed this stop, not the game and not --force."""
        rec = self.checks.get(f"{world}:{n}")
        return bool(rec and rec.ok)

    def owed(self, world: str, n: int, full_xp: int) -> int:
        """What a passing check still has to pay a stop claimed at half price."""
        if not self.is_done(world, n):
            return 0
        return max(0, full_xp - self.awarded(world, n))

    def imported_stops(self) -> list[tuple[str, int]]:
        """Stops a progress code claimed that no check has confirmed since."""
        return sorted(
            {
                (e.world, e.n)
                for e in self.log
                if e.note == IMPORTED_NOTE and not self.is_verified(e.world, e.n)
            }
        )

    def total_done(self) -> int:
        return sum(len(v) for v in self.done_w.values())

    def today_count(self) -> int:
        today = dt.date.today().isoformat()
        return sum(1 for e in self.log if e.at.startswith(today))

    @classmethod
    def load(cls, path: Path = STATE_PATH) -> State:
        if not path.exists():
            return cls()
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        version = raw.get("version", 1)
        if version > STATE_VERSION:
            raise ValueError(
                f"{path} is version {version}; this vibe reads up to "
                f"{STATE_VERSION}. Update the tool (git pull, uv sync)."
            )
        if version == 1:
            raw = _migrate_v1(raw)
        return cls.model_validate(raw)

    def save(self, path: Path = STATE_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            self.model_dump_json(by_alias=True, indent=2) + "\n", encoding="utf-8"
        )

    def to_code(self) -> str:
        """The base64url progress code the game imports."""
        payload = {
            "v": CODE_VERSION,
            "name": self.name,
            "done": list(self.done),
            "doneW": self.done_w,
            "path": self.path,
            "xp": self.xp,
            "artifacts": list(self.artifacts),
            # Added inside version 2: an older reader ignores the key and
            # keeps working, so the code version does not move for it.
            "mentors": list(self.mentors),
            "artifactsBuilt": list(self.artifacts_built),
            "items": list(self.items),
            "ach": list(self.ach),
            "wear": list(self.wear),
            "interests": list(self.interests),
            "pet": self.pet,
            "topics": list(self.roadmap_done),
        }
        raw = json.dumps(payload, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    def merge_code(self, code: str) -> dict[str, Any]:
        """Merge a progress code from the game or another machine.

        Returns:
            The decoded payload.

        Raises:
            ValueError: on a malformed code or a newer code version.
        """
        payload = decode_code(code)
        if payload.get("name"):
            self.name = str(payload["name"])
        done_w = payload.get("doneW") or {"campus": payload.get("done", [])}
        for world, lst in done_w.items():
            for n in lst:
                n = int(n)
                if 1 <= n <= 8 and n not in self.done_w.setdefault(world, []):
                    self.done_w[world].append(n)
        self.path.update(
            {str(k): str(v) for k, v in (payload.get("path") or {}).items()}
        )
        if isinstance(payload.get("xp"), int):
            self.xp = max(self.xp, payload["xp"])
        for a in payload.get("artifacts") or []:
            if str(a) not in self.artifacts:
                self.artifacts.append(str(a))
        for m in payload.get("mentors") or []:
            if str(m) not in self.mentors:
                self.mentors.append(str(m))
        for a in payload.get("artifactsBuilt") or []:
            if str(a) not in self.artifacts_built:
                self.artifacts_built.append(str(a))
        for key in ("items", "ach", "wear"):
            mine: list[str] = getattr(self, key)
            for value in payload.get(key) or []:
                if str(value) not in mine:
                    mine.append(str(value))
        # The companion is one choice, not a set, so the code overwrites it.
        if payload.get("pet"):
            self.pet = check_pet(str(payload["pet"]))
                # An interest is a set, so a code adds a shelf and never removes one:
        # a choice made on the other machine is news, not a correction.
        for shelf in payload.get("interests") or []:
            if str(shelf) not in self.interests:
                self.interests.append(str(shelf))
        # A topic read stays read: the code adds ids and never takes one away.
        for topic_id in payload.get("topics") or []:
            if str(topic_id) not in self.roadmap_done:
                self.roadmap_done.append(str(topic_id))
        return payload


def decode_code(code: str) -> dict[str, Any]:
    raw = code.strip() + "=" * (-len(code.strip()) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(raw))
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError("that is not a valid progress code") from e
    version = int(payload.get("v", 1))
    if version > CODE_VERSION:
        raise ValueError(
            f"progress code version {version} is newer than this tool "
            f"understands ({CODE_VERSION}); update the tool"
        )
    return payload


def _migrate_v1(raw: dict[str, Any]) -> dict[str, Any]:
    done_w = raw.get("doneW") or {w: [] for w in WORLDS}
    if raw.get("done") and not done_w.get("campus"):
        done_w["campus"] = list(raw["done"])
    log = [
        {
            "world": "campus",
            "n": e["n"],
            "at": e.get("at", _now()),
            "note": e.get("note", ""),
        }
        for e in raw.get("log", [])
        if "n" in e
    ]
    return {
        "version": STATE_VERSION,
        "name": raw.get("name", PLACEHOLDER),
        "doneW": {
            w: [int(n) for n in done_w.get(w, [])] for w in set(WORLDS) | set(done_w)
        },
        "path": raw.get("path", {}),
        "log": log,
        "xp": 0,
    }
