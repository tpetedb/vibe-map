---
title: "Networking from the shell"
date: 2026-09-24
tags: [tech, shell]
generated: 396670da4e9f
---
# Networking from the shell

Most network questions have a one-line answer in the terminal: is something listening on this port, and what does it say when I ask. curl asks, and curl -I asks for the headers only; ss on Linux and lsof on a Mac or on Linux show which process holds which socket. Reach for this topic when a local server "does not work", before you open a browser: start it, ask it with curl, and look at the port it is really on. And for an agent: prove a server is up with curl -sI against the exact address and port, and find what holds a port with lsof -nP -iTCP:PORT -sTCP:LISTEN (or ss -ltnp on Linux) instead of guessing.

**History.** curl began as HttpGet, which Daniel Stenberg extended in 1996, became urlget in 1997, and was renamed once more when curl 4 was released on March 20, 1998. Its manual describes it as "a tool for transferring data from or to a server using URLs", and -I, --head fetches the headers only, using the HTTP HEAD command. ss "is used to dump socket statistics"; -l shows only listening sockets, -t TCP sockets, -n exact numbers instead of service names and -p the processes using them. lsof lists information about files opened by processes, a network socket among them, and -iTCP -sTCP:LISTEN lists only network files in the TCP LISTEN state. Python's http.server listens on port 8000 by default, --bind 127.0.0.1 keeps it to localhost, and its own documentation warns that it "is not recommended for production".

**Try in five minutes.** python3 -m http.server 8765 --bind 127.0.0.1 in one terminal. In another: curl -sI http://127.0.0.1:8765/ > head.txt, then lsof -nP -iTCP:8765 -sTCP:LISTEN > port.txt (or ss -ltnp > port.txt on Linux). Stop the server with Ctrl-C.

- Docs: [curl, the curl man page](https://curl.se/docs/manpage.html), [ss(8), another utility to investigate sockets](https://man7.org/linux/man-pages/man8/ss.8.html), [lsof(8), list open files](https://man7.org/linux/man-pages/man8/lsof.8.html), [lsof-org, lsof on GitHub: the dialects it maintains, Linux and Darwin among them](https://github.com/lsof-org/lsof), [Python, http.server and its command-line interface](https://docs.python.org/3/library/http.server.html), [Source: curl, History of curl](https://curl.se/docs/history.html)
- Unlocks: [[systemd, services and the journal]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
