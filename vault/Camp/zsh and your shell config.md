---
title: "zsh and your shell config"
date: 2026-09-16
tags: [tech, shell]
---
# zsh and your shell config

~/.zshrc runs every time you open a terminal: it sets PATH (the folders where commands are looked up), aliases (short names for long commands), the prompt, and small functions. zsh is the macOS default; it is bash-compatible for daily use and adds better completion and globbing. oh-my-zsh bundles plugins and themes; starship is a fast prompt that works in any shell. Keep .zshrc in your dotfiles repo so a new machine is one clone away.

**History.** zsh was written by Paul Falstad while a student at Princeton, around 1990. Apple made it the default login shell with macOS 10.15 Catalina in October 2019, replacing bash.

**Try in five minutes.** source scripts/vibe.zsh then g status.

- Docs: [zsh manual](https://zsh.sourceforge.io/Doc/), [oh-my-zsh](https://ohmyz.sh), [starship prompt](https://starship.rs), [Source: zsh FAQ, 1.1 What is it?](https://zsh.sourceforge.io/FAQ/zshfaq01.html), [Source: Apple, Use zsh as the default shell on your Mac](https://support.apple.com/en-us/102360), [Source: Apple newsroom, macOS Catalina is available today (October 2019)](https://www.apple.com/newsroom/2019/10/macos-catalina-is-available-today/)
- Unlocks: [[Dotfiles]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
