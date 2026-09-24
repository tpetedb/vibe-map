---
title: "Linux, the kernel and the distributions"
date: 2026-09-24
tags: [tech, shell]
generated: 477da8a3a92f
---
# Linux, the kernel and the distributions

Linux is a kernel, and a kernel, in Debian's words, is "the most fundamental program on the computer and does all the basic housekeeping and lets you start other programs." An operating system is more than that: "the set of basic programs and utilities that make your computer run", which is what a distribution such as Debian puts around the kernel. Reach for this topic the first time a server, a container or a Codespace asks you which Linux you are on, because the answer is written in /etc/os-release. And for an agent: read /etc/os-release before choosing a package manager or a path. ID= is there "suitable for scripts", and ID_LIKE= names the distributions this one is related to.

**History.** In August 1991 Linus Torvalds, then a 21-year-old computer science student at the University of Helsinki, wrote to the Usenet group comp.os.minix: "I'm doing a (free) operating system (just a hobby, won't be big and professional like gnu) for 386(486) AT clones." The kernel's own README still describes Linux as "a clone of the operating system Unix, written from scratch by Linus Torvalds with assistance from a loosely-knit team of hackers across the Net", distributed under the GNU General Public License v2. A distribution is the rest of the system around it: Debian "was begun in August 1993 by Ian Murdock, as a new distribution which would be made openly, in the spirit of Linux and GNU." New kernels arrive on a steady rhythm: a merge window of about two weeks, then an -rc release about once a week, up to somewhere between -rc6 and -rc9, then the final release. A distribution says who it is in /etc/os-release, with /usr/lib/os-release as the fallback, where ID= is a lowercase name such as debian or fedora and PRETTY_NAME= is the name to show a person.

**Try in five minutes.** In a Codespace: cat /etc/os-release > os-release.txt. On a Mac with Docker: docker run --rm debian:stable-slim cat /etc/os-release > os-release.txt. Then read its ID= and PRETTY_NAME= lines.

- Docs: [The Linux kernel, Linux kernel release notes (What is Linux?)](https://docs.kernel.org/admin-guide/README.html), [The Linux kernel, How the development process works](https://docs.kernel.org/process/2.Process.html), [Debian, About Debian: operating system, kernel and distribution](https://www.debian.org/intro/about), [os-release(5), the operating system identification file](https://man7.org/linux/man-pages/man5/os-release.5.html), [Source: University of Helsinki, How did the 30-year-old Linux conquer the world?](https://www.helsinki.fi/en/news/mathematics-and-science/how-did-30-year-old-linux-conquer-world), [Source: Torvalds' 1991 Linux announcements (CMU archive)](https://www.cs.cmu.edu/~awb/linux.history.html)
- Unlocks: [[The filesystem and permissions]], [[Package managers]], [[WSL and the macOS differences]]
- Shelf: Terminal and shell · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
