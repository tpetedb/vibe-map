---
title: "tmux, sessions that survive"
date: 2026-09-24
tags: [tech, shell]
generated: db1bdb944620
---
# tmux, sessions that survive

tmux is a terminal multiplexer: several terminals inside one screen, split into panes, and a session that keeps running when you close the window or lose the connection. You detach, go home, and attach again to find everything where you left it. Reach for it on any remote machine where a long job must not die with your SSH connection, and on your own laptop when one window is not enough; it runs on OpenBSD, FreeBSD, NetBSD, Linux, macOS and Solaris. And for an agent: a session made with tmux new-session -d is not attached to your terminal, and tmux has-session -t NAME exits 0 when the session exists and 1 when it does not, so a script can ask before it starts a second one.

**History.** The tmux manual defines it as "a terminal multiplexer: it enables a number of terminals to be created, accessed, and controlled from a single screen", and one that "may be detached from a screen and continue running in the background, then later reattached." A session is a collection of pseudo terminals; each session has one or more windows, and a window may be split into rectangular panes. Each session "is persistent and will survive accidental disconnection (such as ssh(1) connection timeout) or intentional detaching (with the 'C-b d' key strokes)", and tmux attach brings it back. The configuration file, ~/.tmux.conf by default, is "a set of tmux commands which are executed in sequence when the server is first started", and the manual's own example binds R to source-file ~/.tmux.conf to reload it. OpenBSD 4.6, released on October 18, 2009, imported the tmux(1) terminal multiplexer, replacing window(1).

**Try in five minutes.** tmux new-session -d -s camp, then tmux list-sessions > sessions.txt, then tmux kill-session -t camp. Write a tmux.conf with bind-key R source-file ~/.tmux.conf.

- Docs: [tmux(1), the OpenBSD manual page](https://man.openbsd.org/tmux.1), [tmux on GitHub, the README: what it is and where it runs](https://github.com/tmux/tmux), [Source: OpenBSD 4.6 release notes](https://www.openbsd.org/46.html)
- Unlocks: [[Networking from the shell]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
