"""The camp's dashboard: one self-contained HTML page, and the numbers behind it.

`vibe dashboard` writes workspace/dashboard.html from three sources the camp
already keeps: .vibe/state.json (the log and the checks), the Obsidian vault,
and workspace/data/scores.csv. Nothing is stored twice; every number here is
derived, so deleting the report loses nothing.

The page shares the game's design tokens (vibemap/palette.py, generated from
the same values as src/style.css) and the game's event shape: ts, kind, id,
world, with v for a number of seconds. Charts are inline SVG, so the file
opens offline, prints, and needs no library.
"""

from __future__ import annotations

import datetime as dt
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vibemap import campaign, project
from vibemap.palette import css_tokens
from vibemap.quests import level_for
from vibemap.state import State

KIND_LABEL = {
    "session": "Session started",
    "claim": "Stop delivered",
    "check": "Checks run",
    "verified": "Mentor verified",
    "built": "Artifact built for real",
    "artifact": "Artifact found",
}
KIND_HUE = {
    "claim": "var(--green-bright)",
    "verified": "var(--green-bright)",
    "built": "var(--green-bright)",
    "check": "var(--yellow)",
    "artifact": "var(--orange)",
    "session": "var(--blue-bright)",
}
DAYS = 7
STOPS_TOTAL = 32


@dataclass(frozen=True, slots=True)
class Event:
    """One thing that happened, in the shape the game and the CLI share."""

    ts: dt.datetime
    kind: str
    id: str
    world: str = "campus"
    v: float | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "ts": self.ts.isoformat(timespec="minutes"),
            "kind": self.kind,
            "id": self.id,
            "world": self.world,
        }
        if self.v is not None:
            out["v"] = self.v
        return out


def _parse(at: str) -> dt.datetime:
    """A timestamp the state wrote; an unreadable one is not a crash."""
    try:
        return dt.datetime.fromisoformat(at)
    except ValueError:
        return dt.datetime.now()


def events_from_state(st: State) -> list[Event]:
    """The log and the check records, as events, oldest first."""
    out = [
        Event(ts=_parse(e.at), kind="claim", id=str(e.n), world=e.world) for e in st.log
    ]
    for key, record in st.checks.items():
        world, _, n = key.partition(":")
        out.append(
            Event(
                ts=_parse(record.at),
                kind="check",
                id=n or key,
                world=world if n else "campus",
            )
        )
    for mentor in st.mentors:
        out.append(Event(ts=_parse(st.log[-1].at) if st.log else dt.datetime.now(),
                         kind="verified", id=mentor))  # fmt: skip
    for artifact in st.artifacts_built:
        out.append(Event(ts=_parse(st.log[-1].at) if st.log else dt.datetime.now(),
                         kind="built", id=artifact))  # fmt: skip
    return sorted(out, key=lambda e: e.ts)


def _streak(days: list[dt.date]) -> int:
    """Days in a row with something on them, ending today or yesterday."""
    seen = set(days)
    today = dt.date.today()
    cursor = today if today in seen else today - dt.timedelta(days=1)
    n = 0
    while cursor in seen:
        n += 1
        cursor -= dt.timedelta(days=1)
    return n


def _vault_notes(root: Path) -> int:
    folder = root / "vault"
    return len(list(folder.rglob("*.md"))) if folder.exists() else 0


def _scores(root: Path) -> dict[str, Any]:
    """The scores summary, or an empty one when workstream 3 is still to come."""
    path = root / "workspace" / "data" / "scores.csv"
    if not path.exists():
        return {"runs": 0, "best": 0, "best_by": "", "mean": 0.0, "players": []}
    from vibemap.scores import read_scores, summary  # noqa: PLC0415

    try:
        return summary(read_scores(path))
    except ValueError:
        # A renamed column is the workstream 3 lesson, not a reason to crash.
        return {"runs": 0, "best": 0, "best_by": "", "mean": 0.0, "players": []}


def numbers(st: State, root: Path | None = None) -> dict[str, Any]:
    """Every figure the report prints, and what `--json` returns."""
    root = root or project.root()
    events = events_from_state(st)
    today = dt.date.today()
    days = [today - dt.timedelta(days=i) for i in range(DAYS - 1, -1, -1)]
    per_day = {d: 0 for d in days}
    grid: dict[tuple[dt.date, int], int] = {}
    for e in events:
        day = e.ts.date()
        if day in per_day:
            per_day[day] += 1
            grid[(day, e.ts.hour)] = grid.get((day, e.ts.hour), 0) + 1
    # The log is where a claim records what it was worth, so the line is the
    # log's own numbers; a mentor or an artifact adds its XP to the total
    # without a log entry, which is why the tile can stand above the line.
    xp_day: dict[dt.date, int] = {}
    for entry in st.log:
        day = _parse(entry.at).date()
        xp_day[day] = xp_day.get(day, 0) + entry.xp
    age, level, _next = level_for(st.xp)
    worlds = campaign.evenings()
    return {
        "name": st.name,
        "xp": st.xp,
        "level": level,
        "age": age,
        "stops": st.total_done(),
        "stops_total": STOPS_TOTAL,
        "per_island": {w: len(st.done_w.get(w, [])) for w in worlds},
        "island_names": {w: ev.island for w, ev in worlds.items()},
        "mentors": len(st.mentors),
        "mentors_total": len(campaign.mentors()),
        "artifacts": len(st.artifacts),
        "artifacts_built": len(st.artifacts_built),
        "artifacts_total": len(campaign.artifacts()),
        "badges": list(st.badges),
        "checks": len(st.checks),
        "checks_green": sum(1 for c in st.checks.values() if c.ok),
        "notes": _vault_notes(root),
        "streak": _streak([e.ts.date() for e in events]),
        "days": [d.isoformat() for d in days],
        "per_day": [per_day[d] for d in days],
        "xp_day": {d.isoformat(): v for d, v in sorted(xp_day.items())},
        "heat": {f"{d.isoformat()}:{h}": n for (d, h), n in grid.items()},
        "scores": _scores(root),
        "events": [e.as_dict() for e in events[-20:]],
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# ---- chart primitives: the same shapes as src/game/89-dashboard.js ------------


def _esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def _svg(w: int, h: int, label: str, inner: str) -> str:
    return (
        f'<svg class="ch" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet"'
        f' role="img" aria-label="{_esc(label)}">{inner}</svg>'
    )


def spark(values: list[float], hue: str) -> str:
    """A shape, not a reading: no axis, no dots, one hue."""
    top = max(values, default=0)
    if len(values) < 2 or top <= 0:
        return ""
    w, h = 120, 26
    pts = [
        (2 + i * (w - 4) / (len(values) - 1), h - 2 - (v / top) * (h - 6))
        for i, v in enumerate(values)
    ]
    line = " ".join(
        f"{'L' if i else 'M'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts)
    )
    area = f"{line} L {w - 2:.1f} {h - 1} L 2 {h - 1} Z"
    return _svg(
        w,
        h,
        "Last seven days",
        f'<path d="{area}" fill="{hue}" fill-opacity=".12"/>'
        f'<path d="{line}" fill="none" stroke="{hue}" stroke-width="2"'
        ' stroke-linejoin="round" stroke-linecap="round"/>',
    )


def tile(label: str, value: str, caption: str, sparkline: str = "") -> str:
    return (
        f'<div class="tile"><span class="tl">{_esc(label)}</span>'
        f'<b class="tv">{value}</b>'
        f'<span class="tc">{_esc(caption)}</span>{sparkline}</div>'
    )


def ring(name: str, done: int, total: int) -> str:
    r = 26
    circumference = 2 * 3.141592653589793 * r
    hue = "var(--green-bright)" if done == total else "var(--yellow)"
    arc = (
        f'<circle cx="32" cy="32" r="{r}" fill="none" stroke="{hue}" stroke-width="7"'
        f' stroke-linecap="round" stroke-dasharray="'
        f'{circumference * done / total:.1f} {circumference:.1f}"'
        ' transform="rotate(-90 32 32)"/>'
        if done
        else ""
    )
    body = (
        f'<circle cx="32" cy="32" r="{r}" fill="none" stroke="var(--hairline-2)"'
        f' stroke-width="7"/>{arc}'
        f'<text x="32" y="36" text-anchor="middle" class="rt">{done}</text>'
    )
    return (
        f'<div class="ring">{_svg(64, 64, f"{name}: {done} of {total} stops", body)}'
        f'<span class="rl">{_esc(name)}</span>'
        f'<span class="rn">{done}/{total}</span></div>'
    )


def empty(msg: str) -> str:
    return f'<p class="small muted dash-empty">{_esc(msg)}</p>'


def _short_day(iso: str) -> str:
    return dt.date.fromisoformat(iso).strftime("%d %b")


def xp_line(data: dict[str, Any]) -> str:
    """Total XP over the days it was earned. One line, one axis."""
    series: list[tuple[str, int]] = []
    total = 0
    for day, gained in data["xp_day"].items():
        total += gained
        series.append((day, total))
    if len(series) < 2:
        return empty(
            f"Claim on a second day and the line appears. So far: {data['xp']} XP."
        )
    w, h, left, right, top, bottom = 320, 120, 36, 10, 12, 22
    peak = series[-1][1] or 1

    def x(i: int) -> float:
        return left + i * (w - left - right) / (len(series) - 1)

    def y(v: int) -> float:
        return h - bottom - (v / peak) * (h - top - bottom)

    line = " ".join(
        f"{'L' if i else 'M'}{x(i):.1f} {y(v):.1f}" for i, (_, v) in enumerate(series)
    )
    dots = "".join(
        f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3" fill="var(--orange)">'
        f"<title>{_short_day(d)}: {v} XP</title></circle>"
        for i, (d, v) in enumerate(series)
    )
    return _svg(
        w,
        h,
        f"Total XP over time, {peak} XP after {len(series)} days",
        f'<line x1="{left}" y1="{y(peak):.1f}" x2="{w - right}" y2="{y(peak):.1f}"'
        ' class="grid"/>'
        f'<line x1="{left}" y1="{h - bottom}" x2="{w - right}" y2="{h - bottom}"'
        ' class="axis"/>'
        f'<text x="{left - 6}" y="{y(peak) + 4:.1f}" text-anchor="end" class="at">'
        f"{peak}</text>"
        f'<text x="{left - 6}" y="{h - bottom + 4}" text-anchor="end" class="at">'
        "0</text>"
        f'<path d="{line}" fill="none" stroke="var(--orange)" stroke-width="2"'
        f' stroke-linejoin="round"/>{dots}'
        f'<text x="{left}" y="{h - 6}" class="at">{_short_day(series[0][0])}</text>'
        f'<text x="{w - right}" y="{h - 6}" text-anchor="end" class="at">'
        f"{_short_day(series[-1][0])}</text>",
    )


def heatmap(data: dict[str, Any]) -> str:
    """Day by hour, one hue, light to dark by count."""
    heat = data["heat"]
    if not heat:
        return empty("Nothing in the last seven days. Run a check and it lands here.")
    peak = max(heat.values())
    w, left, cell_h, gap = 320, 34, 13, 2
    cell_w = (w - left - 4) / 24
    rows = data["days"]
    h = len(rows) * (cell_h + gap) + 18
    out = []
    for row, day in enumerate(rows):
        label = dt.date.fromisoformat(day).strftime("%a")
        out.append(
            f'<text x="{left - 6}" y="{row * (cell_h + gap) + cell_h - 3}"'
            f' text-anchor="end" class="at">{label}</text>'
        )
        for hour in range(24):
            n = heat.get(f"{day}:{hour}", 0)
            opacity = f"{0.2 + 0.8 * n / peak:.2f}" if n else "0.06"
            title = (
                f"<title>{_short_day(day)} {hour:02d}:00, {n} events</title>"
                if n
                else ""
            )
            out.append(
                f'<rect x="{left + hour * cell_w:.2f}" y="{row * (cell_h + gap)}"'
                f' width="{cell_w - gap:.2f}" height="{cell_h}" rx="3"'
                f' fill="var(--green-bright)" fill-opacity="{opacity}">{title}</rect>'
            )
    for hour in (0, 6, 12, 18):
        out.append(
            f'<text x="{left + hour * cell_w:.2f}"'
            f' y="{len(rows) * (cell_h + gap) + 12}" class="at">{hour:02d}</text>'
        )
    legend = (
        '<p class="small muted legend"><span class="sw" style="opacity:.2"></span>'
        '<span class="sw" style="opacity:.5"></span>'
        '<span class="sw" style="opacity:1"></span>'
        " quiet to busy, last seven days</p>"
    )
    return _svg(w, h, f"Activity by day and hour, busiest hour {peak} events",
                "".join(out)) + legend  # fmt: skip


def score_bars(data: dict[str, Any]) -> str:
    """Best run per player: the only chart on the page made of outside data."""
    players = data["scores"]["players"][:8]
    if not players:
        return empty("No runs yet. Workstream 3 writes workspace/data/scores.csv.")
    w, row_h, left, right = 320, 22, 86, 46
    peak = max(p["best"] for p in players) or 1
    out = []
    for i, p in enumerate(players):
        y = i * row_h
        length = max(3, (w - left - right) * p["best"] / peak)
        name = _esc(p["player"])[:12]
        out.append(
            f'<text x="0" y="{y + 14}" class="at">{name}</text>'
            f'<rect x="{left}" y="{y + 3}" width="{length:.1f}" height="12" rx="4"'
            f' fill="var(--blue)"><title>{name}: best {p["best"]},'
            f" {p['runs']} runs</title></rect>"
            f'<text x="{w}" y="{y + 14}" text-anchor="end" class="at v">'
            f"{p['best']}</text>"
        )
    return _svg(w, len(players) * row_h, "Best run per player", "".join(out))


def feed(data: dict[str, Any]) -> str:
    events = list(reversed(data["events"]))[:12]
    if not events:
        return empty("The feed fills as you claim stops and run checks.")
    rows = []
    for e in events:
        hue = KIND_HUE.get(e["kind"], "var(--muted)")
        label = KIND_LABEL.get(e["kind"], e["kind"])
        when = e["ts"].replace("T", " ")
        rows.append(
            f'<li><i style="background:{hue}"></i>'
            f"<span>{_esc(label)} <b>{_esc(e['id'])}</b></span>"
            f'<span class="when">{_esc(when)}</span></li>'
        )
    return '<ul class="feed">' + "".join(rows) + "</ul>"


# ---- the page ------------------------------------------------------------------

STYLE = """
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font-body);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
main{max-width:640px;margin:0 auto;padding:var(--space-6) var(--space-4) var(--space-8)}
h1{font-family:var(--font-display);font-size:clamp(28px,7vw,40px);letter-spacing:-.02em;
  margin:0 0 var(--space-2)}
h2{font-family:var(--font-display);font-size:12px;font-weight:600;text-transform:uppercase;
  letter-spacing:.14em;color:var(--muted);margin:0 0 var(--space-3)}
p{margin:0 0 var(--space-3)}
.small{font-size:13px}.muted{color:var(--muted)}
.head{font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin-bottom:var(--space-2)}
.head b{color:var(--yellow);font-weight:600}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:var(--space-2);margin:var(--space-4) 0}
.tile{background:var(--surface-2);border:1px solid var(--hairline);
  border-radius:var(--radius-m);padding:var(--space-3) var(--space-3) var(--space-2);
  display:flex;flex-direction:column;gap:2px;min-width:0}
.tl{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:var(--muted)}
.tv{font-family:var(--font-display);font-size:26px;line-height:1.1;letter-spacing:-.02em;
  font-variant-numeric:tabular-nums}
.tv .of{font-size:14px;color:var(--muted);font-weight:600}
.tc{font-size:11px;color:var(--muted);line-height:1.35}
.card{background:var(--surface-2);border:1px solid var(--hairline);border-radius:18px;
  padding:var(--space-4) var(--space-4) var(--space-3);margin:var(--space-3) 0}
.ch{display:block;width:100%;height:auto;margin-top:var(--space-1)}
.tile .ch{margin-top:var(--space-2)}
.rings{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));
  gap:var(--space-3)}
.ring{display:flex;flex-direction:column;align-items:center;gap:2px;text-align:center}
.ring .ch{width:64px}
.rl{font-size:11px;line-height:1.2}
.rn{font-size:10px;font-weight:700;letter-spacing:.1em;color:var(--muted);
  font-variant-numeric:tabular-nums}
text{fill:var(--muted);font-family:var(--font-mono);font-size:9px;
  font-variant-numeric:tabular-nums}
text.rt{fill:var(--text);font-family:var(--font-display);font-size:18px;font-weight:700}
text.v{fill:var(--text)}
.grid{stroke:var(--hairline)}.axis{stroke:var(--hairline-2)}
.legend{display:flex;align-items:center;gap:6px;margin:var(--space-2) 0 0;
  flex-wrap:wrap;font-size:13px;color:var(--muted)}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;
  background:var(--green-bright)}
.feed{list-style:none;margin:0;padding:0}
.feed li{display:flex;align-items:center;gap:var(--space-2);padding:7px 0;
  border-top:1px solid var(--hairline);font-size:13px}
.feed li:first-child{border-top:0}
.feed i{width:7px;height:7px;border-radius:50%;flex:none}
.feed li span:first-of-type{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap}
.feed .when{font-family:var(--font-mono);font-size:11px;color:var(--muted);
  white-space:nowrap;font-variant-numeric:tabular-nums}
.badges{display:flex;flex-wrap:wrap;gap:6px}
.badge{font-size:12px;background:rgba(0,168,107,.14);color:var(--green-bright);
  border-radius:var(--radius-pill);padding:3px 10px}
.foot{font-family:var(--font-mono);font-size:11px;color:var(--muted);
  margin-top:var(--space-6)}
.dash-empty{margin:0}
"""


def render(data: dict[str, Any]) -> str:
    """The whole report: one file, no fetch, no script."""
    scores = data["scores"]
    per_day = [float(n) for n in data["per_day"]]
    xp_series = [float(data["xp_day"].get(day, 0)) for day in data["days"]]
    tiles = "".join(
        [
            tile(
                "Stops delivered",
                f'{data["stops"]}<span class="of">/{data["stops_total"]}</span>',
                f"{round(data['stops'] / data['stops_total'] * 100)} percent"
                " of the campaign",
                spark(per_day, "var(--green-bright)"),
            ),
            tile(
                "XP earned",
                str(data["xp"]),
                f"level {data['level']}, {data['age']} age",
                spark(xp_series, "var(--orange)"),
            ),
            tile(
                "Day streak",
                str(data["streak"]),
                "days in a row" if data["streak"] else "nothing today yet",
                spark(per_day, "var(--yellow)"),
            ),
            tile(
                "Checks run",
                str(data["checks"]),
                f"{data['checks_green']} green",
            ),
            tile(
                "Mentors",
                f'{data["mentors"]}<span class="of">/{data["mentors_total"]}</span>',
                "exercise done and verified",
            ),
            tile(
                "Artifacts",
                f'{data["artifacts"]}<span class="of">'
                f"/{data['artifacts_total']}</span>",
                f"{data['artifacts_built']} built for real",
            ),
            tile("Vault notes", str(data["notes"]), "markdown files in vault/"),
            tile(
                "Runs logged",
                str(scores["runs"]),
                (
                    f"best {scores['best']} by {scores['best_by']}"
                    if scores["runs"]
                    else "workstream 3 writes them"
                ),
            ),
        ]
    )
    rings = "".join(
        ring(data["island_names"][w], n, 8) for w, n in data["per_island"].items()
    )
    badges = (
        '<div class="card"><h2>Badges</h2><div class="badges">'
        + "".join(f'<span class="badge">{_esc(b)}</span>' for b in data["badges"])
        + "</div></div>"
        if data["badges"]
        else ""
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vibe Code Camp: {_esc(data["name"])}</title>
<style>
{css_tokens()}
{STYLE}</style></head>
<body><main>
<p class="head"><b>vibe</b> dashboard · {_esc(data["generated_at"])}</p>
<h1>{_esc(data["name"])}</h1>
<p class="small muted">Built from .vibe/state.json, the vault and the scores in
this camp. Every number is derived; nothing here is a second source of truth.</p>
<div class="tiles">{tiles}</div>
<div class="card"><h2>Progress by island</h2><div class="rings">{rings}</div></div>
<div class="card"><h2>XP over time</h2>{xp_line(data)}
<p class="legend">The XP your claims carry, day by day. Mentors and artifacts add
theirs to the total above.</p></div>
<div class="card"><h2>Activity by day and hour</h2>{heatmap(data)}</div>
<div class="card"><h2>Best run per player</h2>{score_bars(data)}</div>
{badges}
<div class="card"><h2>Recent events</h2>{feed(data)}</div>
<p class="foot">vibe dashboard · regenerate with: uv run vibe dashboard</p>
</main></body></html>
"""


def write(data: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(data), encoding="utf-8")
    return path


def as_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2)
