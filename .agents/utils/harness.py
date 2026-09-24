#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jinja2>=3.1,<4"]
# ///
"""The harness: one source for every agent client, and the files rendered from it.

A person edits `config.toml` at the repository root; the profiles, the model
table, the roles, the hooks and the policy live under `.agents/conf/`. This tool
renders what each client reads (`.claude/settings.json`, `.claude/agents/`,
`.codex/config.toml`, `.codex/hooks.json`, `.codex/agents/`, `CLAUDE.md`) and
records a hash of every output and every input in `.agents/generated.lock`.
`.agents/README.md` is the map, DECISION #193 sections 1 to 3 the reasons.

    uv run python .agents/utils/harness.py sync    render, link skills, write the lock
    python3 .agents/utils/harness.py check         exit 1 on drift since the last sync
    python3 .agents/utils/harness.py doctor        links, schemas, chains, lock, trust
    python3 .agents/utils/harness.py explain       each value, its source, when it acts
    python3 .agents/utils/harness.py pick <role> --provider claude|codex [--usage 0.7]

Standard library only, so a hook and CI can run it with a bare python3 of 3.11
or newer; `sync` alone renders text with Jinja2, declared in the header above.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # the system python on a Mac is 3.9
    raise SystemExit("harness.py needs Python 3.11 or newer (tomllib)") from None

ROOT = Path(__file__).resolve().parents[2]
VERSION = 1
LOCK = ".agents/generated.lock"
OVERLAY = ".agents/config.local.toml"
TEMPLATES = ".agents/templates"
SYNC = "uv run python .agents/utils/harness.py sync"
# What sync reads. Tracked files only: a private overlay or a stray file in one
# of these folders never reaches a committed output.
INPUT_DIRS = (".agents/conf/", ".agents/context/", ".agents/templates/")
INPUT_FILES = ("config.toml", ".agents/utils/harness.py")
# The hook dispatcher's tree joins the digest once it exists (A4).
INPUT_LATER = (".agents/hooks/",)

# The client a session runs in, and whose models it may use: a session never
# switches provider (F156, F157).
PROVIDERS = {"claude": "claude", "codex": "openai", "gemini": None, "aider": None}
SAFEGUARDS = ("strict", "standard", "light")
AUTONOMY = ("pair", "lead", "ralph")
# F162: Claude runs low to max and Haiku takes no effort at all; Codex runs low
# to ultra. So max is a Claude level and ultra a Codex one, each a client's top.
EFFORTS = {
    "claude": ("low", "medium", "high", "xhigh", "max"),
    "openai": ("low", "medium", "high", "xhigh", "ultra"),
}
NO_EFFORT = ("claude-haiku-",)

PROFILE = {
    "version": int,
    "safeguards": SAFEGUARDS,
    "runner": ("compose", "native-sandbox"),
    # Codex command networking stays off unless a tested proxy is configured;
    # the allowlist never filters hosted tools (A3, F083).
    "network": ("off", "allowlist"),
    "escalation": ("deny", "on-request"),
    "local_checks": ("affected-plus-security", "affected", "nearest"),
    "review": {"independent": int, "second": ("deterministic",)},
    "effort": ("models",),
    "mcp_servers": (0, "from-conf"),
    "loop": {
        "blocks_no_progress": int,
        "blocks_max": int,
        "iterations": int,
        "wall_minutes": int,
    },
    "context": {
        "digest_max_chars": int,
        "tool_output_max_chars": int,
        "read_max_kb": int,
        "agents_md_chain_max_kb": int,
    },
    # No bypassPermissions and no danger-full-access: those belong to the
    # verified container alone, never to a host profile (A6).
    "claude": {
        "failIfUnavailable": bool,
        "allowUnsandboxedCommands": bool,
        "defaultMode": ("plan", "default", "acceptEdits"),
    },
    "codex": {
        "sandbox_mode": ("read-only", "workspace-write"),
        # "untrusted" is retired and may stop Codex from starting (F058).
        "approval_policy": ("on-request", "never"),
    },
}
# The floor: an overlay or a root knob may move a value towards the front of
# its tuple, never back; limits go down only; the review count goes up only.
STRONGER = {
    "safeguards": SAFEGUARDS,
    "runner": ("compose", "native-sandbox"),
    "network": ("off", "allowlist"),
    "escalation": ("deny", "on-request"),
    "local_checks": ("affected-plus-security", "affected", "nearest"),
    "mcp_servers": (0, "from-conf"),
    "claude.failIfUnavailable": (True, False),
    "claude.allowUnsandboxedCommands": (False, True),
    "claude.defaultMode": ("plan", "default", "acceptEdits"),
    "codex.sandbox_mode": ("read-only", "workspace-write"),
}
DOWNWARD = ("loop.", "context.")
UPWARD = ("review.independent",)

# When a change takes effect. "now": read at every harness call. "next spawn":
# a new agent. "next session, after sync": rendered into a file the client
# reads once at start (F007, F024). Codex hooks also need /hooks (F068, F070).
APPLIES = {
    "version": "now",
    "profile": "next session, after sync",
    "safeguards": "next session, after sync",
    "autonomy": "next spawn",
    "providers": "next session, after sync",
    "agents": "next spawn",
    "models": "next spawn",
    "usage": "now",
    "runner": "next spawn",
    "network": "next session, after sync",
    "escalation": "next spawn",
    "local_checks": "now",
    "review": "now",
    "effort": "next spawn",
    "mcp_servers": "next session, after sync",
    "loop": "next spawn",
    "context": "next session, after sync",
    "claude": "next session, after sync",
    "codex": "next session, after sync",
    "roles": "next spawn",
    "hooks": "claude: next session, after sync; codex: after sync and /hooks",
    "policy": "next session, after sync",
}
# The versions whose hooks.state key shape this reader was checked against
# (F070): on any other, hook trust is unknown rather than guessed.
CODEX_TESTED = ("0.156.1",)


class Bad(Exception):
    """A source that does not say what it has to. Always names the file."""


class Refused(Bad):
    """An effective value weaker than the tracked floor: nothing may spawn."""


class Paused(Exception):
    """The plan window is past stop_at: spawns wait for it to reset."""


# ---------------------------------------------------------------- reading


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def read_toml(path: Path, root: Path = ROOT) -> dict:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Bad(f"{_rel(path, root)}: missing") from None
    except tomllib.TOMLDecodeError as e:
        raise Bad(f"{_rel(path, root)}: {e}") from None
    if data.get("version") != VERSION:
        raise Bad(
            f"{_rel(path, root)}: version = {data.get('version')!r}; this harness "
            f"reads version {VERSION} and refuses any other"
        )
    return data


def tracked(root: Path, *prefixes: str) -> list[str]:
    """Tracked files under the prefixes, or every file on disk when this is not
    a git checkout (a stamp before `git init`)."""
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *prefixes],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode == 0:
        return sorted(n for n in out.stdout.split("\0") if n)
    found = []
    for p in prefixes:
        base = root / p
        if base.is_file():
            found.append(p)
        elif base.is_dir():
            found += [f.relative_to(root).as_posix() for f in base.rglob("*")]
    return sorted(f for f in found if (root / f).is_file())


def untracked(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--others", "--exclude-standard"]
        + ["--", *INPUT_DIRS],
        capture_output=True,
        text=True,
        check=False,
    )
    return sorted(n for n in out.stdout.split("\0") if n)


def _shape(data: object, shape: object, where: str, partial: bool = False) -> None:
    """Every key known, every value of the right kind: an unknown key is an
    error here, because a client that ignores it would look fine and do nothing."""
    if isinstance(shape, dict):
        if not isinstance(data, dict):
            raise Bad(f"{where}: a table, got {data!r}")
        unknown = sorted(set(data) - set(shape))
        if unknown:
            raise Bad(f"{where}: unknown key {', '.join(unknown)}")
        missing = sorted(set(shape) - set(data))
        if missing and not partial:
            raise Bad(f"{where}: missing {', '.join(missing)}")
        for k, v in data.items():
            _shape(v, shape[k], f"{where}: {k}", partial)
    elif isinstance(shape, tuple):
        if isinstance(data, bool) or data not in shape:
            options = " | ".join(repr(x) for x in shape)
            raise Bad(f"{where} = {data!r}; one of {options}")
    elif shape is bool:
        if not isinstance(data, bool):
            raise Bad(f"{where} = {data!r}; true or false")
    elif shape is int:
        if isinstance(data, bool) or not isinstance(data, int) or data < 0:
            raise Bad(f"{where} = {data!r}; a whole number")
    elif not isinstance(data, shape):  # type: ignore[arg-type]
        raise Bad(f"{where} = {data!r}; a {shape.__name__}")  # type: ignore[union-attr]


def flat(data: dict, prefix: str = "") -> dict[str, object]:
    out: dict[str, object] = {}
    for k, v in data.items():
        if isinstance(v, dict):
            out |= flat(v, f"{prefix}{k}.")
        else:
            out[f"{prefix}{k}"] = v
    return out


def load_config(root: Path = ROOT) -> dict:
    path = root / "config.toml"
    data = read_toml(path, root)
    shape = {
        "version": int,
        "profile": str,
        "safeguards": ("profile", *SAFEGUARDS),
        "autonomy": AUTONOMY,
        "providers": list,
        "agents": int,
        "models": str,
        "usage": dict,
    }
    _shape(data, shape, "config.toml")
    for p in data["providers"]:
        if p not in PROVIDERS:
            raise Bad(f"config.toml: providers names {p!r}; one of {list(PROVIDERS)}")
    if not data["providers"] or len(set(data["providers"])) != len(data["providers"]):
        raise Bad("config.toml: providers is empty or names one twice")
    if not 1 <= data["agents"] <= 20:  # the client refuses a 21st subagent (F120)
        raise Bad(f"config.toml: agents = {data['agents']}; between 1 and 20")
    for vendor, limits in data["usage"].items():
        where = f"config.toml: usage.{vendor}"
        if vendor not in EFFORTS:
            raise Bad(f"{where}: unknown; one of {list(EFFORTS)}")
        _shape(limits, {"plan": str, "slow_at": float, "stop_at": float}, where)
        if not 0 <= limits["slow_at"] <= limits["stop_at"] <= 1:
            raise Bad(f"{where}: 0 <= slow_at <= stop_at <= 1")
    for key, folder in (("profile", "profiles"), ("models", "models")):
        if not (root / ".agents" / "conf" / folder / f"{data[key]}.toml").is_file():
            raise Bad(
                f"config.toml: {key} = {data[key]!r}, and there is no "
                f".agents/conf/{folder}/{data[key]}.toml"
            )
    return data


def load_profile(root: Path, name: str) -> dict:
    path = root / ".agents" / "conf" / "profiles" / f"{name}.toml"
    data = read_toml(path, root)
    _shape(data, PROFILE, _rel(path, root))
    return data


def load_models(root: Path, name: str) -> dict:
    path = root / ".agents" / "conf" / "models" / f"{name}.toml"
    where = _rel(path, root)
    data = read_toml(path, root)
    shape = {
        "version": int,
        "fallback": ("report-before-switch",),
        "ids": dict,
        "requested": dict,
        "roles": dict,
    }
    _shape({"requested": {}, **data}, shape, where)
    for vendor, ids in data["ids"].items():
        if vendor not in EFFORTS or not isinstance(ids, dict):
            raise Bad(f"{where}: ids.{vendor}; one of {list(EFFORTS)}, a table")
    for vendor, ids in data.get("requested", {}).items():
        if vendor not in EFFORTS or not isinstance(ids, list):
            raise Bad(f"{where}: requested.{vendor}; a list under a known vendor")
    for rname, role in data["roles"].items():
        at = f"{where}: roles.{rname}"
        vendors = [v for v in EFFORTS if v in role]
        _shape(role, {**dict.fromkeys(vendors, list), "effort": dict}, at)
        if not vendors:
            raise Bad(f"{at}: names no model")
        if sorted(role["effort"]) != sorted(vendors):
            raise Bad(f"{at}: effort needs exactly one level per vendor it names")
        for vendor in vendors:
            for alias in role[vendor]:
                if alias not in data["ids"].get(vendor, {}):
                    raise Bad(f"{at}: {alias!r} is not in ids.{vendor}")
                model_effort(vendor, data["ids"][vendor][alias], role["effort"][vendor])
    return data


def model_effort(vendor: str, model_id: str, effort: str) -> str | None:
    """The effort a model is launched with: refused when the client has no such
    level, dropped for a model that takes none."""
    if effort not in EFFORTS[vendor]:
        raise Bad(
            f"effort {effort!r} is not a {vendor} level ({', '.join(EFFORTS[vendor])})"
        )
    return None if model_id.startswith(NO_EFFORT) else effort


def load_roles(root: Path, models: dict) -> list[dict]:
    shape = {
        "version": int,
        "name": str,
        "description": str,
        "model_role": str,
        "instructions": str,
        "claude": {"tools": str},
    }
    roles = []
    for rel in tracked(root, ".agents/conf/roles/"):
        if not rel.endswith(".toml"):
            continue
        data = read_toml(root / rel, root)
        _shape(data, shape, rel, partial=True)
        for key in ("name", "description", "instructions"):
            if key not in data:
                raise Bad(f"{rel}: missing {key}")
        if data["name"] != Path(rel).stem:
            raise Bad(f"{rel}: name = {data['name']!r}, the file is {Path(rel).name}")
        if data.get("model_role", "") and data["model_role"] not in models["roles"]:
            raise Bad(f"{rel}: model_role {data['model_role']!r} is not in the table")
        roles.append(data)
    return roles


def load_hooks(root: Path) -> list[dict]:
    path = root / ".agents" / "conf" / "hooks.toml"
    data = read_toml(path, root)
    where = _rel(path, root)
    handler = {
        "event": str,
        "matcher": str,
        "command": str,
        "timeout": int,
        "statusMessage": str,
        "additionalContextLimit": int,
    }
    over = {k: v for k, v in handler.items() if k != "event"}
    _shape(data, {"version": int, "hooks": list}, where)
    for i, h in enumerate(data["hooks"]):
        _shape(
            h, {**handler, "claude": over, "codex": over}, f"{where}: hooks[{i}]", True
        )
        if not all(k in h for k in ("event", "command", "timeout")):
            raise Bad(f"{where}: hooks[{i}] needs event, command and timeout")
    return data["hooks"]


def load_policy(root: Path) -> dict:
    path = root / ".agents" / "conf" / "policy.toml"
    data = read_toml(path, root)
    shape = {
        "version": int,
        "claude": {"deny": list, "ask": list, "sandbox": {"enabled": bool}},
    }
    _shape(data, shape, _rel(path, root))
    return data


def load_repo(root: Path) -> dict:
    path = root / ".agents" / "conf" / "repo.toml"
    data = read_toml(path, root)
    shape = {
        "version": int,
        "name": str,
        "main": str,
        "board": str,
        "skills": str,
        "claude_skills": str,
    }
    _shape(data, shape, _rel(path, root))
    return data


# ---------------------------------------------------------------- effective


@dataclass(frozen=True, slots=True)
class Value:
    value: object
    source: str


def _floor(key: str, floor: Value, new: object, source: str) -> None:
    weaker = False
    if key in STRONGER:
        order = STRONGER[key]
        weaker = order.index(new) > order.index(floor.value)  # type: ignore[arg-type]
    elif key.startswith(DOWNWARD):
        weaker = new > floor.value  # type: ignore[operator]
    elif key in UPWARD:
        weaker = new < floor.value  # type: ignore[operator]
    elif new != floor.value and key not in ("codex.approval_policy",):
        weaker = True
    if weaker:
        raise Refused(
            f"{source}: {key} = {new!r} is weaker than {floor.value!r} in "
            f"{floor.source}; a weaker floor needs a reviewed change to the "
            f"tracked profile, never an overlay"
        )


def effective(root: Path = ROOT, overlay: bool = True) -> tuple[dict, dict[str, Value]]:
    """The values a spawn gets: the profile, the root safeguards knob, then the
    private overlay, each checked against the tracked floor before anything
    starts (A3). Rendering passes overlay=False: tracked input only."""
    config = load_config(root)
    ppath = f".agents/conf/profiles/{config['profile']}.toml"
    profile = load_profile(root, config["profile"])
    values = {k: Value(v, ppath) for k, v in flat(profile).items() if k != "version"}
    if config["safeguards"] != "profile":
        _floor("safeguards", values["safeguards"], config["safeguards"], "config.toml")
        values["safeguards"] = Value(config["safeguards"], "config.toml")
    path = root / OVERLAY
    if overlay and path.is_file():
        data = read_toml(path, root)
        data.pop("version")
        _shape(data, PROFILE, OVERLAY, partial=True)
        for key, new in flat(data).items():
            _floor(key, values[key], new, OVERLAY)
            values[key] = Value(new, OVERLAY)
    if config["autonomy"] == "ralph" and values["runner"].value != "compose":
        raise Refused(
            "config.toml: autonomy = 'ralph' runs only inside the verified strict "
            "container (runner 'compose'), never on the host"
        )
    return config, values


def role_model(models: dict, mrole: str, vendor: str, step: int = 0) -> tuple:
    table = models["roles"][mrole]
    aliases = table.get(vendor)
    if not aliases:
        return None, None
    model_id = models["ids"][vendor][aliases[min(step, len(aliases) - 1)]]
    return model_id, model_effort(vendor, model_id, table["effort"][vendor])


def pick(
    role: str, provider: str, usage: float | None = None, root: Path = ROOT
) -> tuple[str, str | None]:
    """The model and effort to spawn a role with, on the provider the session
    already runs on. Never another provider's model: switching provider is a
    spawn decision a person makes, and it is logged (F156, F157)."""
    config, _ = effective(root)
    if provider not in config["providers"]:
        raise Bad(f"provider {provider!r} is not in config.toml providers")
    vendor = PROVIDERS[provider]
    if vendor is None:
        raise Bad(f"provider {provider!r} has no model table here")
    models = load_models(root, config["models"])
    mrole = role
    agents = {r["name"]: r for r in load_roles(root, models)}
    if role in agents:
        mrole = agents[role].get("model_role", "")
        if not mrole:
            raise Bad(f"role {role!r} runs on the session's own model")
    if mrole not in models["roles"]:
        raise Bad(f"no role {role!r} in the roles or the model table")
    step = 0
    limits = config["usage"].get(vendor)
    if usage is not None and limits:
        if usage >= limits["stop_at"]:
            raise Paused(f"{vendor} usage {usage:.0%} is past stop_at; wait for reset")
        if usage >= limits["slow_at"]:
            step = 1
    model_id, effort = role_model(models, mrole, vendor, step)
    if model_id is None:
        raise Bad(
            f"role {mrole!r} names no {vendor} model, and a session never switches "
            f"provider; spawn it from a {vendor} session instead"
        )
    return model_id, effort


# ---------------------------------------------------------------- rendering


def _header(src: str) -> str:
    text = f"Rendered by .agents/utils/harness.py sync from {src}; edit the source, "
    text += "then sync."
    return "".join(f"# {line}\n" for line in textwrap.wrap(text, 78))


def _toml_str(s: str) -> str:
    if "\n" in s:
        return '"""\n' + s.replace("\\", "\\\\").replace('"""', '""\\"') + '"""'
    return json.dumps(s, ensure_ascii=False)


def _toml_value(v: object) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int | float):
        return str(v)
    if isinstance(v, str):
        return _toml_str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    raise Bad(f"cannot write {v!r} as TOML")


def _toml_key(k: str) -> str:
    return k if re.fullmatch(r"[A-Za-z0-9_-]+", k) else json.dumps(k)


def dump_toml(doc: dict, header: str = "") -> str:
    """A small TOML writer for flat documents with one level of tables, checked
    by reading its own output back."""
    lines = [header.rstrip("\n")] if header else []
    for k, v in doc.items():
        if not isinstance(v, dict):
            lines.append(f"{_toml_key(k)} = {_toml_value(v)}")
    for k, v in doc.items():
        if isinstance(v, dict):
            lines += ["", f"[{_toml_key(k)}]"]
            lines += [f"{_toml_key(a)} = {_toml_value(b)}" for a, b in v.items()]
    text = "\n".join(lines).lstrip("\n") + "\n"
    if tomllib.loads(text) != doc:
        raise Bad("the TOML writer did not round-trip; nothing written")
    return text


@dataclass(frozen=True, slots=True)
class Source:
    root: Path
    config: dict
    values: dict[str, Value]
    models: dict
    roles: list[dict]
    hooks: list[dict]
    policy: dict
    repo: dict


def load(root: Path = ROOT, overlay: bool = False) -> Source:
    config, values = effective(root, overlay)
    models = load_models(root, config["models"])
    return Source(
        root,
        config,
        values,
        models,
        load_roles(root, models),
        load_hooks(root),
        load_policy(root),
        load_repo(root),
    )


def hooks_for(src: Source, client: str) -> dict:
    events: dict[str, list] = {}
    for h in src.hooks:
        h = {**h, **h.get(client, {})}
        handler = {"type": "command", "command": h["command"]}
        for extra in ("statusMessage", "additionalContextLimit"):
            if extra in h:
                handler[extra] = h[extra]
        handler["timeout"] = h["timeout"]
        group = {"matcher": h["matcher"]} if "matcher" in h else {}
        events.setdefault(h["event"], []).append({**group, "hooks": [handler]})
    return {"hooks": events}


def claude_settings(src: Source) -> str:
    v, pol = src.values, src.policy["claude"]
    settings = {
        "permissions": {
            "deny": pol["deny"],
            "ask": pol["ask"],
            "defaultMode": v["claude.defaultMode"].value,
        },
        "sandbox": {
            "enabled": pol["sandbox"]["enabled"],
            "failIfUnavailable": v["claude.failIfUnavailable"].value,
            "allowUnsandboxedCommands": v["claude.allowUnsandboxedCommands"].value,
        },
        **hooks_for(src, "claude"),
    }
    return json.dumps(settings, indent=2, ensure_ascii=False) + "\n"


def codex_config(src: Source) -> str:
    """Resolved values only. Never profile, profiles, a provider, a base URL,
    notify or otel, which a project file may not set (F053, F054); one sandbox
    style, sandbox_mode, since permission profiles cannot combine with it (F081)."""
    v = src.values
    # No writable root: the board is added with --add-dir at launch (A2 as
    # amended), and command networking stays off, its default in
    # workspace-write (F079), until a tested proxy exists (A3).
    doc = {
        "sandbox_mode": v["codex.sandbox_mode"].value,
        "approval_policy": v["codex.approval_policy"].value,
    }
    header = _header(
        f"config.toml and .agents/conf/profiles/{src.config['profile']}.toml"
    ) + (
        "# No writable root is tracked: from a linked worktree a relative one is not\n"
        "# a directory and stops every shell tool. `just codex` adds the board with\n"
        "# --add-dir and the absolute git common dir (work/BOARD.md).\n"
    )
    return dump_toml(doc, header)


def codex_agent(src: Source, role: dict) -> str:
    doc: dict = {"name": role["name"], "description": role["description"]}
    if role.get("model_role"):
        model_id, effort = role_model(src.models, role["model_role"], "openai")
        if model_id:
            doc["model"] = model_id
            if effort:
                doc["model_reasoning_effort"] = effort
    doc["developer_instructions"] = role["instructions"]
    header = _header(
        f".agents/conf/roles/{role['name']}.toml and "
        f".agents/conf/models/{src.config['models']}.toml"
    )
    return dump_toml(doc, header)


FIRST_LINE = re.compile(r"^\{#-?\s*output:\s*(\S+)(?:\s+when\s+(\w+))?\s*-?#\}")


def templates(root: Path) -> list[tuple[str, str, str | None]]:
    """(template, output pattern, provider) from each template's first line, so
    a new output is a new template and no change here."""
    out = []
    for rel in tracked(root, TEMPLATES + "/"):
        first = (root / rel).read_text(encoding="utf-8").split("\n", 1)[0]
        m = FIRST_LINE.match(first)
        if not m:
            raise Bad(f"{rel}: the first line names no output ({{#- output: path -#}})")
        out.append((rel, m.group(1), m.group(2)))
    return out


def rendered_paths(root: Path = ROOT) -> list[str]:
    """Every path sync writes, worked out from the sources without Jinja2, so a
    standard-library caller such as tools/work.py knows what the generator owns."""
    config = load_config(root)
    providers = set(config["providers"])
    roles = [
        Path(r).stem
        for r in tracked(root, ".agents/conf/roles/")
        if r.endswith(".toml")
    ]
    out = []
    if "claude" in providers:
        out.append(".claude/settings.json")
    if "codex" in providers:
        out += [".codex/config.toml", ".codex/hooks.json"]
        out += [f".codex/agents/{r}.toml" for r in roles]
    for _, target, when in templates(root):
        if when and when not in providers:
            continue
        if "{role}" in target:
            out += [target.replace("{role}", r) for r in roles]
        else:
            out.append(target)
    return sorted(set(out))


def _jinja():
    try:
        return importlib.import_module("jinja2")
    except ModuleNotFoundError:
        pass
    uv = shutil.which("uv")
    if os.environ.get("HARNESS_REEXEC") or not uv:
        raise SystemExit(
            "harness.py sync renders with Jinja2: `uv run --script "
            ".agents/utils/harness.py sync` provides it from this file's header"
        )
    # The project environment lacks it; this file's header declares it (PEP 723).
    os.environ["HARNESS_REEXEC"] = "1"
    os.execv(uv, [uv, "run", "--quiet", "--script", __file__, *sys.argv[1:]])


def render(src: Source, text: bool = True) -> dict[str, str]:
    """Every output as the sources say it should be. text=False leaves out the
    Jinja2 outputs, for a caller with the standard library only."""
    providers = set(src.config["providers"])
    out: dict[str, str] = {}
    if "claude" in providers:
        out[".claude/settings.json"] = claude_settings(src)
    if "codex" in providers:
        out[".codex/config.toml"] = codex_config(src)
        out[".codex/hooks.json"] = (
            json.dumps(hooks_for(src, "codex"), indent=2, ensure_ascii=False) + "\n"
        )
        for role in src.roles:
            out[f".codex/agents/{role['name']}.toml"] = codex_agent(src, role)
    if not text:
        return out
    jinja2 = _jinja()
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(src.root / TEMPLATES)),
        keep_trailing_newline=True,
        undefined=jinja2.StrictUndefined,
        autoescape=False,  # Markdown and TOML from our own sources, never HTML
    )
    context = {
        Path(r).stem: (src.root / r).read_text(encoding="utf-8")
        for r in tracked(src.root, ".agents/context/")
        if r.endswith(".md")
    }
    for rel, target, when in templates(src.root):
        if when and when not in providers:
            continue
        tpl = env.get_template(Path(rel).relative_to(TEMPLATES).as_posix())
        if "{role}" not in target:
            out[target] = tpl.render(context=context, config=src.config)
            continue
        for role in src.roles:
            model_id, effort = (None, None)
            if role.get("model_role"):
                model_id, effort = role_model(src.models, role["model_role"], "claude")
            view = {
                "claude": {},
                **role,
                "claude_model": model_id,
                "claude_effort": effort,
            }
            out[target.replace("{role}", role["name"])] = tpl.render(role=view)
    return out


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def inputs(root: Path) -> list[str]:
    later = [p for p in INPUT_LATER if (root / p).exists()]
    return tracked(root, *INPUT_FILES, *INPUT_DIRS, *later)


def lock_text(root: Path, outputs: dict[str, str]) -> str:
    doc = {
        "version": VERSION,
        "inputs": {p: digest((root / p).read_bytes()) for p in inputs(root)},
        "outputs": {p: digest(t.encode()) for p, t in sorted(outputs.items())},
    }
    header = (
        "# Written by .agents/utils/harness.py sync; never edit it by hand. check\n"
        "# compares the tree with it: an output that moved was edited by hand, an\n"
        "# input that moved was not synced. [inputs] is also the reviewed digest of\n"
        "# the policy and the hooks (A4)."
    )
    return dump_toml(doc, header)


def read_lock(root: Path) -> dict:
    data = read_toml(root / LOCK, root)
    _shape(data, {"version": int, "inputs": dict, "outputs": dict}, LOCK)
    return data


def sync(root: Path = ROOT) -> list[str]:
    """Render every output from tracked input, remove what an earlier sync
    wrote and nothing renders now, write the lock, link the skills."""
    src = load(root)
    outs = render(src)
    old = set(read_lock(root)["outputs"]) if (root / LOCK).is_file() else set()
    done = []
    for rel, text in outs.items():
        path = root / rel
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            done.append(f"wrote {rel}")
    for rel in sorted(old - set(outs)):
        if (root / rel).is_file():
            (root / rel).unlink()
            done.append(f"removed {rel}")
    text = lock_text(root, outs)
    if not (root / LOCK).is_file() or (root / LOCK).read_text() != text:
        (root / LOCK).write_text(text, encoding="utf-8")
        done.append(f"wrote {LOCK}")
    return done + link_skills(root)


def check(root: Path = ROOT) -> list[str]:
    """What drifted: an output edited by hand, an input changed without a sync,
    or an output that differs from a fresh render. The Jinja2 outputs are
    re-rendered when Jinja2 is importable and compared by hash otherwise."""
    if not (root / LOCK).is_file():
        return [f"no {LOCK}: run {SYNC}"]
    lock, bad = read_lock(root), []
    now = {p: digest((root / p).read_bytes()) for p in inputs(root)}
    for p in sorted(set(now) | set(lock["inputs"])):
        if now.get(p) != lock["inputs"].get(p):
            bad.append(f"input changed since the last sync: {p}")
    expected = set(rendered_paths(root))
    for p in sorted(expected - set(lock["outputs"])):
        bad.append(f"not in the lock: {p}")
    for p in sorted(set(lock["outputs"]) - expected):
        bad.append(f"the lock lists {p}, which harness.py does not render")
    for p, h in sorted(lock["outputs"].items()):
        f = root / p
        if not f.is_file():
            bad.append(f"missing: {p}")
        elif digest(f.read_bytes()) != h:
            bad.append(f"edited by hand or stale: {p}")
    try:
        importlib.import_module("jinja2")
        text = True
    except ModuleNotFoundError:
        text = False
    for p, t in render(load(root), text=text).items():
        f = root / p
        if f.is_file() and f.read_text(encoding="utf-8") != t:
            bad.append(f"differs from a fresh render: {p}")
    return sorted(set(bad))


# ---------------------------------------------------------------- doctor


def symlinks_work(root: Path) -> bool:
    out = subprocess.run(
        ["git", "-C", str(root), "config", "--get", "core.symlinks"],
        capture_output=True,
        text=True,
        check=False,
    )
    return out.stdout.strip() != "false"  # F146: false checks links out as text


def _same_tree(a: Path, b: Path) -> bool:
    fa = {p.relative_to(a): p for p in a.rglob("*") if p.is_file()}
    fb = {p.relative_to(b): p for p in b.rglob("*") if p.is_file()}
    return fa.keys() == fb.keys() and all(
        fa[k].read_bytes() == fb[k].read_bytes() for k in fa
    )


def link_skills(root: Path = ROOT, can_link: bool | None = None) -> list[str]:
    """One relative link per skill in .claude/skills, repaired when it points
    elsewhere or nowhere, a copy where links cannot be made. Relative, because
    an absolute link dangles in a container and in another clone (F150)."""
    repo = load_repo(root)
    skills, dest = root / repo["skills"], root / repo["claude_skills"]
    if can_link is None:
        can_link = symlinks_work(root)
    wanted = sorted(d.name for d in skills.iterdir() if (d / "SKILL.md").is_file())
    dest.mkdir(parents=True, exist_ok=True)
    done = []
    for name in wanted:
        link, rel = dest / name, os.path.relpath(skills / name, dest)
        if link.is_symlink():
            if os.readlink(link) == rel and link.exists():
                continue
            link.unlink()
        elif link.exists():
            if not can_link and _same_tree(skills / name, link):
                continue
            shutil.rmtree(link)
        if can_link:
            try:
                link.symlink_to(rel, target_is_directory=True)
                done.append(f"linked {repo['claude_skills']}/{name}")
                continue
            except OSError:
                pass
        shutil.copytree(skills / name, link)
        done.append(f"copied {repo['claude_skills']}/{name}")
    for extra in sorted(dest.iterdir()):
        if extra.name not in wanted and extra.is_symlink():
            target = (dest / os.readlink(extra)).resolve()
            if not extra.exists() or target.is_relative_to(skills.resolve()):
                extra.unlink()
                done.append(f"removed {repo['claude_skills']}/{extra.name}")
    return done


def link_problems(root: Path) -> list[str]:
    repo = load_repo(root)
    skills, dest = root / repo["skills"], root / repo["claude_skills"]
    bad = []
    for d in sorted(skills.iterdir()):
        if not (d / "SKILL.md").is_file():
            continue
        link = dest / d.name
        if link.is_symlink():
            if os.path.isabs(os.readlink(link)):
                bad.append(f"{link.relative_to(root)} is an absolute link")
            elif not (link / "SKILL.md").is_file():
                bad.append(f"{link.relative_to(root)} dangles")
        elif not (link / "SKILL.md").is_file():
            bad.append(f"{link.relative_to(root)} is missing")
    return bad


def agents_chains(
    root: Path, files: list[str] | None = None
) -> list[tuple[str, int, list[str]]]:
    """Each root-to-leaf chain of instruction files as Codex reads it: at most
    one per directory, the override first, joined root-down into one budget
    that it truncates silently when crossed (F005, F006)."""
    if files is None:
        files = [
            f
            for f in tracked(root, ".")
            if Path(f).name in ("AGENTS.md", "AGENTS.override.md")
        ]
    by_dir: dict[str, str] = {}
    for f in sorted(files):
        d = Path(f).parent.as_posix()
        if d not in by_dir or Path(f).name == "AGENTS.override.md":
            by_dir[d] = f

    def ancestors(d: str) -> list[str]:
        parts = [] if d == "." else d.split("/")
        return ["."] + ["/".join(parts[: i + 1]) for i in range(len(parts))]

    leaves = [
        d for d in by_dir if not any(o != d and d in ancestors(o) for o in by_dir)
    ]
    out = []
    for leaf in sorted(leaves):
        chain = [by_dir[a] for a in ancestors(leaf) if a in by_dir]
        size = sum((root / f).stat().st_size for f in chain) + 2 * (len(chain) - 1)
        out.append((leaf, size, chain))
    return out


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def client_models(vendor: str) -> dict[str, set[str]] | None:
    """Model ids a client lists, with the effort levels it offers for each; None
    when this machine holds no list (Claude Code keeps none on disk)."""
    if vendor != "openai":
        return None
    try:
        data = json.loads((codex_home() / "models_cache.json").read_text())
        return {
            m["slug"]: {r["effort"] for r in m.get("supported_reasoning_levels", [])}
            for m in data["models"]
        }
    except (OSError, ValueError, KeyError, TypeError):
        return None


def model_problems(models: dict, lists: dict[str, dict | None]) -> tuple[list, list]:
    """(problems, notes): an id a client does not list is a problem; so is an
    effort the client does not offer for that model. A requested id the client
    now lists is a note."""
    bad, notes = [], []
    for vendor, ids in models["ids"].items():
        listed = lists.get(vendor)
        if listed is None:
            notes.append(f"{vendor} ids: unknown, no client model list on this machine")
            continue
        for alias, mid in ids.items():
            if mid not in listed:
                bad.append(
                    f"{vendor} {alias} = {mid} is not in the client's model list"
                )
        for rname, role in models["roles"].items():
            for alias in role.get(vendor, []):
                mid, effort = ids[alias], role["effort"][vendor]
                offered = listed.get(mid) or set()
                if offered and model_effort(vendor, mid, effort) not in offered:
                    bad.append(f"roles.{rname}: {mid} offers no effort {effort}")
        for mid in models.get("requested", {}).get(vendor, []):
            if mid in listed:
                notes.append(f"requested {mid} is listed by the client now: adopt it")
    return bad, notes


def main_checkout(root: Path) -> Path:
    out = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--path-format=absolute"]
        + ["--git-common-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    return Path(out.stdout.strip()).parent if out.returncode == 0 else root


def _codex_user_config() -> dict | None:
    try:
        return tomllib.loads((codex_home() / "config.toml").read_text())
    except FileNotFoundError:
        return {}
    except (OSError, tomllib.TOMLDecodeError):
        return None


def project_trust(root: Path) -> tuple[str, str]:
    """Whether Codex loads this project's .codex/ at all (F055). Codex 0.156.1
    decides by the checkout's own [projects] entry, else the main checkout's
    (config loader decision_for_dir), so a linked worktree inherits the main
    checkout's trust unless it carries an entry of its own."""
    own, main = root.resolve(), main_checkout(root)
    cfg = _codex_user_config()
    if cfg is None:
        return "unknown", "the Codex user config does not parse"
    projects = cfg.get("projects", {})
    for key in dict.fromkeys((str(own), str(main))):
        level = projects.get(key, {}).get("trust_level")
        if level is None:
            continue
        via = "" if key == str(own) else f", which {own} inherits"
        if level == "trusted":
            return "verified", f'projects."{key}".trust_level = "trusted"{via}'
        return "missing", f'projects."{key}".trust_level = "{level}"{via}'
    return "missing", f"{main} is not trusted: answer the prompt when codex starts here"


def codex_version() -> str | None:
    exe = shutil.which("codex")
    if not exe:
        return None
    try:
        out = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"(\d+\.\d+\.\d+)", out.stdout)
    return m.group(1) if m else None


def hook_trust(root: Path, version: str | None = None) -> tuple[str, str]:
    """Whether Codex runs this checkout's hooks, a separate question from project
    trust (A4). Offline this sees whether each handler has a trusted hash in the
    user config (F070); whether that hash matches the command now is the
    client's to say in /hooks, so it never reads as verified from here. A linked
    worktree runs the main checkout's .codex/hooks.json, keyed by that path
    (openai/codex PR 21969), so that is the file read and the key looked up."""
    version = version or codex_version()
    if version is None:
        return "unknown", "codex is not installed here"
    if version not in CODEX_TESTED:
        tested = ", ".join(CODEX_TESTED)
        return "unknown", f"codex {version}: this reader was tested on {tested}"
    path = main_checkout(root) / ".codex" / "hooks.json"
    try:
        events = json.loads(path.read_text())["hooks"]
    except (OSError, ValueError, KeyError):
        return "unknown", f"{path} does not parse"
    keys = [
        f"{path}:{re.sub(r'(?<!^)(?=[A-Z])', '_', ev).lower()}:{g}:{h}"
        for ev, groups in events.items()
        for g, group in enumerate(groups)
        for h, _ in enumerate(group["hooks"])
    ]
    cfg = _codex_user_config()
    if cfg is None:
        return "unknown", "the Codex user config does not parse"
    state = cfg.get("hooks", {}).get("state", {})
    missing = [k for k in keys if k not in state]
    if missing:
        return "missing", (
            f"{len(missing)} of {len(keys)} handlers have no trusted hash: run "
            f"/hooks in codex here"
        )
    return "unknown", "every handler has a hash; /hooks says whether it is current"


def doctor(root: Path = ROOT) -> tuple[list[str], list[str]]:
    """(problems, report). Offline: schemas, lock, skill links, the instruction
    chain, model ids, and Codex trust as two values. Trust is reported, not
    failed: an unattended start refuses anything but verified on both."""
    report, bad = [], []
    try:
        config, values = effective(root)
        models = load_models(root, config["models"])
        load(root)
        report.append(
            f"schemas: ok (profile {config['profile']}, models {config['models']})"
        )
    except Bad as e:
        return [f"schemas: {e}"], report
    for p in untracked(root):
        report.append(f"untracked input, ignored by sync until added: {p}")
    drift = check(root)
    bad += [f"lock: {d}" for d in drift]
    if not drift:
        report.append("lock: every output matches its sources")
    for action in link_skills(root):
        report.append(f"links: {action}")
    problems = link_problems(root)
    bad += [f"links: {p}" for p in problems]
    if not problems:
        report.append("links: every skill resolves through .claude/skills")
    limit = int(values["context.agents_md_chain_max_kb"].value) * 1024  # type: ignore[arg-type]
    for leaf, size, chain in agents_chains(root):
        line = f"chain {leaf}: {size} of {limit} bytes ({' + '.join(chain)})"
        (bad if size > limit else report).append(line)
    mbad, notes = model_problems(models, {v: client_models(v) for v in EFFORTS})
    bad += [f"models: {m}" for m in mbad]
    report += [f"models: {n}" for n in notes]
    if "codex" in config["providers"]:
        for name, (state, why) in (
            ("project trust", project_trust(root)),
            ("hook trust", hook_trust(root)),
        ):
            report.append(f"codex {name}: {state} ({why})")
    return bad, report


# ---------------------------------------------------------------- explain


def explain(root: Path = ROOT) -> list[dict]:
    """Every effective value with the file it comes from and when a change to
    it takes effect."""
    config, values = effective(root)
    rows = [
        {"key": k, "value": config[k], "source": "config.toml"}
        for k in ("version", "profile", "autonomy", "providers", "agents", "models")
    ]
    for vendor, limits in config["usage"].items():
        rows += [
            {"key": f"usage.{vendor}.{k}", "value": v, "source": "config.toml"}
            for k, v in limits.items()
        ]
    rows += [
        {"key": k, "value": v.value, "source": v.source} for k, v in values.items()
    ]
    mpath = f".agents/conf/models/{config['models']}.toml"
    models = load_models(root, config["models"])
    for mrole in models["roles"]:
        for vendor in EFFORTS:
            model_id, effort = role_model(models, mrole, vendor)
            if model_id:
                value = f"{model_id} effort {effort or 'none'}"
                key = f"models.{mrole}.{vendor}"
                rows.append({"key": key, "value": value, "source": mpath})
    for role in load_roles(root, models):
        name = role["name"]
        value = role.get("model_role") or "the session's own model"
        source = f".agents/conf/roles/{name}.toml"
        rows.append({"key": f"roles.{name}", "value": value, "source": source})
    for h in load_hooks(root):
        source = ".agents/conf/hooks.toml"
        rows.append(
            {"key": f"hooks.{h['event']}", "value": h["command"], "source": source}
        )
    for client, part in load_policy(root).items():
        if isinstance(part, dict):
            for k, v in flat(part).items():
                source = ".agents/conf/policy.toml"
                rows.append(
                    {"key": f"policy.{client}.{k}", "value": v, "source": source}
                )
    for row in rows:
        row["applies"] = APPLIES[row["key"].split(".", 1)[0]]
    return rows


# ---------------------------------------------------------------- the commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harness.py", description=__doc__.split("\n")[0]
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sync", help="render every output, link the skills, write the lock")
    sub.add_parser("check", help="exit 1 on drift")
    sub.add_parser("doctor", help="offline health: links, schemas, chains, lock, trust")
    ex = sub.add_parser("explain", help="every effective value and where it comes from")
    ex.add_argument("--json", action="store_true")
    pk = sub.add_parser("pick", help="the model and effort for a role on one provider")
    pk.add_argument("role")
    pk.add_argument("--provider", required=True, choices=sorted(PROVIDERS))
    pk.add_argument("--usage", type=float, help="share of the plan window used, 0 to 1")
    a = parser.parse_args(argv)
    try:
        if a.cmd == "sync":
            for line in sync():
                print(line)
            print("harness sync: done")
        elif a.cmd == "check":
            drift = check()
            for line in drift:
                print("drift:", line)
            if drift:
                print(f"harness check: {len(drift)} drifted; run {SYNC}")
                return 1
            print("harness check: OK")
        elif a.cmd == "doctor":
            bad, report = doctor()
            for line in report:
                print(line)
            for line in bad:
                print("PROBLEM", line)
            print("harness doctor:", "OK" if not bad else f"{len(bad)} problems")
            return 1 if bad else 0
        elif a.cmd == "explain":
            rows = explain()
            if a.json:
                print(json.dumps(rows, indent=2, default=str))
            else:
                for r in rows:
                    print(
                        f"{r['key']} = {r['value']!r}  [{r['source']}; {r['applies']}]"
                    )
        elif a.cmd == "pick":
            model_id, effort = pick(a.role, a.provider, a.usage)
            print(model_id if effort is None else f"{model_id} {effort}")
    except Paused as e:
        print(f"harness: paused: {e}", file=sys.stderr)
        return 3
    except Bad as e:
        print(f"harness: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
