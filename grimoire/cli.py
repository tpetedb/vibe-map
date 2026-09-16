#!/usr/bin/env python3
"""Grimoire CLI: the terminal companion to the game.

    uv run grimoire status            where you are, XP, level, badges
    uv run grimoire check [n]         verify a workstream, award the XP
    uv run grimoire done n "note"     claim it (checks first; --force to skip)
    uv run grimoire vault build       rebuild the Obsidian vault from state
    uv run grimoire export / import   the progress code the game speaks
    uv run grimoire start             the onboarding screen

`python3 grimoire/cli.py status` keeps working for the syllabus.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

if __package__ in (None, ""):  # run as a script: put the repo root on the path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from grimoire import __version__, campaign
from grimoire.config import CONFIG_PATH, DIFFICULTIES, Config
from grimoire.palette import RICH_THEME
from grimoire.personas import PERSONAS, get_persona
from grimoire.providers import PROVIDERS, ProviderMissing, ask
from grimoire.quests import BADGES, level_for, new_badges, quest_for, run_quest, xp_for
from grimoire.state import CheckRecord, State
from grimoire.themes import THEMES, load_theme
from grimoire.toolbelt import TOOLS, get_tool, install
from grimoire.vault import Vault

ROOT = Path(__file__).resolve().parents[1]
console = Console(theme=RICH_THEME, highlight=False)
WORLDS = list(campaign.WORLD_NAMES)


class Ctx:
    """Config, state and vault, loaded once per command."""

    def __init__(self) -> None:
        self.cfg = Config.load()
        self.state = State.load()
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


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="grimoire")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """The terminal companion to Vibe Code Camp."""
    try:
        ctx.obj = Ctx()
    except ValueError as e:
        _fail(str(e))


# ---- status -------------------------------------------------------------------


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
                    "persona": cfg.learner.persona,
                    "difficulty": cfg.learner.difficulty,
                    "mode": cfg.learner.mode, "provider": cfg.learner.provider,
                },
                indent=2,
            )
        )  # fmt: skip
        return
    diff = DIFFICULTIES[cfg.learner.difficulty]
    head = (
        f"[title]{st.name}[/] · {ctx.persona.label} · {diff.label} · "
        f"provider [path]{cfg.learner.provider}[/] · "
        f"theme [path]{cfg.theme.preset}[/]\n"
        f"Level [ok]{label}[/] ({age} age) · [xp]{st.xp} XP[/]"
        + (f" · {nxt - st.xp} to the next level" if nxt else " · top level")
        + f" · {st.total_done()}/32 stops"
    )
    console.print(Panel(head, title="Vibe Code Camp", border_style="accent"))
    t = Table(header_style="path", box=None, padding=(0, 1))
    t.add_column("evening")
    for i in range(1, 9):
        t.add_column(str(i), justify="center")
    t.add_column("done", justify="right")
    for w, ev in campaign.evenings().items():
        cells = [
            "[done]x[/]" if st.is_done(w, i) else "[todo].[/]" for i in range(1, 9)
        ]
        t.add_row(f"{ev.short} · {ev.island}", *cells, f"{len(st.done_w.get(w, []))}/8")
    console.print(t)
    if st.badges:
        console.print(
            "Badges: "
            + ", ".join(f"[ok]{BADGES.get(b, b).split(':')[0]}[/]" for b in st.badges)
        )
    nxt_ws = _next_workstream(st, "campus")
    if nxt_ws:
        console.print(
            f"Next: [path]{nxt_ws.hour} {nxt_ws.name}[/]. "
            f"Run [accent]grimoire check {nxt_ws.n}[/] when you think it is done."
        )
    else:
        console.print(
            "[ok]Evening 1 complete.[/] Pick another island: "
            "grimoire check --world winter 1"
        )


def _next_workstream(st: State, world: str):
    for ws in campaign.evenings()[world].workstreams:
        if not st.is_done(world, ws.n):
            return ws
    return None


# ---- check and done -----------------------------------------------------------


def _print_results(results, quest, cfg: Config) -> bool:
    t = Table(
        title=f"{quest.title} ({quest.world} {quest.n})", title_style="title", box=None
    )
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
            console.print(f"  [warn]hint[/] {r.hint}")
    return not failed


def _claim(ctx: Ctx, world: str, n: int, note: str, results, *, forced: bool) -> None:
    ws = campaign.evenings()[world].workstreams[n - 1]
    xp = xp_for(ctx.cfg.learner.difficulty)
    if forced:
        xp //= 2
    fresh = ctx.state.mark_done(world, n, note=note, xp=xp)
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
    else:
        console.print(f"[muted]{ws.name} was already done; note added.[/]")
    for b in badges:
        console.print(f"[title]Badge:[/] {BADGES[b]}")
    age, label, _ = level_for(ctx.state.xp)
    console.print(
        f"Level {label}, {ctx.state.xp} XP. "
        f"Note: vault/{ctx.cfg.vault.folder}/{ws.name}.md"
    )


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
@pass_ctx
def check(ctx: Ctx, n: int | None, world: str | None, all_: bool, claim: bool) -> None:
    """Verify the definition of done for a workstream and award the XP."""
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
    for k in targets:
        quest = quest_for(world, k, ctx.cfg)
        results = run_quest(quest, ctx.cfg)
        ok = _print_results(results, quest, ctx.cfg)
        if ok and claim and not ctx.state.is_done(world, k):
            _claim(ctx, world, k, "verified by grimoire check", results, forced=False)
        elif ok:
            console.print("[ok]all checks pass[/]")
        else:
            console.print(
                "[warn]not yet.[/] Fix the failed checks, "
                "or `grimoire done` with --force for half XP."
            )


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
    quest = quest_for(world, n, ctx.cfg)
    results = run_quest(quest, ctx.cfg)
    ok = _print_results(results, quest, ctx.cfg)
    if not ok and not force:
        _fail("checks failed; fix them or add --force (half XP)")
    _claim(ctx, world, n, note, results, forced=not ok)


# ---- vault --------------------------------------------------------------------


@cli.group()
def vault() -> None:
    """Build, lint and log the Obsidian vault."""


@vault.command("build")
@pass_ctx
def vault_build(ctx: Ctx) -> None:
    """Rebuild every generated note from the state."""
    paths = ctx.vault.build(ctx.persona)
    console.print(
        f"[ok]vault built[/]: {len(paths)} notes in {ctx.vault.dir.relative_to(ROOT)}"
    )


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
    console.print("[muted]written to vault/Grimoire/Map.md[/]")


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
    try:
        ctx.state.merge_code(code)
    except ValueError as e:
        _fail(str(e))
    ctx.save()
    ctx.vault.build(ctx.persona)
    console.print(
        f"[ok]imported[/]: {ctx.state.total_done()}/32 stops, {ctx.state.xp} XP"
    )


@cli.command()
@click.argument("mentor_id")
@click.argument("choice", type=click.Choice(["deep", "skip"]))
@pass_ctx
def mentor(ctx: Ctx, mentor_id: str, choice: str) -> None:
    """Record a mentor choice (deep or skip)."""
    try:
        m = campaign.mentor(mentor_id)
    except ValueError as e:
        _fail(str(e))
    ctx.state.path[mentor_id] = choice
    ctx.save()
    ctx.vault.build(ctx.persona)
    console.print(f"[ok]{m['name']}[/]: {choice}")


# ---- scores -------------------------------------------------------------------


@cli.command()
@click.option("--sql", "sql_name", default=None, help="run a query from sql/ instead")
def scores(sql_name: str | None) -> None:
    """Summarise data/scores.csv with polars, or run a sql/ query with DuckDB."""
    from grimoire.scores import frame_table, read_scores, run_sql, scores_table, summary

    if sql_name:
        try:
            console.print(frame_table(run_sql(sql_name), f"sql/{sql_name}"))
        except FileNotFoundError as e:
            _fail(str(e))
        return
    console.print(scores_table(summary(read_scores())))


# ---- configuration --------------------------------------------------------------


@cli.group()
def config() -> None:
    """Show or change grimoire.toml."""


@config.command("show")
@pass_ctx
def config_show(ctx: Ctx) -> None:
    click.echo(ctx.cfg.dump())


def _set_learner(ctx: Ctx, field: str, value: str) -> None:
    data = ctx.cfg.model_dump()
    data["learner"][field] = value
    ctx.cfg = Config.model_validate(data)
    ctx.cfg.save(CONFIG_PATH)
    console.print(f"[ok]{field}[/] = {value} (grimoire.toml)")


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
    ex = ROOT / "data" / "examples"
    ex.mkdir(parents=True, exist_ok=True)
    (ex / p.dataset.filename).write_text(p.dataset.to_csv(), encoding="utf-8")
    ctx.vault = Vault(ctx.cfg, ctx.state)
    ctx.vault.build(p)
    console.print(
        f"[ok]{p.label}[/]: dataset data/examples/{p.dataset.filename}, "
        "note vault/Grimoire/Your field.md"
    )


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
        from grimoire.council import create_theme

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
    console.print(f"[ok]theme[/] = {name}. Run `just build` to bake it into the game.")


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
            ":!game/grimoire.html",
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
    except ProviderMissing as e:
        console.print(f"[warn]{e}[/]")
        console.print(log)


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
    from grimoire.council import convene

    ids = [m.strip() for m in mentors.split(",") if m.strip()]
    try:
        path = convene(ctx, topic, mentor_ids=ids, dry_run=dry_run)
    except (ProviderMissing, RuntimeError, ValueError) as e:
        _fail(str(e))
    if path:
        console.print(f"[ok]council minutes[/]: {path.relative_to(ROOT)}")


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


@cli.command()
def play() -> None:
    """Open the game in the default browser."""
    subprocess.run(["open", str(ROOT / "game" / "grimoire.html")])


@cli.command()
def start() -> None:
    """The onboarding screen: checks, choices, launchers."""
    from grimoire.tui import run

    run()


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
