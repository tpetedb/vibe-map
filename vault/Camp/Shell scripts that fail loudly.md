---
title: "Shell scripts that fail loudly"
date: 2026-09-24
tags: [tech, shell]
generated: 9a37c384ba55
---
# Shell scripts that fail loudly

A shell script keeps running after a command fails unless you tell it not to. Three options change it: set -e stops at the first failing command, set -u refuses a variable that was never set, and set -o pipefail makes a pipeline fail when any command in it fails. Add quoting, so "$@" hands every argument through whole, and a trap that cleans up on EXIT, and a script says when it goes wrong. Reach for this the moment a script does more than one thing, and run ShellCheck over it. And for an agent: start every bash script with set -euo pipefail, quote every expansion, and run shellcheck on it before calling it done.

**History.** POSIX.1-2024 describes -e this way: "when any command fails (for any of the reasons listed in 2.8.1 Consequences of Shell Errors or by returning an exit status greater than zero), the shell immediately shall exit", with exceptions such as the condition of an if or any command of an AND-OR list other than the last. With -u, expanding an unset parameter makes the shell "write a message to standard error and the expansion shall fail". The pipefail option was added in this edition of the standard: it derives the exit status of a pipeline "from the exit statuses of all of the commands in the pipeline, not just the last (rightmost) command". A trap on EXIT runs "when the shell terminates normally (exits)", and the value of $? after the trap is the value it had before. ShellCheck is a GPLv3 tool that gives warnings and suggestions for bash and sh scripts, and the gallery of bad code in its README opens with quoting, an unquoted variable and an unquoted $@ among the examples.

**Try in five minutes.** Write safe.sh with #!/usr/bin/env bash, set -euo pipefail, trap 'echo "cleanup ran" >&2' EXIT, a function greet() { printf 'hello, %s\n' "$1"; } and a loop for name in "$@"; do greet "$name"; done. Run bash safe.sh "Ada Lovelace" > out.txt, then shellcheck safe.sh.

- Docs: [POSIX.1-2024, Shell Command Language (set, trap, pipelines, exit status)](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html), [ShellCheck, a shell script static analysis tool](https://github.com/koalaman/shellcheck), [GNU bash manual page, the set builtin and EXIT STATUS (Debian)](https://manpages.debian.org/bookworm/bash/bash.1.en.html)
- Unlocks: [[cron and timers]], [[systemd, services and the journal]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
