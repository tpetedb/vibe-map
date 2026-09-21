"""Summarise workspace/data/scores.csv and draw a tiny bar chart in the terminal.

New concept in this file: a dictionary comprehension builds {player: [scores]}
in one line, then max()/statistics.mean() summarise each list.
Run from the camp root: python3 workspace/python/scores.py
"""

import csv
import statistics
from pathlib import Path


def main():
    rows = list(csv.DictReader(open(Path(__file__).parents[1] / "data" / "scores.csv")))
    players = sorted({r["player"] for r in rows})
    scores = {p: [int(r["score"]) for r in rows if r["player"] == p] for p in players}
    top = max(int(r["score"]) for r in rows)
    print(f"{'player':<10}{'runs':>5}{'best':>6}{'mean':>7}  chart")
    for p in players:
        s = scores[p]
        bar = "#" * int(30 * max(s) / top)
        print(f"{p:<10}{len(s):>5}{max(s):>6}{statistics.mean(s):>7.1f}  {bar}")


if __name__ == "__main__":
    main()
