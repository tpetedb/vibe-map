#!/usr/bin/env python3
"""vibe CLI: the terminal companion to the game.

    uv run vibe status            where you are, XP, level, badges
    uv run vibe check [n]         verify a workstream, award the XP
    uv run vibe done n "note"     claim it (checks first; --force to skip)
    uv run vibe vault build       rebuild the Obsidian vault from state
    uv run vibe export / import   the progress code the game speaks
    uv run vibe start             the onboarding screen

`uv run vibe status` keeps working for the syllabus.
"""

from __future__ import annotations

import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

if __package__ in (None, ""):  # run as a script: put the repo root on the path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from vibemap import __version__, campaign, pet, project, quests
from vibemap import chat as chat_bridge
from vibemap.artifact_checks import (
    ARTIFACT_NOTE,
    ARTIFACT_SECTION,
    ARTIFACT_WORDS,
    ARTIFACT_XP_SHARE,
    artifact_dir,
    artifact_ids,
    artifact_quest,
    get_artifact,
)
from vibemap.config import CONFIG_PATH, DIFFICULTIES, Config, deprecation_note
from vibemap.interests import (
    label as shelf_label,
)
from vibemap.interests import (
    parse as parse_interests,
)
from vibemap.interests import (
    shelves,
    suggestions,
)
from vibemap.palette import RICH_THEME
from vibemap.personas import PERSONAS, get_persona
from vibemap.providers import PROVIDERS, ProviderMissing, ask
from vibemap.quests import (
    BADGES,
    MENTOR_XP_SHARE,
    fork_quest,
    level_for,
    mentor_quest,
    new_badges,
    quest_for,
    run_quest,
    xp_for,
)
from vibemap.state import (
    IMPORTED_NOTE,
    PLACEHOLDER,
    CheckRecord,
    LogEntry,
    State,
)
from vibemap.themes import THEMES, load_theme
from vibemap.toolbelt import TOOLS, get_tool, install
from vibemap.vault import Vault, safe_title

ROOT = project.root()
console = Console(theme=RICH_THEME, highlight=False)
WORLDS = list(campaign.WORLD_NAMES)
# The rate the vendored sprites were drawn at; the ASCII art idles at half a
# second a frame instead.
PET_FPS = 8


class Ctx:
    """Config, state and vault, loaded once per command."""

    def __init__(self) -> None:
        self.cfg = Config.load()
        self.state = State.load()
        # camp.toml is where a learner types their name, so the state follows
        # it while the state still holds the placeholder.
        if self.state.name == PLACEHOLDER and self.cfg.learner.name != PLACEHOLDER:
            self.state.name = self.cfg.learner.name
        self.vault = Vault(self.cfg, self.state)

    @property
    def persona(self):
        return get_persona(self.cfg.learner.persona)

    def save(self) -> None:
        self.state.save()


pass_ctx = click.make_pass_decorator(Ctx, ensure=True)


def _fail(msg: str) -> None:
    console.print(f"[err]{msg}[/]")
    sys.exit(1)


def _exit_code(ok: bool) -> None:
    """End the command: 0 when every check passed, 1 when one did not.

    A failed check is an undone task, not a broken tool, so nothing else is
    printed; the table above already says which row failed.
    """
    sys.exit(0 if ok else 1)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="vibe")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """The terminal companion to Vibe Code Camp."""
    try:
        ctx.obj = Ctx()
    except ValueError as e:
        _fail(str(e))
    note = deprecation_note()
    if note:
        console.print(f"[warn]deprecated:[/] {note}")


# ---- status -------------------------------------------------------------------


def _stop_cell(st: State, world: str, n: int) -> str:
    """One square of the status grid: done, claimed but not checked, or to do."""
    if not st.is_done(world, n):
        return "[todo].[/]"
    return "[done]x[/]" if st.is_verified(world, n) else "[warn]i[/]"


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="machine-readable")
@pass_ctx
def status(ctx: Ctx, as_json: bool) -> None:
    """Where you are in the campaign, with XP, level and badges."""
    st, cfg = ctx.state, ctx.cfg
    age, label, nxt = level_for(st.xp)
    if as_json:
        click.echo(
            json.dumps(
                {
                    "name": st.name, "xp": st.xp, "level": label, "age": age,
                    "next_level_at": nxt, "done": st.done_w, "badges": st.badges,
                    "mentors": st.mentors, "artifacts": st.artifacts,
                    "artifacts_built": st.artifacts_built,
                    "persona": cfg.learner.persona,
                    "difficulty": cfg.learner.difficulty,
                    "mode": cfg.learner.mode, "provider": cfg.learner.provider,
                    "interests": cfg.learner.interests,
                    "items": st.items, "ach": st.ach, "wear": st.wear,
                },
                indent=2,
            )
        )  # fmt: skip
        return
    if not project.is_camp():
        console.print(
            f"[warn]No camp in {ROOT}[/] (no config/camp.toml). "
            "Start one with [accent]vibe new[/], or cd into a camp."
        )
    diff = DIFFICULTIES[cfg.learner.difficulty]
    head = (
        f"[title]{st.name}[/] · {ctx.persona.label} · {diff.label} · "
        f"provider [path]{cfg.learner.provider}[/] · "
        f"theme [path]{cfg.theme.preset}[/]\n"
        f"Level [ok]{label}[/] ({age} age) · [xp]{st.xp} XP[/]"
        + (f" · {nxt - st.xp} to the next level" if nxt else " · top level")
        + f" · {st.total_done()}/32 stops"
        + f" · {len(st.artifacts)}/{len(campaign.artifacts())} artifacts"
        + f" ({len(st.artifacts_built)} built for real)"
        # "Met" is the verified encounter, not a hello on the island.
        + f"\n{len(st.mentors)}/{len(campaign.mentors())} mentors met "
        + "(their exercise done and checked)"
        # The avatar, as text: what was picked up on the islands and what the
        # walker is wearing while doing it.
        + f"\n{len(st.items)}/{len(campaign.collectibles())} things collected"
        + f" · {len(st.ach)} achievements"
        + (f" · wearing {', '.join(st.wear)}" if st.wear else " · wearing nothing yet")
        + "\nLearning: "
        + (
            ", ".join(shelf_label(c) for c in cfg.learner.interests)
            if cfg.learner.interests
            else "everything"
        )
        + " (vibe interests)"
    )
    panel = Panel(head, title="Vibe Code Camp", border_style="accent")
    if cfg.pet.enabled:
        grid = Table.grid(padding=(0, 2))
        grid.add_row(panel, pet.render(_pet(ctx), stats=False, style=cfg.pet.style))
        console.print(grid)
    else:
        console.print(panel)
    t = Table(header_style="path", box=None, padding=(0, 1))
    t.add_column("evening")
    for i in range(1, 9):
        t.add_column(str(i), justify="center")
    t.add_column("done", justify="right")
    for w, ev in campaign.evenings().items():
        cells = [_stop_cell(st, w, i) for i in range(1, 9)]
        t.add_row(f"{ev.short} · {ev.island}", *cells, f"{len(st.done_w.get(w, []))}/8")
    console.print(t)
    if st.imported_stops():
        console.print(
            "[muted]i = claimed in the game, not verified here; "
            "vibe check pays the other half.[/]"
        )
    if st.badges:
        console.print(
            "Badges: "
            + ", ".join(f"[ok]{BADGES.get(b, b).split(':')[0]}[/]" for b in st.badges)
        )
    _print_next_topic(ctx)
    nxt_ws = _next_workstream(st, "campus")
    if nxt_ws:
        console.print(
            f"Next: [path]{nxt_ws.hour} {nxt_ws.name}[/]. "
            f"Run [accent]vibe check {nxt_ws.n}[/] when you think it is done."
        )
        return
    for world in WORLDS:
        ws = _next_workstream(st, world)
        if ws:
            console.print(
                f"[ok]{campaign.WORLD_NAMES['campus']} complete.[/] Next island: "
                f"[accent]vibe check --world {world} {ws.n}[/] "
                f"({ws.hour} {ws.name})."
            )
            return
    console.print(
        "[ok]All 32 stops done. The campaign is finished.[/] "
        "Write the last note, then keep the vault growing: vibe vault feature --all."
    )


def _next_workstream(st: State, world: str):
    for ws in campaign.evenings()[world].workstreams:
        if not st.is_done(world, ws.n):
            return ws
    return None


# ---- check and done -----------------------------------------------------------


def _print_results(results, quest, cfg: Config) -> bool:
    where = f"{quest.world} {quest.n}" if quest.n else quest.world
    t = Table(title=f"{quest.title} ({where})", title_style="title", box=None)
    t.add_column("check")
    t.add_column("result")
    t.add_column("detail", style="muted")
    hints = DIFFICULTIES[cfg.learner.difficulty].hints
    for r in results:
        mark = "[ok]pass[/]" if r.ok else "[err]fail[/]"
        t.add_row(r.name, mark, r.detail)
    console.print(t)
    failed = [r for r in results if not r.ok]
    if failed and hints != "none":
        for r in failed:
            console.print(f"  [warn]hint[/] {escape(r.hint)}")
    return not failed


def _claim(ctx: Ctx, world: str, n: int, note: str, results, *, forced: bool) -> None:
    ws = campaign.evenings()[world].workstreams[n - 1]
    full = xp_for(ctx.cfg.learner.difficulty)
    xp = full // 2 if forced else full
    fresh = ctx.state.mark_done(world, n, note=note, xp=xp)
    # A stop already claimed at half price (imported from the game, or forced)
    # is topped up to full the first time its checks actually pass.
    topped = 0
    if not fresh and not forced and all(r.ok for r in results):
        topped = ctx.state.owed(world, n, full)
        if topped:
            ctx.state.log.append(LogEntry(world=world, n=n, note=note, xp=topped))
            ctx.state.xp += topped
    ctx.state.checks[f"{world}:{n}"] = CheckRecord(
        ok=all(r.ok for r in results),
        passed=[r.name for r in results if r.ok],
        failed=[r.name for r in results if not r.ok],
    )
    badges = new_badges(ctx.state, ctx.cfg)
    ctx.save()
    bullets = [
        f"done at {ctx.state.log[-1].at[11:16]}" if fresh else "checked again",
        note or "built it",
        "checks: " + (", ".join(r.name for r in results if r.ok) or "none"),
        f"links: [[Tonight]], [[Map]], [[{campaign.evenings()[world].short}]]",
    ]
    ctx.vault.upsert_dated(
        ws.name,
        summary=(
            f"{ws.hour}, [[{campaign.evenings()[world].short}]]. Outcome: {ws.outcome}."
        ),
        bullets=bullets,
        tags=["workstream"],
        sources=[u for _, u in ws.sources],
    )
    ctx.vault.build(ctx.persona)
    if fresh:
        console.print(
            f"[ok]{ws.name} done[/] [xp]+{xp} XP[/]"
            + (" (forced, half XP)" if forced else "")
        )
    elif topped:
        console.print(
            f"[ok]{ws.name} verified[/] [xp]+{topped} XP[/] "
            "(it was claimed without a check, at half)"
        )
    else:
        console.print(f"[muted]{ws.name} was already done; note added.[/]")
    for b in badges:
        console.print(f"[title]Badge:[/] {BADGES[b]}")
    age, label, _ = level_for(ctx.state.xp)
    console.print(
        f"Level {label}, {ctx.state.xp} XP. "
        f"Note: vault/{ctx.cfg.vault.folder}/{safe_title(ws.name)}.md"
    )
    _pet_cheer(ctx)


@cli.command()
@click.argument("n", type=int, required=False)
@click.option(
    "--world",
    "-w",
    default=None,
    type=click.Choice(WORLDS),
    help="island (default: campus)",
)
@click.option(
    "--all", "all_", is_flag=True, help="check every workstream of the island"
)
@click.option("--claim/--no-claim", default=True, help="mark done when the checks pass")
@click.option(
    "--mentor",
    "mentor_id",
    default=None,
    help="check a mentor encounter instead of a workstream (an id, or all)",
)
@click.option(
    "--artifact",
    "artifact_id",
    default=None,
    help="check an artifact you built for real (an id, or all)",
)
@click.option(
    "--fork",
    "fork_",
    is_flag=False,
    flag_value="all",
    default=None,
    help="check the fork challenges: all, or one of "
    + ", ".join(quests.FORK_CHALLENGES),
)
@pass_ctx
def check(
    ctx: Ctx,
    n: int | None,
    world: str | None,
    all_: bool,
    claim: bool,
    mentor_id: str | None,
    artifact_id: str | None,
    fork_: str | None,
) -> None:
    """Verify the definition of done for a workstream and award the XP.

    Exit code 0 when every check passed, 1 when any failed, so the command can
    be a step in a pipeline. --no-claim changes what is recorded, never the code.
    """
    if mentor_id:
        _exit_code(_check_mentors(ctx, mentor_id, claim=claim))
    if artifact_id:
        _exit_code(_check_artifacts(ctx, artifact_id, claim=claim))
    if fork_:
        try:
            quest = fork_quest(ctx.cfg, fork_)
        except ValueError as e:
            _fail(str(e))
        ok = _print_results(run_quest(quest, ctx.cfg), quest, ctx.cfg)
        if ok:
            console.print("[ok]your fork builds and is yours[/]")
        else:
            console.print("[warn]not yet.[/] Fix the failed checks and run it again.")
        _exit_code(ok)
    world = world or "campus"
    if all_:
        targets = list(range(1, 9))
    elif n is None:
        nxt = _next_workstream(ctx.state, world)
        if nxt is None:
            console.print("[ok]Everything on this island is done.[/]")
            return
        targets = [nxt.n]
    else:
        if not 1 <= n <= 8:
            _fail("workstream is 1 to 8")
        targets = [n]
    every = True
    for k in targets:
        quest = quest_for(world, k, ctx.cfg)
        results = run_quest(quest, ctx.cfg)
        ok = _print_results(results, quest, ctx.cfg)
        every = every and ok
        # A stop claimed in the game or forced carries half the XP; passing the
        # checks later is what buys the other half (ADR 0004).
        owed = ctx.state.owed(world, k, xp_for(ctx.cfg.learner.difficulty))
        if ok and claim and (not ctx.state.is_done(world, k) or owed):
            _claim(ctx, world, k, "verified by vibe check", results, forced=False)
        elif ok:
            console.print("[ok]all checks pass[/]")
        else:
            console.print(
                "[warn]not yet.[/] Fix the failed checks, "
                "or `vibe done` with --force for half XP."
            )
    _exit_code(every)


@cli.command()
@click.argument("n", type=int)
@click.argument("note", required=False, default="")
@click.option("--world", "-w", default="campus", type=click.Choice(WORLDS))
@click.option("--force", is_flag=True, help="claim even if checks fail (half XP)")
@pass_ctx
def done(ctx: Ctx, n: int, note: str, world: str, force: bool) -> None:
    """Mark workstream N done, after running its checks."""
    if not 1 <= n <= 8:
        _fail("workstream is 1 to 8")
    if force and ctx.state.is_done(world, n):
        ws = campaign.evenings()[world].workstreams[n - 1]
        console.print(
            f"[muted]{ws.name} is already done; nothing to force. "
            f"Take it back with vibe undo {n}"
            + (f" --world {world}" if world != "campus" else "")
            + ".[/]"
        )
        return
    quest = quest_for(world, n, ctx.cfg)
    results = run_quest(quest, ctx.cfg)
    ok = _print_results(results, quest, ctx.cfg)
    if not ok and not force:
        _fail("checks failed; fix them or add --force (half XP)")
    _claim(ctx, world, n, note, results, forced=not ok)


@cli.command()
@click.argument("n", type=int)
@click.option("--world", "-w", default="campus", type=click.Choice(WORLDS))
@pass_ctx
def undo(ctx: Ctx, n: int, world: str) -> None:
    """Un-claim workstream N: the XP goes back and the note loses the entry."""
    if not 1 <= n <= 8:
        _fail("workstream is 1 to 8")
    if not ctx.state.is_done(world, n):
        _fail(f"{world} {n} is not done; nothing to undo")
    ws = campaign.evenings()[world].workstreams[n - 1]
    xp = ctx.state.undo(world, n)
    ctx.save()
    ctx.vault.drop_claim(ws.name)
    ctx.vault.build(ctx.persona)
    console.print(
        f"[ok]{ws.name} is open again[/] [xp]-{xp} XP[/]. "
        f"Your own words in vault/{ctx.cfg.vault.folder}/{safe_title(ws.name)}.md "
        "stay."
    )


# ---- vault --------------------------------------------------------------------


@cli.group()
def vault() -> None:
    """Build, lint and log the Obsidian vault."""


@vault.command("build")
@pass_ctx
def vault_build(ctx: Ctx) -> None:
    """Rebuild every generated note from the state."""
    ctx.vault.build(ctx.persona)
    console.print(
        f"[ok]vault built[/]: {len(ctx.vault.notes())} notes in "
        f"{ctx.vault.dir.relative_to(ROOT)}"
    )


@vault.command("mode")
@click.argument("mode", required=False, type=click.Choice(["full", "grow"]))
@pass_ctx
def vault_mode(ctx: Ctx, mode: str | None) -> None:
    """full: every note from day one. grow: the vault fills up as you play."""
    from vibemap import grow

    if mode is None:
        console.print(f"vault mode = [path]{ctx.cfg.vault.mode}[/]")
        return
    data = ctx.cfg.model_dump()
    data["vault"]["mode"] = mode
    cfg = Config.model_validate(data)
    cfg.save(CONFIG_PATH)
    ctx.cfg = cfg
    ctx.vault = Vault(cfg, ctx.state)
    if mode == "full":
        moved = grow.restore_all(ctx.vault)
        ctx.vault.build(ctx.persona)
        console.print(f"[ok]full[/]: {moved} notes back from the library.")
    else:
        ctx.vault.build(ctx.persona)
        here, waiting = grow.sync(ctx.vault)
        console.print(
            f"[ok]grow[/]: {here} notes in the camp, {waiting} waiting in "
            f"vault/_library. {grow.next_hint(ctx.vault)}"
        )


@vault.command("unlock")
@click.argument("title")
@pass_ctx
def vault_unlock(ctx: Ctx, title: str) -> None:
    """Unlock one note by hand in grow mode."""
    from vibemap import grow

    p = grow.unlock(ctx.vault, title)
    if p is None:
        _fail(f"no note called {title!r} in the camp or the library")
    ctx.save()
    console.print(f"[ok]unlocked[/] {p.relative_to(ROOT)}")


@vault.command("lint")
@pass_ctx
def vault_lint(ctx: Ctx) -> None:
    """Orphans, dead links and notes without frontmatter."""
    r = ctx.vault.lint()
    console.print(f"{r.notes} notes, {r.link_count()} wikilinks")
    for o in r.orphans:
        console.print(f"  [warn]orphan[/] {o}")
    for src, dst in r.dead_links:
        console.print(f"  [err]dead link[/] {src} -> {escape('[[' + dst + ']]')}")
    for f in r.no_frontmatter:
        console.print(f"  [warn]no frontmatter[/] {f}")
    if r.ok:
        console.print("[ok]vault OK[/]")
    else:
        sys.exit(1)


@vault.command("log")
@click.argument("line")
@pass_ctx
def vault_log(ctx: Ctx, line: str) -> None:
    """Append one line to Tonight's Build log."""
    ctx.vault.add_build_log(line)
    console.print("[ok]logged[/]")


@vault.command("feature")
@click.argument("feature_id", required=False)
@click.option("--all", "everything", is_flag=True, help="bootstrap every feature")
@pass_ctx
def vault_feature(ctx: Ctx, feature_id: str | None, everything: bool) -> None:
    """List Obsidian features, or bootstrap one (or all) into the vault.

    Each feature gets a note with the facts, the syntax and a five-minute
    try from the official help; canvases, bases, templates, slides and
    snippets also get a working example file.
    """
    from vibemap import obsidian

    if feature_id is None and not everything:
        t = Table(box=None, header_style="path")
        t.add_column("id")
        t.add_column("feature")
        t.add_column("kind", style="muted")
        for f in obsidian.features().values():
            t.add_row(f.id, f.name, f.kind)
        console.print(t)
        console.print("[muted]docs/OBSIDIAN.md has the table with the tries.[/]")
        return
    ids = list(obsidian.features()) if everything else [feature_id]
    try:
        titles = obsidian.bootstrap(ctx.vault.dir, ids, write=ctx.vault.write)
    except ValueError as e:
        _fail(str(e))
    ctx.vault.add_build_log(
        f"[[Obsidian features]]: {len(titles)} feature note(s) bootstrapped"
    )
    console.print(
        f"[ok]{len(titles)} feature note(s)[/] under vault/{ctx.cfg.vault.folder}/, "
        "hub [[Obsidian features]]. Open the vault and follow the tries."
    )


@vault.command("method")
@click.argument("method_id", required=False)
@pass_ctx
def vault_method(ctx: Ctx, method_id: str | None) -> None:
    """List note-taking methods, or bootstrap one into the vault."""
    from vibemap.methods import METHODS, get_method

    if method_id is None:
        t = Table(box=None, header_style="path")
        t.add_column("id")
        t.add_column("method")
        t.add_column("best for", style="muted")
        for m in METHODS.values():
            t.add_row(m.id, m.name, m.when)
        console.print(t)
        console.print(
            "[muted]docs/NOTE-METHODS.md compares them; methods can coexist.[/]"
        )
        return
    try:
        m = get_method(method_id)
    except ValueError as e:
        _fail(str(e))
    base = ctx.vault.dir / "Methods" / m.name
    for folder in m.folders:
        (base / folder).mkdir(parents=True, exist_ok=True)
        (base / folder / ".gitkeep").touch()
    tdir = ctx.vault.dir / "_templates" / m.id
    tdir.mkdir(parents=True, exist_ok=True)
    for tpl in m.templates:
        (tdir / tpl.filename).write_text(tpl.body, encoding="utf-8")
    title = f"Method - {m.name}"
    ctx.vault.write(title, m.hub, tags=["tech"])
    ctx.vault.add_build_log(f"[[{title}]] bootstrapped under Methods/{m.name}/")
    console.print(
        f"[ok]{m.name}[/]: {len(m.folders)} folders under vault/{ctx.cfg.vault.folder}/"
        f"Methods/{m.name}, {len(m.templates)} templates in _templates/{m.id}, "
        f"hub note {title}"
    )


@cli.command()
@pass_ctx
def init(ctx: Ctx) -> None:
    """Create the state file and the vault (safe to re-run)."""
    ctx.save()
    ctx.vault.build(ctx.persona)
    console.print(f"[ok]vault ready[/] at {ctx.vault.dir.relative_to(ROOT)}")


@cli.command("map")
@pass_ctx
def map_(ctx: Ctx) -> None:
    """Rebuild Map.md and print the Mermaid."""
    ctx.vault.build(ctx.persona)
    text = ctx.vault.path("Map").read_text(encoding="utf-8")
    console.print(text.split("```mermaid\n", 1)[1].split("```", 1)[0])
    console.print("[muted]written to vault/Camp/Map.md[/]")


# ---- sync with the game -------------------------------------------------------


@cli.command()
@pass_ctx
def export(ctx: Ctx) -> None:
    """Print the progress code to paste into the game."""
    click.echo(ctx.state.to_code())


@cli.command("import")
@click.argument("code")
@pass_ctx
def import_(ctx: Ctx, code: str) -> None:
    """Take a progress code from the game and update state and vault."""
    before = {(w, n) for w, lst in ctx.state.done_w.items() for n in lst}
    try:
        ctx.state.merge_code(code)
    except ValueError as e:
        _fail(str(e))
    # A claim in the game is self-report, so it earns half the XP a verified
    # check does (ADR 0004); `vibe check` can top it up later.
    half = xp_for(ctx.cfg.learner.difficulty) // 2
    fresh = sorted(
        {(w, n) for w, lst in ctx.state.done_w.items() for n in lst} - before
    )
    for w, n in fresh:
        ctx.state.log.append(LogEntry(world=w, n=n, note=IMPORTED_NOTE, xp=half))
    ctx.state.xp += half * len(fresh)
    new_badges(ctx.state, ctx.cfg)
    ctx.save()
    ctx.vault.build(ctx.persona)
    console.print(
        f"[ok]imported[/]: {len(fresh)} new stops, {ctx.state.total_done()}/32 "
        f"in total, {ctx.state.xp} XP"
    )
    waiting = ctx.state.imported_stops()
    if waiting:
        console.print(
            f"[warn]imported, not verified[/]: {len(waiting)} stop(s) at half XP. "
            "The game claims a stop, it never checks one. Run the check to earn "
            "the other half:"
        )
        for w, n in waiting:
            flag = "" if w == "campus" else f" -w {w}"
            console.print(f"  [accent]vibe check{flag} {n}[/]")


def _mentor_or_fail(mentor_id: str) -> dict:
    """The mentor with that id, or exit 1 with the list of the twelve."""
    try:
        return campaign.mentor(mentor_id)
    except ValueError as e:
        _fail(str(e))
        raise  # unreachable: _fail exits


def _check_mentors(ctx: Ctx, mentor_id: str, *, claim: bool) -> bool:
    """Run the encounter checks for one mentor, or for all twelve."""
    if mentor_id == "all":
        ids = [m["id"] for m in campaign.mentors()]
    else:
        ids = [_mentor_or_fail(mentor_id)["id"]]
    every = True
    for mid in ids:
        quest = mentor_quest(mid, ctx.cfg)
        results = run_quest(quest, ctx.cfg)
        ok = _print_results(results, quest, ctx.cfg)
        every = every and ok
        if ok and claim and mid not in ctx.state.mentors:
            _claim_mentor(ctx, mid, results)
        elif ok:
            console.print("[ok]all checks pass[/]")
        else:
            console.print(
                f"[warn]not yet.[/] The exercise lives in workspace/mentors/{mid}/."
            )
    return every


def _claim_mentor(ctx: Ctx, mentor_id: str, results) -> None:
    """Record a verified encounter: the badge on the island comes from this."""
    m = campaign.mentor(mentor_id)
    xp = xp_for(ctx.cfg.learner.difficulty) // MENTOR_XP_SHARE
    ctx.state.mentors.append(mentor_id)
    ctx.state.path.setdefault(mentor_id, "deep")
    ctx.state.xp += xp
    ctx.state.checks[f"mentor:{mentor_id}"] = CheckRecord(
        ok=True,
        passed=[r.name for r in results if r.ok],
        failed=[r.name for r in results if not r.ok],
    )
    badges = new_badges(ctx.state, ctx.cfg)
    ctx.save()
    ctx.vault.build(ctx.persona)
    console.print(f"[ok]{m['name']} done[/] [xp]+{xp} XP[/]")
    for b in badges:
        console.print(f"[title]Badge:[/] {BADGES[b]}")


def _check_artifacts(ctx: Ctx, artifact_id: str, *, claim: bool) -> bool:
    """Run the Do it for real checks for one artifact, or for all of them."""
    if artifact_id == "all":
        ids = artifact_ids()
    else:
        try:
            ids = [get_artifact(artifact_id)["id"]]
        except ValueError as e:
            _fail(str(e))
    every = True
    for aid in ids:
        quest = artifact_quest(aid, ctx.cfg)
        results = run_quest(quest, ctx.cfg)
        ok = _print_results(results, quest, ctx.cfg)
        every = every and ok
        if ok and claim and aid not in ctx.state.artifacts_built:
            _claim_artifact(ctx, aid, results)
        elif ok:
            console.print("[ok]all checks pass[/]")
        else:
            console.print(
                f"[warn]not yet.[/] The walkthrough: [accent]vibe artifact {aid}[/], "
                f"or the artifact sheet in the game; the work goes in "
                f"workspace/artifacts/{aid}/."
            )
    return every


def _claim_artifact(ctx: Ctx, artifact_id: str, results) -> None:
    """Record an artifact built for real; the progress code carries it back."""
    name = get_artifact(artifact_id)["name"]
    xp = xp_for(ctx.cfg.learner.difficulty) // ARTIFACT_XP_SHARE
    ctx.state.artifacts_built.append(artifact_id)
    if artifact_id not in ctx.state.artifacts:
        ctx.state.artifacts.append(artifact_id)
    ctx.state.xp += xp
    ctx.state.checks[f"artifact:{artifact_id}"] = CheckRecord(
        ok=True,
        passed=[r.name for r in results if r.ok],
        failed=[r.name for r in results if not r.ok],
    )
    badges = new_badges(ctx.state, ctx.cfg)
    ctx.save()
    ctx.vault.build(ctx.persona)
    console.print(f"[ok]{name} built for real[/] [xp]+{xp} XP[/]")
    for b in badges:
        console.print(f"[title]Badge:[/] {BADGES[b]}")


# A scaffolded folder is a starting point, never a pass: the stub says what
# is missing and `vibe check --mentor <id>` keeps failing until the learner
# writes the real thing.
STUB_LINES = (
    "TODO: {title}",
    "Write this yourself; the check fails until you do.",
)


def _stub_text(mentor_id: str, ex: dict) -> str:
    """The placeholder for the file the exercise names, commented for Python."""
    mark = "# " if ex["file"].endswith(".py") else ""
    lines = [mark + line.format(title=ex["title"]) for line in STUB_LINES]
    lines.append(f"{mark}Run: vibe check --mentor {mentor_id}")
    return "\n".join(lines) + "\n"


def _note_stub() -> str:
    return (
        f"{quests.MENTOR_SECTION}\n\n"
        "Replace this line with your own words, at least "
        f"{quests.MENTOR_WORDS} of them.\n"
    )


def _scaffold_mentor(m: dict) -> tuple[list[str], list[str]]:
    """Create the exercise folder; returns (written, kept) file names.

    A file that is already there is the learner's work, so it is left alone.
    """
    ex = m["encounter"]["exercise"]
    here = quests.mentor_dir(m["id"])
    here.mkdir(parents=True, exist_ok=True)
    written, kept = [], []
    for name, body in (
        (ex["file"], _stub_text(m["id"], ex)),
        (quests.MENTOR_NOTE, _note_stub()),
    ):
        target = here / name
        if target.exists():
            kept.append(name)
            continue
        target.write_text(body, encoding="utf-8")
        written.append(name)
    return written, kept


def _show_encounter(ctx: Ctx, m: dict) -> None:
    """What this mentor asks of you, and the command that proves it."""
    ex = m["encounter"]["exercise"]
    met = "[ok]met[/]" if m["id"] in ctx.state.mentors else "[todo]not yet met[/]"
    console.print(
        f"[title]{m['name']}[/] · [path]{campaign.WORLD_NAMES[m['world']]}[/] · {met}"
    )
    console.print(f"[accent]{escape(ex['title'])}[/] · {ex['minutes']} minutes")
    for i, step in enumerate(ex["steps"], 1):
        console.print(f"  {i}. {escape(step)}")
    console.print(f"Done when: {escape(ex['done'])}")
    console.print(f"Check it: [accent]vibe check --mentor {m['id']}[/]")


def _list_mentors(ctx: Ctx) -> None:
    """The twelve, their island and whether the encounter is verified."""
    t = Table(header_style="path", box=None, padding=(0, 1))
    for col in ("id", "mentor", "island", "encounter"):
        t.add_column(col)
    for m in campaign.mentors():
        done = m["id"] in ctx.state.mentors
        t.add_row(
            m["id"],
            m["name"],
            campaign.WORLD_NAMES[m["world"]],
            "[done]verified[/]" if done else "[todo]not yet[/]",
        )
    console.print(t)
    console.print(
        "One mentor: [accent]vibe mentor <id>[/], "
        "and [accent]vibe mentor <id> --start[/] to set the folder up."
    )


@cli.command()
@click.argument("mentor_id", required=False)
@click.argument("choice", required=False, type=click.Choice(["deep", "skip"]))
@click.option(
    "--start", is_flag=True, help="scaffold workspace/mentors/<id>/ for the exercise"
)
@pass_ctx
def mentor(ctx: Ctx, mentor_id: str | None, choice: str | None, start: bool) -> None:
    """What a mentor asks of you, or record a choice (deep or skip)."""
    if not mentor_id:
        _list_mentors(ctx)
        return
    m = _mentor_or_fail(mentor_id)
    if choice:
        ctx.state.path[mentor_id] = choice
        ctx.save()
        ctx.vault.build(ctx.persona)
        console.print(f"[ok]{m['name']}[/]: {choice}")
        return
    if start:
        written, kept = _scaffold_mentor(m)
        where = m["encounter"]["exercise"]["dir"]
        if written:
            console.print(f"[ok]{where}/[/]: wrote {', '.join(written)}")
        for name in kept:
            console.print(f"[warn]kept your {where}/{name}[/], it was already there")
    _show_encounter(ctx, m)


# A scaffolded artifact folder is the same promise the mentor one makes: the
# stub names the task and the check keeps failing until the learner writes it.
ARTIFACT_COMMENT = {".py": "# ", ".yml": "# ", ".yaml": "# ", ".md": "", "": "# "}


def _artifact_stub(artifact_id: str, real: dict) -> tuple[str, str] | None:
    """(file name, body) for the one file the walkthrough names, if it names one.

    A task whose files are produced by its commands (uv init, git) gets no stub:
    a fake pyproject.toml would be in the way of the tool that writes it.
    """
    name = real["check"].get("file")
    if not name:
        return None
    title = real["title"]
    if name.endswith(".json"):
        body = json.dumps({"TODO": title, "see": real["doc"]["url"]}, indent=2) + "\n"
        return name, body
    mark = ARTIFACT_COMMENT.get(Path(name).suffix, "# ")
    lines = [f"{mark}TODO: {title}", f"{mark}{STUB_LINES[1]}"]
    lines.append(f"{mark}Run: vibe check --artifact {artifact_id}")
    return name, "\n".join(lines) + "\n"


def _artifact_note_stub() -> str:
    return (
        f"{ARTIFACT_SECTION}\n\n"
        "Replace this line with your own words, at least "
        f"{ARTIFACT_WORDS} of them.\n"
    )


def _scaffold_artifact(a: dict) -> tuple[list[str], list[str]]:
    """Create workspace/artifacts/<id>/; returns (written, kept) file names."""
    here = artifact_dir(a["id"])
    here.mkdir(parents=True, exist_ok=True)
    files = [(ARTIFACT_NOTE, _artifact_note_stub())]
    stub = _artifact_stub(a["id"], a["real"])
    if stub:
        files.insert(0, stub)
    written, kept = [], []
    for name, body in files:
        target = here / name
        if target.exists():
            kept.append(name)
            continue
        target.write_text(body, encoding="utf-8")
        written.append(name)
    return written, kept


def _show_artifact(ctx: Ctx, a: dict) -> None:
    """The walkthrough the artifact sheet shows in the game, in the terminal."""
    real = a["real"]
    built = a["id"] in ctx.state.artifacts_built
    state = "[ok]built for real[/]" if built else "[todo]not built yet[/]"
    console.print(
        f"[title]{a['name']}[/] · [path]{campaign.WORLD_NAMES[a['world']]}[/] · {state}"
    )
    console.print(f"[muted]{escape(a['what'])}[/]")
    console.print(f"[accent]{escape(real['title'])}[/] · {real['minutes']} minutes")
    console.print(f"Read first: {escape(real['doc']['title'])} {real['doc']['url']}")
    for i, step in enumerate(real["steps"], 1):
        console.print(f"  {i}. {escape(step)}")
    for cmd in real.get("commands", ()):
        console.print(f"  [muted]$ {escape(cmd)}[/]")
    console.print(f"Work in: [path]{real['dir']}/[/]")
    console.print(f"Done when: {escape(real['done'])}")
    console.print(f"Check it: [accent]vibe check --artifact {a['id']}[/]")


def _list_artifacts(ctx: Ctx) -> None:
    """Every artifact, its island and whether it was built for real."""
    t = Table(header_style="path", box=None, padding=(0, 1))
    for col in ("id", "artifact", "island", "task", "built"):
        t.add_column(col)
    for a in campaign.artifacts():
        built = a["id"] in ctx.state.artifacts_built
        t.add_row(
            a["id"],
            a["name"],
            campaign.WORLD_NAMES[a["world"]],
            a["real"]["title"],
            "[done]for real[/]" if built else "[todo]not yet[/]",
        )
    console.print(t)
    console.print(
        "One artifact: [accent]vibe artifact <id>[/], "
        "and [accent]vibe artifact <id> --start[/] to set the folder up."
    )


@cli.command()
@click.argument("artifact_id", required=False)
@click.option(
    "--start", is_flag=True, help="scaffold workspace/artifacts/<id>/ for the task"
)
@pass_ctx
def artifact(ctx: Ctx, artifact_id: str | None, start: bool) -> None:
    """The walkthrough for an artifact, the same one the game shows."""
    if not artifact_id:
        _list_artifacts(ctx)
        return
    try:
        a = get_artifact(artifact_id)
    except ValueError as e:
        _fail(str(e))
    if start:
        written, kept = _scaffold_artifact(a)
        where = a["real"]["dir"]
        if written:
            console.print(f"[ok]{where}/[/]: wrote {', '.join(written)}")
        for name in kept:
            console.print(f"[warn]kept your {where}/{name}[/], it was already there")
        if not a["real"]["check"].get("file"):
            console.print(
                f"[muted]{where}/ is ready; this task's files come from the "
                "commands below, so vibe writes none of them.[/]"
            )
    _show_artifact(ctx, a)


# ---- scores -------------------------------------------------------------------


@cli.command()
@click.option(
    "--sql", "sql_name", default=None, help="run a query from workspace/sql/ instead"
)
def scores(sql_name: str | None) -> None:
    """Summarise workspace/data/scores.csv, or run a workspace/sql/ query."""
    from vibemap.scores import (
        SCORES,
        frame_table,
        read_scores,
        run_sql,
        scores_table,
        summary,
    )

    if not SCORES.exists():
        _fail("no scores yet; workstream 3 creates workspace/data/scores.csv")
    if sql_name:
        try:
            console.print(frame_table(run_sql(sql_name), f"workspace/sql/{sql_name}"))
        except FileNotFoundError as e:
            _fail(str(e))
        return
    console.print(scores_table(summary(read_scores())))


# ---- dashboard ------------------------------------------------------------------


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="print the numbers instead")
@click.option("--open/--no-open", "open_it", default=True, help="open the report")
@click.option(
    "--out",
    "out",
    type=click.Path(path_type=Path),
    default=None,
    help="where to write it (default workspace/dashboard.html)",
)
@pass_ctx
def dashboard(ctx: Ctx, as_json: bool, open_it: bool, out: Path | None) -> None:
    """Write workspace/dashboard.html from the state, the vault and the scores."""
    from vibemap import dashboard as dash  # noqa: PLC0415

    data = dash.numbers(ctx.state, ROOT)
    if as_json:
        click.echo(dash.as_json(data))
        return
    path = dash.write(data, out or ROOT / "workspace" / "dashboard.html")
    console.print(
        f"[ok]Wrote[/] [path]{path}[/]: {data['stops']}/{data['stops_total']} stops, "
        f"[xp]{data['xp']} XP[/], {data['notes']} notes, {data['scores']['runs']} runs."
    )
    if open_it:
        click.launch(str(path))


# ---- configuration --------------------------------------------------------------


@cli.group()
def config() -> None:
    """Show or change config/camp.toml."""


@config.command("show")
@pass_ctx
def config_show(ctx: Ctx) -> None:
    click.echo(ctx.cfg.dump())


def _set_learner(ctx: Ctx, field: str, value: str) -> None:
    data = ctx.cfg.model_dump()
    data["learner"][field] = value
    ctx.cfg = Config.model_validate(data)
    ctx.cfg.save(CONFIG_PATH)
    console.print(f"[ok]{field}[/] = {value} ({CONFIG_PATH.name})")


@cli.command()
@click.argument("persona_id", required=False)
@pass_ctx
def persona(ctx: Ctx, persona_id: str | None) -> None:
    """List personas, or switch to one (writes its dataset and vault note)."""
    if persona_id is None:
        t = Table(box=None, header_style="path")
        t.add_column("id")
        t.add_column("who")
        t.add_column("field", style="muted")
        for p in PERSONAS.values():
            mark = " [ok](current)[/]" if p.id == ctx.cfg.learner.persona else ""
            t.add_row(p.id + mark, p.label, p.field)
        console.print(t)
        return
    try:
        p = get_persona(persona_id)
    except ValueError as e:
        _fail(str(e))
    _set_learner(ctx, "persona", p.id)
    ex = ROOT / "workspace" / "data" / "examples"
    ex.mkdir(parents=True, exist_ok=True)
    (ex / p.dataset.filename).write_text(p.dataset.to_csv(), encoding="utf-8")
    ctx.vault = Vault(ctx.cfg, ctx.state)
    ctx.vault.build(p)
    console.print(
        f"[ok]{p.label}[/]: dataset workspace/data/examples/{p.dataset.filename}, "
        "note vault/Camp/Your field.md"
    )


@cli.command()
@click.argument("name", required=False)
@pass_ctx
def name(ctx: Ctx, name: str | None) -> None:
    """Show or set your name (the game and the vault use it)."""
    if name is None:
        console.print(ctx.cfg.learner.name)
        return
    _set_learner(ctx, "name", name)
    ctx.state.name = name
    ctx.save()
    ctx.vault = Vault(ctx.cfg, ctx.state)
    ctx.vault.build(ctx.persona)
    console.print("[ok]vault rebuilt[/] with your name in vault/Camp/Tonight.md")


@cli.command()
@click.argument("level", required=False, type=click.Choice(list(DIFFICULTIES)))
@pass_ctx
def difficulty(ctx: Ctx, level: str | None) -> None:
    """Show or set the difficulty (beginner to god)."""
    if level is None:
        for k, d in DIFFICULTIES.items():
            mark = "[ok]*[/]" if k == ctx.cfg.learner.difficulty else " "
            console.print(f"{mark} [path]{k:9}[/] x{d.xp_multiplier} XP · {d.blurb}")
        return
    _set_learner(ctx, "difficulty", level)


def _set_interests(ctx: Ctx, chosen: list[str]) -> None:
    """One writer for the choice: camp.toml is the truth, state is the copy."""
    data = ctx.cfg.model_dump()
    data["learner"]["interests"] = chosen
    ctx.cfg = Config.model_validate(data)
    ctx.cfg.save(CONFIG_PATH)
    ctx.state.interests = list(chosen)
    ctx.save()


def _interest_lines(ctx: Ctx) -> None:
    chosen = ctx.cfg.learner.interests
    for c, name, blurb in shelves():
        mark = "[ok]*[/]" if (not chosen or c in chosen) else " "
        console.print(f"{mark} [path]{c:10}[/] {name:24} [muted]{blurb}[/]")
    if chosen:
        console.print(
            f"Chosen: [ok]{', '.join(shelf_label(c) for c in chosen)}[/]. "
            "Nothing is hidden by a choice; these come first."
        )
    else:
        console.print(
            "[ok]Everything[/], the default. Narrow it with "
            "[accent]vibe interests set data,shell,agents[/]."
        )


@cli.command()
@click.argument("action", required=False, type=click.Choice(["list", "set", "all"]))
@click.argument("names", required=False)
@pass_ctx
def interests(ctx: Ctx, action: str | None, names: str | None) -> None:
    """What you want to learn: which shelves of the tree come first."""
    if action in (None, "list"):
        _interest_lines(ctx)
        _print_next_topic(ctx)
        return
    if action == "all":
        _set_interests(ctx, [])
        console.print("[ok]interests[/] = everything (config/camp.toml)")
        return
    if not names:
        _fail("vibe interests set data,shell,agents (or: vibe interests all)")
    try:
        chosen = parse_interests(names)
    except ValueError as e:
        _fail(str(e))
    _set_interests(ctx, chosen)
    console.print(
        f"[ok]interests[/] = {', '.join(chosen) or 'everything'} ({CONFIG_PATH.name})"
    )
    _print_next_topic(ctx)


def _print_next_topic(ctx: Ctx) -> None:
    nxt = suggestions(ctx.cfg.learner.interests, ctx.state.roadmap_done, limit=1)
    if nxt:
        s = nxt[0]
        console.print(
            f"Next topic: [accent]{s.name}[/] "
            f"([path]{shelf_label(s.shelf)}[/], {campaign.depth_label(s.depth)})"
        )


@cli.command()
@click.argument("provider_id", required=False, type=click.Choice(list(PROVIDERS)))
@pass_ctx
def provider(ctx: Ctx, provider_id: str | None) -> None:
    """Show or set the model provider CLI used by explain and council."""
    if provider_id is None:
        for p in PROVIDERS.values():
            mark = "[ok]*[/]" if p.id == ctx.cfg.learner.provider else " "
            state = "[ok]installed[/]" if p.available() else f"[muted]{p.install}[/]"
            console.print(f"{mark} [path]{p.id:9}[/] {p.label:22} {state}")
        return
    _set_learner(ctx, "provider", provider_id)


@cli.command()
@click.argument("mode", required=False, type=click.Choice(["campaign", "roadmap"]))
@pass_ctx
def mode(ctx: Ctx, mode: str | None) -> None:
    """campaign (four evenings) or roadmap (the tech tree as quests)."""
    if mode is None:
        console.print(f"mode = [path]{ctx.cfg.learner.mode}[/]")
        return
    _set_learner(ctx, "mode", mode)


@cli.command()
@click.argument("name", required=False)
@click.option(
    "--create", is_flag=True, help="ask the provider to write themes/NAME.toml"
)
@click.option("--brief", default="", help="one line describing the theme to create")
@pass_ctx
def theme(ctx: Ctx, name: str | None, create: bool, brief: str) -> None:
    """List themes, switch to one, or create a custom one with the provider."""
    if name is None:
        for t in THEMES.values():
            mark = "[ok]*[/]" if t.id == ctx.cfg.theme.preset else " "
            console.print(
                f"{mark} [path]{t.id:12}[/] {t.label} ({t.tone}, {t.pairing_kind})"
            )
        custom = (
            sorted((ROOT / "themes").glob("*.toml"))
            if (ROOT / "themes").exists()
            else []
        )
        for p in custom:
            console.print(f"  [path]{p.stem:12}[/] custom (themes/{p.name})")
        return
    if create:
        from vibemap.council import create_theme

        try:
            path = create_theme(ctx.cfg.learner.provider, name, brief)
        except (ProviderMissing, RuntimeError, ValueError) as e:
            _fail(str(e))
        console.print(f"[ok]wrote[/] {path.relative_to(ROOT)}")
    try:
        load_theme(name)
    except ValueError as e:
        _fail(str(e))
    data = ctx.cfg.model_dump()
    data["theme"]["preset"] = name
    Config.model_validate(data).save(CONFIG_PATH)
    if (ROOT / "tools" / "build.py").exists():
        console.print(f"[ok]theme[/] = {name}. Run `just build` to bake it in.")
    else:
        console.print(
            f"[ok]theme[/] = {name}. It colours the terminal and the vault; the "
            "hosted game keeps the studio theme, because baking a theme into the "
            "game needs the product repository."
        )


# ---- dotfiles ------------------------------------------------------------------


@cli.group(invoke_without_command=True)
@click.pass_context
def dotfiles(click_ctx: click.Context) -> None:
    """Terminal setup modules from Tom's toolbox: list, show, install."""
    if click_ctx.invoked_subcommand is None:
        click_ctx.invoke(dotfiles_list)


@dotfiles.command("list")
@pass_ctx
def dotfiles_list(ctx: Ctx) -> None:
    """Every module with its install state."""
    from vibemap import dotfiles as df

    home, vault = df.default_home(), ROOT / ctx.cfg.vault.path
    t = Table(box=None, header_style="path")
    t.add_column("id")
    t.add_column("module")
    t.add_column("state")
    t.add_column("what", style="muted", max_width=70)
    for m in df.MODULES.values():
        state = (
            "[ok]installed[/]"
            if df.is_installed(m, home=home, vault=vault)
            else "[todo]not yet[/]"
        )
        t.add_row(m.id, m.name, state, m.what.split(". ")[0] + ".")
    console.print(t)
    console.print(
        "[muted]vibe dotfiles show <id> prints the files; "
        "vibe dotfiles install <id> (or --all) writes them with backups. "
        "Adapted from github.com/tpetedb/toms-toolbox (MIT).[/]"
    )


@dotfiles.command("show")
@click.argument("module_id")
@pass_ctx
def dotfiles_show(ctx: Ctx, module_id: str) -> None:
    """Print a module's files, brew line and what to do after."""
    from vibemap import dotfiles as df

    try:
        m = df.get_module(module_id)
    except ValueError as e:
        _fail(str(e))
    console.print(Panel(m.what, title=m.name, border_style="accent"))
    if m.brew:
        console.print(f"[path]deps[/]  {df.brew_command(m)}")
    for rel, target in m.files:
        console.print(f"[path]file[/]  {target}")
        console.print(escape(df.source_text(rel).rstrip()), highlight=False)
        console.print()
    if m.append:
        console.print(f"[path]appends to[/] {m.append[0]}: {escape(m.append[1])}")
    console.print(f"[path]after[/] {m.after}\n[path]docs[/]  {m.docs}")


@dotfiles.command("install")
@click.argument("module_id", required=False)
@click.option("--all", "everything", is_flag=True, help="every module")
@click.option("--dry-run", is_flag=True, help="print what would change, write nothing")
@click.option(
    "--brew", "run_brew", is_flag=True, help="also run brew install for the deps"
)
@pass_ctx
def dotfiles_install(
    ctx: Ctx, module_id: str | None, everything: bool, dry_run: bool, run_brew: bool
) -> None:
    """Write a module's files (backups for anything that differs)."""
    from vibemap import dotfiles as df

    if not module_id and not everything:
        _fail("give a module id or --all; vibe dotfiles lists them")
    home, vault = df.default_home(), ROOT / ctx.cfg.vault.path
    ids = list(df.MODULES) if everything else [module_id]
    for mid in ids:
        try:
            m = df.get_module(mid)  # type: ignore[arg-type]
        except ValueError as e:
            _fail(str(e))
        if m.macos_only and sys.platform != "darwin":
            console.print(f"[warn]{m.id}[/]: macOS only, skipped")
            continue
        if run_brew and m.brew and not dry_run:
            subprocess.run(["brew", "install", *" ".join(m.brew).split()], check=False)
        p = df.install(m, home=home, vault=vault, dry_run=dry_run)
        verb = "would write" if dry_run else "wrote"
        for target, backup in p.writes:
            console.print(
                f"[ok]{verb}[/] {target}"
                + ("  [muted](backup kept)[/]" if backup else "")
            )
        for rc in p.appends:
            console.print(
                f"[ok]{'would append' if dry_run else 'appended'}[/] one line to {rc}"
            )
        for target in p.skipped:
            console.print(f"[muted]unchanged[/] {target}")
        if m.brew and not run_brew:
            console.print(f"[muted]deps: {df.brew_command(m)}[/]")
        console.print(f"[path]{m.id}[/] {m.after}")


# ---- news ---------------------------------------------------------------------


@cli.command("news")
@click.option("--limit", default=40, show_default=True, help="items to keep")
@click.option("--dry-run", is_flag=True, help="print, write nothing")
@click.option("--json", "as_json", is_flag=True, help="print the items as JSON")
@pass_ctx
def news_cmd(ctx: Ctx, limit: int, dry_run: bool, as_json: bool) -> None:
    """Pull the AI feeds into the vault note News and a news.json.

    The file is data/news.json in the product, where the build bakes it into
    the game, and .vibe/news.json in a camp, which has no build.
    """
    from vibemap import news

    feeds = (
        tuple((news.source_name(u), u) for u in ctx.cfg.news.feeds)
        or news.DEFAULT_FEEDS
    )
    items, problems = news.fetch(feeds, per_feed=ctx.cfg.news.per_feed)
    items = items[:limit]
    if as_json:
        click.echo(json.dumps([i.__dict__ for i in items], indent=1))
        return
    for it in items[:12]:
        console.print(
            f"[muted]{it.date[:10] or '          '}[/] {escape(it.title)}  "
            f"[path]{it.source}[/]"
        )
    if len(items) > 12:
        console.print(f"[muted]... and {len(items) - 12} more[/]")
    for p in problems:
        console.print(f"[warn]feed[/] {escape(p)}")
    if dry_run:
        return
    # The product bakes data/news.json into the game; a camp has no build, so
    # the feed stays in its state folder and the vault note is the reader.
    target = ROOT / "data" if (ROOT / "tools" / "build.py").exists() else ROOT / ".vibe"
    written = target / "news.json"
    news.write_json(items, written)
    ctx.vault.write("News", news.note_body(items, problems), tags=["concept"])
    console.print(
        f"[ok]news[/]: {len(items)} items in {written.relative_to(ROOT)} and vault/"
        f"{ctx.cfg.vault.folder}/News.md"
    )


def _pet(ctx: Ctx) -> pet.Pet:
    c = ctx.cfg.pet
    try:
        return pet.resolve(
            ctx.state.name, species=c.species, name=c.name, eye=c.eye, hat=c.hat
        )
    except ValueError as e:
        _fail(f"camp.toml [pet]: {e}")
        raise


@cli.command("pet")
@click.option(
    "--watch",
    "--animate",
    "-w",
    "-a",
    "animate",
    is_flag=True,
    help="a looping preview until Ctrl-C",
)
@click.option("--all", "gallery", is_flag=True, help="every species, frame 0")
@click.option("--species", default=None, help="set the species in camp.toml")
@click.option("--name", "pet_name", default=None, help="set the name in camp.toml")
@click.option("--eye", default=None, help="set the eye in camp.toml")
@click.option("--hat", default=None, help="set the hat in camp.toml")
@click.option(
    "--style",
    type=click.Choice(["auto", "pixel", "ascii"]),
    default=None,
    help="set the renderer in camp.toml",
)
@click.option("--on/--off", "enabled", default=None, help="show or hide the pet")
@click.option("--reset", is_flag=True, help="back to what your name rolled")
@pass_ctx
def pet_cmd(
    ctx: Ctx,
    animate: bool,
    gallery: bool,
    species: str | None,
    pet_name: str | None,
    eye: str | None,
    hat: str | None,
    style: str | None,
    enabled: bool | None,
    reset: bool,
) -> None:
    """Your terminal companion: show it, watch it, or configure it.

    The creature, its rarity and its stats are rolled from your name, the
    same roll as claude-buddy (MIT, Romesh Niriella). Six species are real
    pixel sprites: the crab, duck, turtle and snail from vscode-pets (MIT,
    Anthony Shaw), the cat and the dog from two CC0 packs by Shepardskin on
    OpenGameArt, all credited in vibemap/data/pets/CREDITS.md. Every other
    species keeps the ASCII art. Overrides live in config/camp.toml under
    [pet]; --species picks one and writes it there.
    """
    if gallery:
        for name, rows in pet.gallery():
            console.print(f"[path]{name}[/]")
            console.print("\n".join(rows))
            console.print()
        return
    changes = {
        k: v
        for k, v in {
            "species": species,
            "name": pet_name,
            "eye": eye,
            "hat": hat,
        }.items()
        if v is not None
    }
    if reset:
        changes = {"species": "", "name": "", "eye": "", "hat": ""}
    if changes or style is not None or enabled is not None:
        data = ctx.cfg.model_dump()
        data["pet"].update(changes)
        if style is not None:
            data["pet"]["style"] = style
        if enabled is not None:
            data["pet"]["enabled"] = enabled
        cfg = Config.model_validate(data)
        try:
            pet.resolve(ctx.state.name, **{k: data["pet"][k] for k in changes})
        except ValueError as e:
            _fail(str(e))
        cfg.save(CONFIG_PATH)
        ctx.cfg = cfg
        # The table name is square-bracketed, so it has to be escaped for rich.
        console.print(f"[ok]{CONFIG_PATH.name} \\[pet] updated[/]")
    p = _pet(ctx)
    how = ctx.cfg.pet.style
    if not animate:
        console.print(pet.render(p, style=how))
        _pet_credit(p, how)
        return
    import time

    from rich.live import Live

    sprite = pet.columns(p, how)
    width = max(sprite, console.width - 4)
    # Eight frames a second for the sprites, half a second for the art.
    period = 1 / PET_FPS if sprite > pet.WIDTH else 0.5
    tick = 0
    try:
        with Live(console=console, refresh_per_second=8) as live:
            while True:
                offset = pet.stroll(tick, width, sprite_width=sprite)
                live.update(
                    pet.render(
                        p,
                        tick,
                        stats=False,
                        offset=offset,
                        style=how,
                        state=pet.gait(tick, width, sprite_width=sprite),
                    )
                )
                time.sleep(period)
                tick += 1
    except KeyboardInterrupt:
        _pet_credit(p, how)
        console.print(f"{p.face}  bye")


def _pet_cheer(ctx: Ctx) -> None:
    """The happy state, once, whenever a stop is claimed.

    On a real terminal it plays the state through at the sprite's own rate; a
    pipe or a test gets the single frame, so nothing depends on the clock.
    """
    if not ctx.cfg.pet.enabled:
        return
    p = _pet(ctx)
    how = ctx.cfg.pet.style
    frames = pet.happy_frames(p, how)
    first = pet.body(p, 0, style=how, state="happy")
    if frames == 1 or not console.is_terminal:
        console.print(first, end="")
    else:
        import time

        from rich.live import Live

        with Live(first, console=console, refresh_per_second=PET_FPS) as live:
            for tick in range(1, frames):
                time.sleep(1 / PET_FPS)
                live.update(pet.body(p, tick, style=how, state="happy"))
    console.print(f"[muted]{p.name} is pleased.[/]")


def _pet_credit(p: pet.Pet, style: str) -> None:
    """Say who drew the sprites whenever they are the thing on screen."""
    line = pet.credit(p, style)
    if line:
        console.print(f"[muted]{line}[/]")


# ---- explain, council, toolbelt ------------------------------------------------


@cli.command()
@click.option(
    "--commits", "-n", default=3, show_default=True, help="how many commits back"
)
@pass_ctx
def explain(ctx: Ctx, commits: int) -> None:
    """Ask the provider to explain what changed in the last commits, in plain words."""
    log = subprocess.run(
        ["git", "log", f"-{commits}", "--stat", "--format=%h %s%n%b"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout
    diff = subprocess.run(
        [
            "git",
            "diff",
            f"HEAD~{commits}",
            "--",
            ".",
            ":!game/vibe-map.html",
            ":!uv.lock",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout
    if not log:
        _fail("no git history to explain")
    prompt = (
        "You are explaining a git history to someone learning to code with an AI "
        "agent. In plain words, no jargon, at most ten sentences: what changed, "
        "why it probably "
        "changed, and one thing to check. Then list the files touched.\n\n"
        f"GIT LOG:\n{log}\n\nDIFF (truncated):\n{diff[:12000]}"
    )
    try:
        console.print(
            Panel(
                ask(ctx.cfg.learner.provider, prompt),
                title="explain",
                border_style="accent",
            )
        )
    except (ProviderMissing, RuntimeError) as e:
        console.print(f"[warn]{escape(str(e))}[/]")
        console.print(escape(log))


@cli.command()
@click.argument("topic")
@click.option(
    "--mentors",
    "-m",
    default="",
    help="comma-separated mentor ids (default: all on the current island)",
)
@click.option(
    "--dry-run", is_flag=True, help="print the prompts instead of calling the provider"
)
@pass_ctx
def council(ctx: Ctx, topic: str, mentors: str, dry_run: bool) -> None:
    """Convene the mentors: each answers, they review each other, a chairman decides."""
    from vibemap.council import convene

    ids = [m.strip() for m in mentors.split(",") if m.strip()]
    try:
        path = convene(ctx, topic, mentor_ids=ids, dry_run=dry_run)
    except (ProviderMissing, RuntimeError, ValueError) as e:
        _fail(str(e))
    if path:
        console.print(f"[ok]council minutes[/]: {path.relative_to(ROOT)}")


@cli.group()
def chat() -> None:
    """Answer questions about the game with your own Claude or Codex subscription."""


@chat.command("serve")
@click.option(
    "--pair",
    "pair_code",
    default=None,
    help="the pairing code the game's chat panel shows",
)
@click.option(
    "--port",
    default=chat_bridge.DEFAULT_PORT,
    show_default=True,
    help="0 takes a free port; type it into the panel",
)
@click.option(
    "--provider",
    "provider_id",
    default=None,
    type=click.Choice(list(PROVIDERS)),
    help="default: the provider in config/camp.toml",
)
@click.option(
    "--origin",
    "origins",
    multiple=True,
    help="one more allowed Origin (your own hosted copy)",
)
@click.option(
    "--timeout",
    default=chat_bridge.DEFAULT_TIMEOUT,
    show_default=True,
    help="seconds before an answer is given up on",
)
@pass_ctx
def chat_serve(
    ctx: Ctx,
    pair_code: str | None,
    port: int,
    provider_id: str | None,
    origins: tuple[str, ...],
    timeout: int,
) -> None:
    """Run the loopback bridge the game's chat panel talks to."""
    code = pair_code or chat_bridge.new_code()
    try:
        bridge = chat_bridge.Bridge(
            ctx.cfg,
            code=code,
            provider_id=provider_id,
            origins=frozenset(origins),
            timeout=timeout,
        )
    except ValueError as e:
        _fail(str(e))
    health = bridge.health()
    server = chat_bridge.serve(bridge, port=port)
    bound = server.server_address[1]
    console.print(
        Panel(
            f"[title]pairing code[/] {bridge.code}\n"
            f"[title]bridge[/] http://{chat_bridge.HOST}:{bound}\n"
            f"[title]provider[/] {health['label']}"
            + (
                ""
                if health["available"]
                else f" [warn]not installed[/] ({health['install']})"
            )
            + "\n[muted]Loopback only. It answers questions; it never runs a command "
            "for the page. Ctrl-C to stop.[/]",
            title="vibe chat",
            border_style="accent",
        )
    )
    if not pair_code:
        console.print(
            "[muted]Type this code into the game's chat panel, or start the "
            "bridge with[/] vibe chat serve --pair <code from the panel>"
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("[muted]bridge stopped[/]")
    finally:
        server.server_close()


@chat.command("ask")
@click.argument("question")
@click.option("--world", "-w", default="campus", type=click.Choice(WORLDS))
@click.option("--stop", "-s", type=int, default=None, help="the stop it is about")
@click.option("--mentor", "-m", "mentor_id", default=None, help="the mentor in view")
@click.option(
    "--artifact", "-a", "artifact_id", default=None, help="the artifact in view"
)
@pass_ctx
def chat_ask(
    ctx: Ctx,
    question: str,
    world: str,
    stop: int | None,
    mentor_id: str | None,
    artifact_id: str | None,
) -> None:
    """The same question and the same prompt, answered in the terminal."""
    try:
        ask = chat_bridge.Ask.from_payload(
            {
                "question": question,
                "world": world,
                "stop": stop,
                "mentor": mentor_id,
                "artifact": artifact_id,
            }
        )
    except ValueError as e:
        _fail(str(e))
    bridge = chat_bridge.Bridge(ctx.cfg, code=chat_bridge.new_code())
    console.print(f"[muted]{chat_bridge.context_line(ask)}[/]")
    try:
        answer = "".join(bridge.answer(ask))
    except (ProviderMissing, RuntimeError) as e:
        _fail(str(e))
    console.print(Panel(escape(answer.strip()), title="chat", border_style="accent"))


@cli.command()
@click.option(
    "--tier",
    type=click.Choice(["core", "evening", "toolbelt", "provider"]),
    default=None,
)
@click.option(
    "--install",
    "install_id",
    default=None,
    help="a tool id, or 'missing' for every missing one",
)
@click.option("--dry-run", is_flag=True, help="print the commands only")
def toolbelt(tier: str | None, install_id: str | None, dry_run: bool) -> None:
    """What is installed, what is missing, and the documented command for each."""
    if install_id:
        targets = (
            [
                t
                for t in TOOLS
                if not t.is_installed() and (tier is None or t.tier == tier)
            ]
            if install_id == "missing"
            else [get_tool(install_id)]
        )
        for t in targets:
            console.print(f"[title]{t.label}[/] ({t.size}) {t.what}")
            rc = install(t, dry_run=dry_run)
            console.print("[ok]ok[/]" if rc == 0 else f"[err]exit {rc}[/]")
        return
    t = Table(box=None, header_style="path")
    t.add_column("tool")
    t.add_column("tier", style="muted")
    t.add_column("status")
    t.add_column("what", style="muted")
    for tool in TOOLS:
        if tier and tool.tier != tier:
            continue
        v = tool.version()
        status = f"[ok]{v}[/]" if v else f"[warn]missing[/] [muted]{tool.install}[/]"
        t.add_row(tool.label, tool.tier, status, tool.what)
    console.print(t)


# One camp per person and start date: vibe-map-<name>-<YYYY-MM-DD>. Sorts by
# date in a listing and tells you which camp a note or a code came from.
def camp_dir_name(who: str | None = None, day: date | None = None) -> str:
    """The folder name convention for a new camp: your name, vibe-map, the date."""
    raw = who or os.environ.get("VIBE_NAME") or getpass.getuser() or "player"
    # Fold accents (Jorg, not j-rg) the same way the game's setup guide does.
    folded = unicodedata.normalize("NFD", raw).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-") or "player"
    return f"vibe-map-{slug}-{(day or date.today()).isoformat()}"


# The template is stored with underscores where a camp has dots, so packaging
# and git never skip the folders; the camp gets the real names.
TEMPLATE_NAMES = {
    "_gitignore": ".gitignore",
    "_agents": ".agents",
    "_claude": ".claude",
    "_github": ".github",
}


def copy_template(target: Path) -> int:
    """Write the camp skeleton from the package into TARGET; returns the file count."""
    # Inside the context: from a wheel this is a real folder, from a zip a temp one.
    with project.data_dir("template") as src:
        return _copy_tree(src, target)


def _copy_tree(src: Path, target: Path) -> int:
    n = 0
    for f in sorted(src.rglob("*")):
        if not f.is_file() or "__pycache__" in f.parts:
            continue
        parts = [TEMPLATE_NAMES.get(p, p) for p in f.relative_to(src).parts]
        dst = target.joinpath(*parts)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(f.read_bytes())
        n += 1
    skills = target / ".claude" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    src_skills = target / ".agents" / "skills"
    for skill in sorted(src_skills.iterdir()) if src_skills.is_dir() else []:
        link = skills / skill.name
        if skill.is_dir() and not link.exists():
            link.symlink_to(Path("..") / ".." / ".agents" / "skills" / skill.name)
    return n


def _quiet(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> int:
    return subprocess.run(
        cmd, cwd=cwd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode


@cli.command()
@click.argument("directory", required=False)
@click.option(
    "--github",
    default=None,
    help="also create OWNER/NAME on GitHub and push the camp there (needs gh)",
)
@click.option(
    "--name", "who", default=None, help="your name for the folder (default: the login)"
)
def new(directory: str | None, github: str | None, who: str | None) -> None:
    """Start a camp in DIRECTORY (default vibe-map-<name>-<date>): your workspace,
    your vault, the configuration. The engine stays in the vibe command."""
    if directory is None:
        directory = camp_dir_name(who)
        console.print(f"[muted]folder from the convention:[/] {directory}")
    target = Path(directory).expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        _fail(f"{target} exists and is not empty")
    target.mkdir(parents=True, exist_ok=True)
    n = copy_template(target)
    console.print(f"[ok]{n} files[/] from the template into {target}")
    if who:
        toml = target / project.CAMP_CONFIG
        toml.write_text(
            toml.read_text(encoding="utf-8").replace(
                'name = "<your_name>"', f'name = "{who}"', 1
            ),
            encoding="utf-8",
        )
    env = dict(os.environ, VIBE_HOME=str(target))
    if _quiet([sys.executable, "-m", "vibemap.cli", "init"], target, env) == 0:
        console.print("[ok]vault built[/] (vault/Camp/Tonight.md is the hub)")
    else:
        console.print("[warn]vault not built[/]; run: vibe init")
    committed = False
    if _quiet(["git", "init", "-q"], target) == 0:
        _quiet(["git", "add", "-A"], target)
        committed = (
            _quiet(
                ["git", "commit", "-q", "-m", "Start the camp from the vibe template"],
                target,
            )
            == 0
        )
        if committed:
            console.print("[ok]git repository[/] with the first commit")
        else:
            console.print(
                "[warn]git could not commit[/] (set user.name and user.email); "
                "commit by hand, then push"
            )
    else:
        console.print("[warn]git not found[/]; the camp is not under version control")
    if github and not committed:
        _fail("no first commit to push; fix git, commit, then: gh repo create")
    if github:
        cmd = ["gh", "repo", "create", github, "--source", ".", "--public", "--push"]
        console.print(f"[muted]$ {' '.join(cmd)}[/]")
        if subprocess.run(cmd, cwd=target).returncode != 0:
            _fail("gh could not create the repository; is gh installed and logged in?")
    console.print(
        f"[ok]camp ready[/] at {target}\nNext:\n  cd {target}\n"
        "  just start          # or: vibe start\n"
        "  vibe play           # the game, hosted; vibe play --offline caches it"
    )


@cli.command()
@click.option(
    "--from",
    "source",
    default=None,
    help="a product checkout to copy from (default: the source vibe carries)",
)
@click.option("--force", is_flag=True, help="replace an existing fork")
@pass_ctx
def fork(ctx: Ctx, source: str | None, force: bool) -> None:
    """Copy the game's source into workspace/forks/vibe-map and make it yours.

    The fork carries src/ (with its own src/config/), tools/build.py and the
    generated inputs the build needs, so `just build` there produces your own
    game file. Its journey configuration is still the camp's config/camp.toml.
    No clone and no network: an installed vibe ships the source it copies.
    """
    dest = quests.fork_dir()
    if dest.exists() and any(dest.iterdir()) and not force:
        _fail(f"{dest} exists; pass --force to replace it")
    with _fork_source(source) as src_root:
        if dest.exists():
            shutil.rmtree(dest)
        n = _copy_fork(src_root, dest)
    console.print(f"[ok]{n} files[/] into [path]{dest}[/]")
    console.print(
        "Next:\n"
        f"  cd {dest}\n"
        "  edit src/config/00-config.js   # the world scale, the palette\n"
        "  just build                     # your own game/vibe-map.html\n"
        "  vibe check --fork config       # the challenge that checks\n"
        "The four challenges are in the fork's README.md; "
        "vibe check --world prod 6 runs them all."
    )


FORK_JUSTFILE = """# Your fork of the game. One command: build it, then open it.
# The source configuration is src/config/; the journey configuration stays in
# your camp's config/camp.toml. See docs/CONFIG.md in the product.

# show the task list
default:
    @just --list

# concatenate src/ into game/vibe-map.html
build:
    python3 tools/build.py

# open your build
game: build
    open game/vibe-map.html

# record whether the build passes right now (the repair challenge)
record:
    python3 tools/record_build.py
"""

FORK_RECORD = '''"""Record one build result in repair.json.

Run it while the build is broken, repair the build, run it again: the file
then holds a failing run followed by a passing one, which is the evidence
`vibe check --fork repair` looks for. Nothing else writes this file.

    python3 tools/record_build.py
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = ROOT / "repair.json"
VERSION = 1


def main() -> int:
    out = subprocess.run(
        [sys.executable, "tools/build.py"], cwd=ROOT, capture_output=True, text=True
    )
    ok = out.returncode == 0
    data = {"version": VERSION, "runs": []}
    if MARKER.exists():
        data = json.loads(MARKER.read_text(encoding="utf-8"))
        if data.get("version") != VERSION:
            raise SystemExit(
                f"repair.json version {data.get('version')} is not {VERSION}"
            )
    error = (out.stderr or out.stdout).strip().splitlines()
    data["runs"].append(
        {
            "at": dt.datetime.now().isoformat(timespec="seconds"),
            "ok": ok,
            "error": "" if ok else error[-1][:200] if error else "no output",
        }
    )
    MARKER.write_text(json.dumps(data, indent=2) + "\\n", encoding="utf-8")
    said = "build passed" if ok else "build failed"
    print(f"{said}, {len(data['runs'])} run(s) recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

FORK_README = """# Your fork of Vibe Map

Your fork is yours to break and repair; the course keeps living in the
product (https://github.com/tpetedb/vibe-map). Nothing here feeds back into
it, and nothing here is needed to play: this is the copy you experiment on.

Everything the build needs is here: `src/` (the game in load order, with
`src/vendor/` and your own `src/config/`), `tools/build.py` and the generated
inputs under `tools/generated/`.

    just build      # or: python3 tools/build.py
    open game/vibe-map.html

Your camp's `config/camp.toml` still decides who you are, how hard and which
theme; `src/config/00-config.js` is the game's own level: the world scale,
the island radius, the palette. `vibe check --fork` verifies that it builds
and that your configuration is no longer the product's.

## Challenges

Each one is checked; `vibe check --fork <challenge>` runs one of them, and
`vibe check --world prod 6` runs the stop they belong to.

1. `exists`: fork tpetedb/vibe-map on GitHub, then `vibe fork` here.
2. `config`: change one value in `src/config/00-config.js` (the world scale,
   or a palette colour) and rebuild. Look at the result.
3. `topic`: pick a topic from `vibe news` or an article you found, and have
   your agent add it to `tools/generated/campaign.json` (a stop of your own)
   or to `tools/generated/tree.js` (a node of your own), then rebuild.
4. `repair`: break the build on purpose, run `just record`, read the error,
   repair it, and run `just record` again. The two runs in `repair.json` are
   the evidence.
"""


FORK_SOURCE = "fork_source"


def _fork_source_label(src_root: Path) -> str:
    """What the manifest records: a checkout by path, the package by version.

    The packaged source unpacks to a path nobody can visit twice, so naming the
    release is the only line that stays true.
    """
    if src_root.name == FORK_SOURCE:
        return f"vibe-map {__version__} (packaged source)"
    return str(src_root)


@contextmanager
def _fork_source(source: str | None) -> Iterator[Path]:
    """Where the fork is copied from: --from, this checkout, else the package.

    An installed `vibe` carries the game's source under vibemap/data, so a camp
    from `vibe new` can fork offline; a product checkout forks from its own src/
    so a maintainer always sees the working tree.
    """
    if source:
        given = Path(source).expanduser().resolve()
        if not (given / "src" / "config").is_dir():
            _fail(
                f"{given} is not a product checkout (no src/config). "
                "Clone https://github.com/tpetedb/vibe-map and pass it with --from."
            )
        yield given
        return
    if (ROOT / "src" / "config").is_dir():
        yield ROOT
        return
    with project.data_dir(FORK_SOURCE) as packaged:
        if not (Path(packaged) / "src" / "config").is_dir():
            _fail(
                "this copy of vibe carries no game source. Clone "
                "https://github.com/tpetedb/vibe-map and pass it with --from."
            )
        yield Path(packaged)


def _copy_fork(src_root: Path, dest: Path) -> int:
    """Write the fork: src/, the build tool, the generated inputs, the tasks."""
    dest.mkdir(parents=True, exist_ok=True)
    n = _copy_tree(src_root / "src", dest / "src")
    (dest / "tools").mkdir(exist_ok=True)
    shutil.copyfile(src_root / "tools" / "build.py", dest / "tools" / "build.py")
    (dest / "tools" / "record_build.py").write_text(FORK_RECORD, encoding="utf-8")
    n += 2
    generated = dest / "tools" / "generated"
    generated.mkdir(exist_ok=True)
    for name in ("notes.js", "tree.js"):
        shutil.copyfile(src_root / "tools" / "generated" / name, generated / name)
        n += 1
    # The campaign travels with the fork so the build never needs the package.
    (generated / "campaign.json").write_text(
        project.data_text("campaign.json"), encoding="utf-8"
    )
    (dest / "justfile").write_text(FORK_JUSTFILE, encoding="utf-8")
    (dest / "README.md").write_text(FORK_README, encoding="utf-8")
    (dest / "game").mkdir(exist_ok=True)
    (dest / quests.FORK_MANIFEST).write_text(
        json.dumps(
            {
                "version": quests.FORK_VERSION,
                "source": _fork_source_label(src_root),
                "created": date.today().isoformat(),
                "config_sha256": quests.config_fingerprint(dest / "src" / "config"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return n + 4


HOSTED_GAME = "https://tpetedb.github.io/vibe-map/"
RAW_GAME = "https://raw.githubusercontent.com/tpetedb/vibe-map/main/game/vibe-map.html"


def open_game(offline: bool = False) -> str:
    """Open the game and say what was opened: the build, the cache, the host."""
    local = ROOT / "game" / "vibe-map.html"
    cached = ROOT / ".vibe" / "vibe-map.html"
    if offline and not local.exists():
        import urllib.request

        cached.parent.mkdir(parents=True, exist_ok=True)
        console.print(f"[muted]fetching {RAW_GAME}[/]")
        urllib.request.urlretrieve(RAW_GAME, cached)
        console.print(f"[ok]cached[/] {cached.relative_to(ROOT)}")
    for p in (local, cached):
        if p.exists():
            subprocess.run(["open", str(p)])
            return str(p)
    console.print(f"[muted]opening the hosted game[/] {HOSTED_GAME}")
    subprocess.run(["open", HOSTED_GAME])
    return HOSTED_GAME


@cli.command()
@click.option(
    "--offline", is_flag=True, help="download the game into .vibe/ and open that copy"
)
def play(offline: bool) -> None:
    """Open the game: the local build, the cached copy, else the hosted one."""
    open_game(offline)


@cli.command()
def start() -> None:
    """The onboarding screen: checks, choices, launchers."""
    from vibemap.tui import run

    run()


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
