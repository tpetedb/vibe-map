# Source

Issue #86 (Z4 Topic pack: Linux and the shell). docs/TOPICS.md is how to write a topic and an origin; `just new-topic` or tools/new_topic.py scaffolds a pack; vibemap/data/topics/core/unix.toml and bash.toml are worked examples.

# What

A new pack `linux` (shelf shell): kernel and distros, filesystem and permissions, processes and signals, systemd, package managers, shell scripting, text tools (grep, sed, awk), cron, tmux, networking basics, and WSL and macOS gotchas. SSH stays in core. Each topic: the five-sentence model, a hands-on under 20 minutes with a deterministic offline check of a kind that already exists, 3 to 6 sources you opened, one primary origin at a place already on main (`uv run vibe places`) or an abstract one. A wished-for place goes to issue #168 as a wish, never a new place file.
