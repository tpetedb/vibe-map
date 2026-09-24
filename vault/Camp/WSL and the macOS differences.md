---
title: "WSL and the macOS differences"
date: 2026-09-24
tags: [tech, shell]
generated: 862ee20b6e8d
---
# WSL and the macOS differences

The same command can behave differently on Linux, on a Mac and on Windows, and the differences bite in scripts that pass on one laptop and fail on the next. On Windows, WSL runs a Linux environment without a separate virtual machine or dual booting, and it is fastest when your project lives in the Linux file system rather than under /mnt/c. On a Mac the classic trap is sed -i: GNU sed takes an optional backup suffix, while the sed in Apple's own sources takes -i extension, an option its manual calls a non-standard FreeBSD extension. Reach for this topic the first time a teammate says "works on my machine" about a shell script. And for an agent: never write sed -i without a suffix in a script meant for more than one system; sed -i.bak 's/a/b/' file, then rm file.bak, behaves the same with GNU sed and on a Mac.

**History.** The Windows Subsystem for Linux was first announced at BUILD in 2016 and first shipped with the Windows 10 Anniversary Update; WSL 2, first announced in 2019, relies on the Linux kernel itself, and in May 2025 Microsoft open-sourced the code that powers WSL. Today WSL 2 is the default and "uses virtualization technology to run a Linux kernel inside of a lightweight utility virtual machine". For the fastest performance Microsoft says to store your files "in the WSL file system if you are working in a Linux command line"; a path under /mnt/c is the Windows C: drive mounted into Linux, and Windows is case-insensitive where Linux is case-sensitive. GNU sed documents -i[SUFFIX] as "edit files in place (makes backup if SUFFIX supplied)", so -i alone works there. The sed manual in Apple's text_cmds sources, written by Diomidis Spinellis of FreeBSD, gives -i extension instead, calls -i a non-standard FreeBSD extension, and warns that "It is not recommended to give a zero-length extension when in-place editing files", so a real suffix such as -i.bak is the one form both read the same way.

**Try in five minutes.** printf 'colour\n' > word.txt, then sed -i.bak 's/colour/color/' word.txt && rm word.txt.bak, then cat word.txt. Put the same sed line in portable.sh. It prints color on a Mac, in a Codespace and in WSL alike.

- Docs: [Microsoft Learn, What is the Windows Subsystem for Linux?](https://learn.microsoft.com/en-us/windows/wsl/about), [Microsoft Learn, Working across Windows and Linux file systems](https://learn.microsoft.com/en-us/windows/wsl/filesystems), [GNU sed manual page (Debian)](https://manpages.debian.org/bookworm/sed/sed.1.en.html), [Apple open source, text_cmds: the sed manual and its -i and -I options](https://github.com/apple-oss-distributions/text_cmds/blob/main/sed/sed.1), [Source: Windows Developer Blog, The Windows Subsystem for Linux is now open source (May 2025)](https://blogs.windows.com/windowsdeveloper/2025/05/19/the-windows-subsystem-for-linux-is-now-open-source/)
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
