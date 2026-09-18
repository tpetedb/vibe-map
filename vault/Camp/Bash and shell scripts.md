---
title: "Bash and shell scripts"
date: 2026-09-16
tags: [tech, shell]
generated: 4d1662cb3ff0
---
# Bash and shell scripts

Bash is the language the terminal speaks. A shell script is a text file of commands; pipes (|) chain small tools into big ones. This is also what hooks and setup scripts are written in.

**History.** The Bourne shell shipped with Seventh Edition Unix in January 1979; bash (the Bourne-again shell, written by Brian Fox) went into beta as the GNU replacement in June 1989. macOS switched its default login shell to zsh with macOS 10.15 Catalina in 2019; zsh is bash-compatible for everything you will meet tonight.

**Try in five minutes.** cat workspace/data/scores.csv | sort -t, -k3 -n | tail -3 (the three highest scores, no code written).

- Docs: [Bash Guide (Greg's wiki)](https://mywiki.wooledge.org/BashGuide), [ShellCheck, lint your scripts](https://www.shellcheck.net), [Source: GNU Bash manual, What is Bash?](https://www.gnu.org/software/bash/manual/html_node/What-is-Bash_003f.html), [Source: TUHS, Seventh Edition Unix (January 1979)](https://www.tuhs.org/cgi-bin/utree.pl?file=V7), [Source: GNU's Bulletin, June 1989](https://www.gnu.org/bulletins/bull7.html), [Source: Apple, Use zsh as the default shell on your Mac](https://support.apple.com/en-us/102360)
- Unlocks: [[zsh and your shell config]], [[Dotfiles]], [[Justfiles and task running]], [[Docker and containers]], [[Hooks]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
