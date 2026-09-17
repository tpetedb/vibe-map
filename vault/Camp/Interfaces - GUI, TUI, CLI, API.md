---
title: "Interfaces: GUI, TUI, CLI, API"
date: 2026-09-17
tags: [tech, shell]
generated: 56d08d225fde
---
# Interfaces: GUI, TUI, CLI, API

Four ways to talk to a program. A CLI takes a command and flags and prints text (`vibe status`, git, uv). A TUI draws a screen inside the terminal you can move around in (`just start`, htop, the Claude Code chat). A GUI is windows and a pointer (Obsidian, Zed, the browser game). An API is for programs, not people: HTTP endpoints that return JSON (GitHub's REST API), or a protocol two programs agree on, such as MCP between an agent and a tool server and ACP between an editor and an agent. One program can have all four: Obsidian has a GUI, a URI scheme and a CLI.

**History.** The command line came with time-sharing systems and Unix (1969); full-screen terminal programs followed once terminals could address the screen, with vi (1976) and the curses library (1978); the graphical desktop was prototyped on the Xerox Alto (1973) and sold with the Macintosh (1984); REST named the web's API style in Roy Fielding's dissertation (2000); MCP was published by Anthropic on 25 November 2024 and ACP by Zed in August 2025.

**Try in five minutes.** Run the same thing four ways: `uv run vibe status` (CLI), `just start` then Campaign map (TUI), the Roadmap button in game/vibe-map.html (GUI), and `gh api repos/tpetedb/vibe-map` (API). Notice what each one is good at.

- Docs: [Textual, TUIs in Python](https://textual.textualize.io/), [click, CLIs in Python](https://click.palletsprojects.com/), [GitHub REST API](https://docs.github.com/en/rest), [Model Context Protocol](https://modelcontextprotocol.io/), [Agent Client Protocol](https://agentclientprotocol.com/), [Source: Roy Fielding, Architectural Styles and the Design of Network-based Software Architectures (2000)](https://ics.uci.edu/~fielding/pubs/dissertation/top.htm), [Source: Anthropic, Introducing the Model Context Protocol (25 November 2024)](https://www.anthropic.com/news/model-context-protocol), [Source: Zed, Bring your own agent to Zed (ACP, August 2025)](https://zed.dev/blog/bring-your-own-agent-to-zed), [Source: Wikipedia, Text-based user interface (curses, 1978)](https://en.wikipedia.org/wiki/Text-based_user_interface), [Source: Wikipedia, Xerox Alto (1973) and Macintosh (1984)](https://en.wikipedia.org/wiki/Xerox_Alto)
- Unlocks: [[Unix and the terminal]], [[MCP (Model Context Protocol)]], [[Building and consuming APIs]]
- Shelf: Terminal and shell · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
