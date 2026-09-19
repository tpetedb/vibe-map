- The onboarding terminal fits a small window: the launcher list scrolls and
  keeps the focused button in view, the toolbelt keeps its rows at 80x24, and a
  launcher hint wraps instead of running off the side.
- The welcome screen refuses an empty name instead of storing the placeholder,
  Enter in the name field is Continue, and a theme of your own stays selected
  and stays in `config/camp.toml` when you press Continue.
- The Terminal setup rows say "installed" as soon as a module is installed, the
  campaign map speaks the same grid language as `vibe status` (`x` checked, `i`
  claimed but not verified, `>` next, `.` to do), the Campaign status launcher
  runs the CLI directly instead of `uv run --no-sync`, and the Obsidian launcher
  opens the vault folder that `[vault] path` names.
- A tool version in the toolbelt arrives without escape codes, so btop no longer
  prints `^[[1m1.4.7^[[0m` into the table or under `NO_COLOR`.
- The companion keeps its hat on every idle frame, and `vibe pet` on a terminal
  without truecolor says why forced pixels look flat and how to get the art.
