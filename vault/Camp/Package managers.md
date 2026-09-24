---
title: "Package managers"
date: 2026-09-24
tags: [tech, shell]
generated: 0ca341017300
---
# Package managers

A package manager installs a program together with the packages it depends on, from the sources it is configured with, and upgrades them later with one command. Debian uses APT (apt at the keyboard, apt-get in scripts), RPM-based distributions use DNF, and on a Mac the comparison is Homebrew, which also runs on Linux and WSL. Reach for this topic whenever a tutorial says "install X": the command depends on which system you are on, and a list of packages in a file is how you install the same set twice. And for an agent: in a script or a Dockerfile use apt-get, not apt, because apt "may change behavior between versions"; on a Mac write the tools into a Brewfile and run brew bundle.

**History.** Debian 2.1, released on March 9th, 1999, introduced apt, "a new package management interface" that, in the project's own history, "established a new paradigm for package acquisition and installation on Open Source operating systems." In apt, update "is used to download package information from all configured sources", and install, remove and upgrade act on that information. The apt manual says the command "is designed as an end-user tool and it may change behavior between versions", so scripts should prefer apt-get and apt-cache, which "keep backward compatibility as much as possible". DNF "is the next upcoming major version of YUM, a package manager for RPM-based Linux distributions", and dnf install "makes sure that the given packages and their dependencies are installed on the system." Homebrew installs command-line tools and applications "across macOS, Linux and WSL", each package into its own keg inside the Cellar, and a Brewfile gives it "a declarative interface for installing/upgrading packages".

**Try in five minutes.** Write a Brewfile with the line brew "jq" and run brew bundle check. Then write install-debian.sh with apt-get update and apt-get install -y jq, the way a Dockerfile would install the same tool on Debian.

- Docs: [Debian, apt(8) manual page](https://manpages.debian.org/bookworm/apt/apt.8.en.html), [DNF, command reference](https://dnf.readthedocs.io/en/latest/command_ref.html), [Homebrew, the package manager for macOS and Linux](https://brew.sh/), [Homebrew, Homebrew Bundle, brew bundle and Brewfile](https://docs.brew.sh/Brew-Bundle-and-Brewfile), [Source: A Brief History of Debian, Debian Releases](https://www.debian.org/doc/manuals/project-history/releases.en.html)
- Unlocks: [[systemd, services and the journal]]
- Shelf: Terminal and shell · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
