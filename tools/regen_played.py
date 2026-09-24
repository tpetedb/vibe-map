"""Regenerate an explicit local checkout of the public played camp.

The target must be a clean git checkout. Work is assembled in a temporary
camp first, then copied into the target and committed on the branch the caller
already chose. Nothing reaches a remote unless ``--push`` is present.

    uv run python tools/regen_played.py --camp ../vibe-map-played --dry-run
    uv run python tools/regen_played.py --camp ../vibe-map-played
    uv run python tools/regen_played.py --camp ../vibe-map-played --push
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools.script_camp import CAMP_MARKER, script_everything
from vibemap import campaign, quests
from vibemap.state import CheckRecord, State

ROOT = Path(__file__).resolve().parents[1]
COMMIT_MESSAGE = "Regenerate the played camp from the current release"
COPY_EXCLUDES = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
RETAINED_PREFIXES = ("workspace/", "vault/", "docs/media/")
REQUIRED_PRODUCT_FILE = "game/vibe-map.html"
REQUIRED_PRODUCT_DIR = "docs/media"
REQUIRED_MEDIA_FILES = ("README.md", "gameplay.gif", "hero.png")
SOURCE_MARKER = Path(".vibe/played-source.json")
PRODUCT_INPUTS = (
    "config",
    "docs/media",
    "game/vibe-map.html",
    "game/news.json",
    "pyproject.toml",
    "src",
    "tools/build.py",
    "tools/generated",
    "tools/script_camp.py",
    "tools/regen_played.py",
    "vibemap",
)
PLAYED_GITHUB_ORIGINS = {
    "git@github.com:tpetedb/vibe-map-played",
    "ssh://git@github.com/tpetedb/vibe-map-played",
    "https://github.com/tpetedb/vibe-map-played",
}


class RegenerationError(RuntimeError):
    """The target cannot be changed without risking work already there."""


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()
        raise RegenerationError(f"{' '.join(command)} failed: {detail}")
    return result.stdout.strip()


def _git(repo: Path, *args: str) -> str:
    return _run(["git", *args], cwd=repo)


def _played_origin(url: str) -> bool:
    """Recognize the public played repo or a local bare clone used for checks."""
    plain = url.rstrip("/").removesuffix(".git")
    if plain in PLAYED_GITHUB_ORIGINS:
        return True
    return Path(url).is_absolute() and Path(url).name == "vibe-map-played.git"


def _remote_urls(camp: Path, *, push: bool = False) -> tuple[str, ...]:
    args = (
        ("remote", "get-url", "--push", "--all", "origin")
        if push
        else ("remote", "get-url", "--all", "origin")
    )
    return tuple(_git(camp, *args).splitlines())


def check_target(camp: Path) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    """Return branch and remote URLs after proving the checkout is played."""
    camp = camp.resolve()
    if not (camp / ".git").exists() or not (camp / CAMP_MARKER).is_file():
        raise RegenerationError(
            f"{camp} is not a played camp checkout: expected .git and {CAMP_MARKER}"
        )
    status = _git(camp, "status", "--porcelain", "--untracked-files=all")
    if status:
        raise RegenerationError(f"{camp} is not clean; commit or move its work first")
    branch = _git(camp, "branch", "--show-current")
    if not branch:
        raise RegenerationError(f"{camp} has a detached HEAD; choose a branch first")
    origin = _remote_urls(camp)
    push_url = _remote_urls(camp, push=True)
    if (
        not origin
        or not push_url
        or not all(_played_origin(url) for url in (*origin, *push_url))
    ):
        raise RegenerationError(
            f"{camp} is not the tpetedb/vibe-map-played checkout: "
            f"origin fetch={origin!r}, push={push_url!r}"
        )
    return branch, origin, push_url


def played_state(product: Path = ROOT, *, name: str = "Tom") -> State:
    """The complete demonstration state, derived from current package data."""
    state = State(name=name, pet="crab")
    xp = quests.xp_for("normal")
    for world, evening in campaign.evenings().items():
        for stop in evening.workstreams:
            state.mark_done(world, stop.n, note="played instance", xp=xp)
            state.checks[f"{world}:{stop.n}"] = CheckRecord(
                ok=True, passed=["scripted learner deliverable"]
            )

    artifact_ids = [str(item["id"]) for item in campaign.artifacts()]
    mentor_ids = [str(mentor["id"]) for mentor in campaign.mentors()]
    state.path = {mentor_id: "deep" for mentor_id in mentor_ids}
    state.artifacts = list(artifact_ids)
    state.artifacts_built = list(artifact_ids)
    state.mentors = list(mentor_ids)
    state.items = [str(item["id"]) for item in campaign.collectibles()]

    achievements = [
        "first-light",
        "full-evening",
        "campaign",
        "collector",
        "builder",
        "mentored",
    ]
    for wearable in campaign.wearables():
        earned_by = str(wearable["by"])
        if earned_by not in achievements:
            achievements.append(earned_by)
    state.ach = achievements

    # One item per slot is visible. The last earned item in a slot wins, just
    # as toggleWear() does in the game.
    worn_by_slot: dict[str, str] = {}
    for wearable in campaign.wearables():
        worn_by_slot[str(wearable["slot"])] = str(wearable["id"])
    state.wear = list(worn_by_slot.values())
    state.badges = [
        "first-light",
        "full-evening",
        "campaign",
        "streak-3",
        "collector",
        "builder",
        "mentored",
    ]
    state.roadmap_done = [node.id for node in campaign.tech_nodes()]
    return state


def check_product(product: Path) -> None:
    """Fail before staging when a reviewed publication input is absent."""
    game = product / REQUIRED_PRODUCT_FILE
    media = product / REQUIRED_PRODUCT_DIR
    missing = []
    if not game.is_file():
        missing.append(REQUIRED_PRODUCT_FILE)
    if not media.is_dir():
        missing.append(f"{REQUIRED_PRODUCT_DIR}/")
    else:
        missing.extend(
            f"{REQUIRED_PRODUCT_DIR}/{name}"
            for name in REQUIRED_MEDIA_FILES
            if not (media / name).is_file()
        )
    if missing:
        raise RegenerationError(
            "product is missing required publication input: " + ", ".join(missing)
        )


def product_fingerprint(product: Path) -> str:
    """Hash the inputs that can change the published camp's generated files."""
    digest = hashlib.sha256()
    for relative in PRODUCT_INPUTS:
        source = product / relative
        paths = sorted(source.rglob("*")) if source.is_dir() else [source]
        for path in paths:
            if not path.is_file() or COPY_EXCLUDES & set(path.parts):
                continue
            digest.update(str(path.relative_to(product)).encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def _same_source(camp: Path, fingerprint: str) -> bool:
    marker = camp / SOURCE_MARKER
    if not marker.is_file() or _git(camp, "log", "-1", "--format=%s") != COMMIT_MESSAGE:
        return False
    try:
        return json.loads(marker.read_text()) == {
            "version": 1,
            "product": fingerprint,
        }
    except (OSError, ValueError):
        return False


def _copy_current_product(stage: Path, product: Path) -> None:
    """Add the built game and reviewed pictures a played camp publishes."""
    check_product(product)
    for relative in (REQUIRED_PRODUCT_FILE, "game/news.json"):
        source = product / relative
        if source.is_file():
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    source_media = product / REQUIRED_PRODUCT_DIR
    shutil.copytree(source_media, stage / REQUIRED_PRODUCT_DIR, dirs_exist_ok=True)


def prepare_stage(
    stage: Path, product: Path = ROOT, *, published_camp: Path | None = None
) -> None:
    """Build the complete camp away from the checkout that will receive it."""
    check_product(product)
    env = dict(os.environ, VIBE_HOME=str(stage))
    _run(
        [sys.executable, "-m", "vibemap.cli", "new", str(stage), "--name", "Tom"],
        cwd=product,
        env=env,
    )
    script_everything(stage, product)
    if published_camp is not None:
        mcp = stage / "workspace/artifacts/bridge/mcp.json"
        config = json.loads(mcp.read_text())
        config["mcpServers"]["camp-scores"]["args"][1] = str(published_camp)
        mcp.write_text(json.dumps(config, indent=2) + "\n")
    played_state(product).save(stage / ".vibe" / "state.json")
    _copy_current_product(stage, product)


def _ignore(_directory: str, names: list[str]) -> set[str]:
    return set(names) & COPY_EXCLUDES


def _copied_from_stage(path: Path, stage: Path) -> bool:
    return not (COPY_EXCLUDES & set(path.relative_to(stage).parts))


def _same_file(source: Path, target: Path) -> bool:
    """An ignored target may remain only when staging would leave it unchanged."""
    if source.is_symlink() or target.is_symlink():
        return (
            source.is_symlink()
            and target.is_symlink()
            and os.readlink(source) == os.readlink(target)
        )
    return (
        source.is_file()
        and target.is_file()
        and filecmp.cmp(source, target, shallow=False)
    )


def install(stage: Path, camp: Path) -> bool:
    """Replace tracked camp content from a complete stage and commit it locally."""
    camp = camp.resolve()
    branch, origin, push_url = check_target(camp)
    original = _git(camp, "rev-parse", "HEAD")
    tracked = set(_git(camp, "ls-files", "-z").split("\0")) - {""}
    ignored = set(
        _git(
            camp,
            "ls-files",
            "-z",
            "--others",
            "--ignored",
            "--exclude-standard",
        ).split("\0")
    ) - {""}
    stage_files = sorted(
        str(path.relative_to(stage))
        for path in stage.rglob("*")
        if (path.is_file() or path.is_symlink()) and _copied_from_stage(path, stage)
    )
    # A new release may omit older learner artifacts, vault notes or media.
    # Keep those tracked records unless the stage explicitly replaces them.
    retained_tracked = {
        relative
        for relative in tracked - set(stage_files)
        if relative.startswith(RETAINED_PREFIXES)
    }
    scores = "workspace/data/scores.csv"
    if scores in tracked:
        if scores in stage_files and not _same_file(stage / scores, camp / scores):
            raise RegenerationError(f"{camp} would overwrite tracked {scores}")
        retained_tracked.add(scores)
    preserved = ignored & set(stage_files)
    overlaps = sorted(
        relative
        for relative in preserved
        if not _same_file(stage / relative, camp / relative)
    )
    if overlaps:
        names = ", ".join(overlaps[:3])
        raise RegenerationError(
            f"{camp} has ignored data that regeneration would replace: {names}"
        )
    new_directories = sorted(
        (
            path.relative_to(stage)
            for path in stage.rglob("*")
            if path.is_dir()
            and _copied_from_stage(path, stage)
            and not (camp / path.relative_to(stage)).exists()
        ),
        key=lambda path: len(path.parts),
        reverse=True,
    )

    def keep_ignored(directory: str, names: list[str]) -> set[str]:
        parent = Path(directory).relative_to(stage)
        return _ignore(directory, names) | {
            name for name in names if str(parent / name) in preserved | retained_tracked
        }

    try:
        for relative in tracked - retained_tracked:
            path = camp / relative
            if path.is_file() or path.is_symlink():
                path.unlink()
        shutil.copytree(stage, camp, dirs_exist_ok=True, ignore=keep_ignored)

        if _git(camp, "branch", "--show-current") != branch:
            raise RegenerationError("the regeneration changed the target branch")
        if _remote_urls(camp) != origin:
            raise RegenerationError("the regeneration changed the target origin")
        if _remote_urls(camp, push=True) != push_url:
            raise RegenerationError("the regeneration changed the target push URL")
        still_ignored = set(
            _git(
                camp,
                "ls-files",
                "-z",
                "--others",
                "--ignored",
                "--exclude-standard",
            ).split("\0")
        ) - {""}
        exposed = sorted(ignored - still_ignored)
        if exposed:
            names = ", ".join(exposed[:3])
            raise RegenerationError(
                f"regeneration would expose ignored target data: {names}"
            )

        _git(camp, "add", "-A")
        state_path = camp / ".vibe" / "state.json"
        if state_path.is_file():
            _git(camp, "add", "-f", ".vibe/state.json")
        if (camp / SOURCE_MARKER).is_file():
            _git(camp, "add", "-f", str(SOURCE_MARKER))
        if not _git(camp, "status", "--porcelain"):
            return False
        _git(
            camp,
            "-c",
            "user.name=vibe regeneration",
            "-c",
            "user.email=actions@users.noreply.github.com",
            "commit",
            "-qm",
            COMMIT_MESSAGE,
        )
        return True
    except BaseException:
        # The target was proven clean before mutation, so HEAD is a complete
        # rollback point. Remove ignored files created from the stage explicitly;
        # git clean deliberately leaves unrelated ignored learner data alone.
        _git(camp, "reset", "--hard", original)
        for relative in stage_files:
            path = camp / relative
            if (
                relative not in tracked
                and relative not in ignored
                and (path.is_file() or path.is_symlink())
            ):
                path.unlink()
        _git(camp, "clean", "-fd")
        for relative in new_directories:
            try:
                (camp / relative).rmdir()
            except OSError:
                pass
        raise


def push_reviewed(camp: Path) -> str:
    """Push the clean commit already selected by the maintainer."""
    camp = camp.resolve()
    branch, _, _ = check_target(camp)
    reviewed = _git(camp, "rev-parse", "HEAD")
    _git(camp, "push", "origin", f"{reviewed}:refs/heads/{branch}")
    if _git(camp, "rev-parse", "HEAD") != reviewed:
        raise RegenerationError("the reviewed commit changed while it was pushed")
    return branch


def regenerate(
    camp: Path,
    product: Path = ROOT,
    *,
    dry_run: bool,
    push: bool,
) -> str:
    """Regenerate one named checkout after all safety checks pass."""
    camp = camp.resolve()
    product = product.resolve()
    branch, _, _ = check_target(camp)
    check_product(product)
    fingerprint = product_fingerprint(product)
    if dry_run:
        action = "push its reviewed commit" if push else "regenerate without pushing"
        return f"would {action}: {camp} on {branch}"
    if push:
        branch = push_reviewed(camp)
        return f"pushed reviewed commit: {camp} on {branch}"
    if _same_source(camp, fingerprint):
        return f"already current: {camp} on {branch} without pushing"
    with tempfile.TemporaryDirectory(prefix="vibe-played-") as temporary:
        stage = Path(temporary) / "camp"
        prepare_stage(stage, product, published_camp=camp)
        (stage / SOURCE_MARKER).write_text(
            json.dumps({"version": 1, "product": fingerprint}, indent=2) + "\n"
        )
        changed = install(stage, camp)
    action = "regenerated" if changed else "already current"
    return f"{action}: {camp} on {branch} without pushing"


def main() -> None:
    parser = argparse.ArgumentParser(prog="regen_played")
    parser.add_argument("--camp", required=True, help="local vibe-map-played checkout")
    parser.add_argument(
        "--product", default=str(ROOT), help="vibe-map product checkout to publish"
    )
    parser.add_argument("--dry-run", action="store_true", help="check and print only")
    parser.add_argument(
        "--push", action="store_true", help="push the resulting commit to origin"
    )
    args = parser.parse_args()
    try:
        print(
            regenerate(
                Path(args.camp),
                Path(args.product),
                dry_run=args.dry_run,
                push=args.push,
            )
        )
    except RegenerationError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
