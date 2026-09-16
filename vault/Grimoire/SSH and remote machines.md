---
title: "SSH and remote machines"
date: 2026-09-16
tags: [tech, castle]
---
# SSH and remote machines

SSH is an encrypted terminal to another computer. ssh user@host gives you a shell on a server; the same key pair authenticates you to GitHub. Once you can SSH somewhere, everything in the Dark Age works there too, including running an agent on a remote box.

**History.** SSH was written by Tatu Ylonen at Helsinki University of Technology and published in July 1995, after a password sniffer was found on the university network; OpenSSH (first shipped with OpenBSD in December 1999) is what every Mac and Linux ships.

**Try in five minutes.** ssh-keygen -t ed25519, then gh ssh-key add ~/.ssh/id_ed25519.pub, then ssh -T git@github.com.

- Docs: [OpenSSH manual](https://www.openssh.com/manual.html), [GitHub: connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh), [Source: SSH Academy, SSH history](https://www.ssh.com/academy/ssh), [Source: Ylonen, SSH: Secure Login Connections over the Internet (USENIX 1996)](https://www.usenix.org/legacy/publications/library/proceedings/sec96/full_papers/ylonen/), [Source: OpenSSH project history](https://www.openssh.org/history.html)
- Unlocks: [[Cloud and servers]], [[Docker and containers]]
- Age: Castle Age · Level: Medior

<!-- generated from tools/tech.py; edit there -->

Back to [[Tech tree]]

#tech #castle
