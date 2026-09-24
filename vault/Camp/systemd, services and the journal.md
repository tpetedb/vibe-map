---
title: "systemd, services and the journal"
date: 2026-09-24
tags: [tech, shell]
generated: 0ac8f3ea32ee
---
# systemd, services and the journal

On a Linux machine that runs systemd, a long-running program is a service, and systemd is what starts it and supervises it. You describe the service once in a small unit file, an ini-style text file with a [Unit], a [Service] and an [Install] section, and journalctl reads what it printed. Reach for this topic when a web app, a bot or a worker on a server has to keep running after you log out. And for an agent: write the unit file, check it with systemd-analyze verify before anyone enables it, and read failures with journalctl -u NAME rather than guessing.

**History.** In April 2010 Lennart Poettering announced systemd in the blog post Rethinking PID 1, as "a (still experimental) init system" that "starts up and supervises the entire system" and "is based around the notion of units." A unit file is "a plain text ini-style file" that describes a service, a socket, a timer, a mount point and more, and a file whose name ends in .service "encodes information about a process controlled and supervised by systemd." ExecStart= gives the commands run when the service starts, and with no Type= set, Type=simple is assumed. In the [Install] section, WantedBy=multi-user.target is what systemctl enable reads: it creates a symlink in /etc/systemd/system/multi-user.target.wants/ that tells systemd to pull the unit in when starting multi-user.target. journalctl prints "the log entries stored in the journal", and journalctl -u shows the messages of one unit.

**Try in five minutes.** Write hello.service with [Unit] Description=Hello, [Service] ExecStart=/usr/bin/env echo hello, and [Install] WantedBy=multi-user.target. On a Linux machine with systemd, systemd-analyze verify ./hello.service loads the file and prints warnings if it finds errors.

- Docs: [systemd.unit(5), unit configuration](https://man7.org/linux/man-pages/man5/systemd.unit.5.html), [systemd.service(5), service unit configuration](https://man7.org/linux/man-pages/man5/systemd.service.5.html), [journalctl(1), print log entries from the systemd journal](https://man7.org/linux/man-pages/man1/journalctl.1.html), [systemd-analyze(1), analyze and debug the system manager](https://man7.org/linux/man-pages/man1/systemd-analyze.1.html), [Source: Lennart Poettering, Rethinking PID 1 (April 2010)](https://0pointer.de/blog/projects/systemd.html)
- Unlocks: [[cron and timers]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
