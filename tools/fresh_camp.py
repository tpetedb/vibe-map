"""A fresh camp, end to end: vibe new, the checks that refuse, then the checks
that pass, then the progress code out and back in.

This is the only test that runs the command a learner actually installs. It
never imports vibemap; it starts a process, the way a camp does, so a packaging
mistake (a missing template file, package data left out of the wheel) fails
here and nowhere else.

    uv run python tools/fresh_camp.py                     the `vibe` on PATH
    uv run python tools/fresh_camp.py --vibe="uv run vibe"
    uv run python tools/fresh_camp.py --keep              leave the camps behind
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

# The journey configuration is what makes a folder a camp.
CAMP_MARKER = "config/camp.toml"

# Workstream 1 wants a page of the learner's own with a script and a score in
# it; workstream 3 wants three rows of scores, one query and one script. These
# are the smallest artefacts that satisfy vibemap/quests.py, not good work.
GAME_HTML = """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Coffee clicker</title></head>
  <body>
    <canvas id="board" width="320" height="240"></canvas>
    <p>score: <span id="score">0</span></p>
    <script>
      let score = 0;
      document.getElementById('board').onclick = () => {
        score += 1;
        document.getElementById('score').textContent = score;
      };
    </script>
    <!-- PAD -->
  </body>
</html>
""".replace("PAD", "padding so the check sees a page, not a stub. " * 20)

SCORES_CSV = """played_at,player,score,duration_s
2026-09-15T20:10:00,Lotte,120,45
2026-09-15T20:14:00,Lotte,180,51
2026-09-15T20:20:00,Tom,90,38
"""

TOP_RUNS_SQL = """-- Which runs scored highest, and who owns them?
select player,
       score,
       duration_s
from read_csv_auto('workspace/data/scores.csv')
order by score desc
limit 5;
"""

SCORES_PY = '''"""Print the best run per player."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

CSV = Path(__file__).resolve().parents[1] / "data" / "scores.csv"


def best() -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    with CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["player"]] = max(out[row["player"]], int(row["score"]))
    return dict(out)


if __name__ == "__main__":
    for player, score in sorted(best().items()):
        print(f"{player}: {score}")
'''


class CampError(AssertionError):
    """A step of the fresh-camp run did not do what a learner would see."""


@dataclass(slots=True)
class Camp:
    """One camp folder and the vibe command that drives it."""

    vibe: Sequence[str]
    path: Path
    log: list[str] = field(default_factory=list)

    def run(self, *args: str, refuses: bool = False) -> str:
        """Run vibe in this camp and return its output, failing loudly.

        A check that refuses exits 1, so REFUSES says which code this step
        expects; any other code is a broken run rather than an undone task.
        """
        env = dict(os.environ, VIBE_HOME=str(self.path), NO_COLOR="1", COLUMNS="200")
        done = subprocess.run(
            [*self.vibe, *args],
            cwd=self.path,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        self.log.append(" ".join(args))
        want = 1 if refuses else 0
        if done.returncode != want:
            raise CampError(
                f"vibe {' '.join(args)} exited {done.returncode}, expected {want}"
                f"\n{done.stdout}\n{done.stderr}"
            )
        return done.stdout

    def done(self) -> dict[str, list[int]]:
        """What the camp counts as done, from the command a script would use."""
        return json.loads(self.run("status", "--json"))["done"]

    def write(self, rel: str, text: str) -> None:
        target = self.path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def _new_camp(vibe: Sequence[str], where: Path, who: str) -> Camp:
    """`vibe new` into an empty folder, the way a learner starts."""
    env = dict(os.environ, NO_COLOR="1")
    done = subprocess.run(
        [*vibe, "new", "--name", who],
        cwd=where,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if done.returncode != 0:
        raise CampError(
            f"vibe new exited {done.returncode}\n{done.stdout}{done.stderr}"
        )
    camps = [p for p in where.iterdir() if p.is_dir() and (p / CAMP_MARKER).exists()]
    if len(camps) != 1:
        raise CampError(f"expected one camp in {where}, found {camps}")
    return Camp(vibe, camps[0])


def run_fresh_camp(vibe: Sequence[str], where: Path) -> dict[str, object]:
    """The whole journey in one camp, plus a second camp for the import.

    Returns a summary; raises CampError on the first step that misbehaves.
    """
    camp = _new_camp(vibe, where, "Lotte")
    for rel in (CAMP_MARKER, "vault/Camp/Tonight.md", "workspace/README.md"):
        if not (camp.path / rel).exists():
            raise CampError(f"a fresh camp has no {rel}")

    # An empty camp is not done. Every one of these checks looks at something
    # the learner has not built yet, so none of them may claim a stop.
    camp.run("check", "1", refuses=True)
    camp.run("check", "3", refuses=True)
    camp.run("check", "--world", "winter", "1", refuses=True)
    empty = camp.done()
    if any(empty.values()):
        raise CampError(f"an empty camp claimed stops: {empty}")

    camp.write("workspace/game/index.html", GAME_HTML)
    camp.write("workspace/data/scores.csv", SCORES_CSV)
    camp.write("workspace/sql/top_runs.sql", TOP_RUNS_SQL)
    camp.write("workspace/python/scores.py", SCORES_PY)

    camp.run("check", "1")
    camp.run("check", "3")
    played = camp.done()
    if sorted(played.get("campus", [])) != [1, 3]:
        raise CampError(f"workstreams 1 and 3 did not pass: {played}")

    # The note check still refuses: nothing was written in the learner's words.
    camp.run("check", "--world", "winter", "1", refuses=True)
    if camp.done().get("winter"):
        raise CampError("the winter note check passed without a note")

    # A camp has no checkout, so this is where a fork source left out of the
    # wheel would show up and nowhere else.
    camp.run("fork")
    if not (camp.path / "workspace/forks/vibe-map/src/config/00-config.js").exists():
        raise CampError("vibe fork wrote no src/config")
    camp.run("check", "--fork", "exists")

    code = camp.run("export").strip().splitlines()[-1].strip()
    if not code:
        raise CampError("vibe export printed no code")

    second = where / "second"
    second.mkdir()
    other = _new_camp(vibe, second, "Tom")
    other.run("import", code)
    imported = other.done()
    if sorted(imported.get("campus", [])) != [1, 3]:
        raise CampError(f"the code did not carry the stops: {imported}")

    camp.run("vault", "lint")
    return {
        "camp": str(camp.path),
        "code": code,
        "done": played,
        "imported": imported,
        "steps": camp.log + other.log,
    }


def main() -> None:
    args = sys.argv[1:]
    vibe = shlex.split(
        next(
            (a.split("=", 1)[1] for a in args if a.startswith("--vibe=")),
            "vibe",
        )
    )
    keep = "--keep" in args
    where = Path(tempfile.mkdtemp(prefix="vibe-fresh-camp-"))
    try:
        result = run_fresh_camp(vibe, where)
    except BaseException:
        print(f"the camps are left in {where} to look at")
        raise
    if keep:
        print(f"camps left in {where}")
    else:
        shutil.rmtree(where, ignore_errors=True)
    for step in result["steps"]:
        print(f"vibe {step}")
    print(f"done: {json.dumps(result['done'])}")
    print(f"code: {result['code'][:24]}...")


if __name__ == "__main__":
    main()
