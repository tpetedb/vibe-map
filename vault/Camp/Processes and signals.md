---
title: "Processes and signals"
date: 2026-09-24
tags: [tech, shell]
generated: a7cb3b213421
---
# Processes and signals

Every command you run is a process: the shell starts it, waits for it, and reads its exit status when it ends. A signal is how you talk to a process that is already running, and kill is the command that sends one, SIGTERM when you name no other. Reach for this topic when a server will not stop, when a job has to run in the background, or when a script has to tell "it failed" apart from "somebody stopped it". And for an agent: stop a process with SIGTERM first and give it the chance to clean up. SIGKILL cannot be caught, blocked or ignored, so nothing the program meant to do on the way out will happen.

**History.** Dennis Ritchie's history of Unix sums up how a shell runs a command: it reads the line, creates a child process by fork, the child uses exec to call in the command from a file, and the parent uses wait until the child terminates by calling exit. In PDP-7 Unix processes existed very early, precisely two of them, one for each of the two terminals, and fork, wait and exec came later. The kill utility "shall send a signal to the process or processes specified by each pid operand", and sends SIGTERM if no signal is named. On Linux, SIGINT (2) is the interrupt from the keyboard, SIGTERM (15) the termination signal and SIGKILL (9) the kill signal, and "The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored." In bash, "When a command terminates on a fatal signal N, bash uses the value of 128+N as the exit status", which is how a script can tell a failure from a stop.

**Try in five minutes.** bash -c 'sleep 30 & pid=$!; kill -TERM "$pid"; wait "$pid"; echo "exit: $?"' > signals.txt, then cat signals.txt: 143 is 128 plus 15, the number of SIGTERM.

- Docs: [signal(7), overview of signals](https://man7.org/linux/man-pages/man7/signal.7.html), [POSIX.1-2024, kill: terminate or signal processes](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/kill.html), [GNU bash manual page, EXIT STATUS (Debian)](https://manpages.debian.org/bookworm/bash/bash.1.en.html), [POSIX.1-2024, wait: await process completion](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/wait.html), [Source: Ritchie, The Evolution of the Unix Time-sharing System](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/hist.html)
- Unlocks: [[systemd, services and the journal]], [[tmux, sessions that survive]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
