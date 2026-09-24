---
title: "The filesystem and permissions"
date: 2026-09-24
tags: [tech, shell]
generated: fce667e19572
---
# The filesystem and permissions

A Linux machine keeps its files in one agreed tree, and every file in it carries three sets of permissions: for its owner, for the other users in its group, and for everyone else. The tree is written down in the Filesystem Hierarchy Standard, which is why configuration sits under /etc, logs under /var/log and your own files under /home. Reach for this topic when a script says "Permission denied", when a key file has to be readable by you alone, or when you wonder where a program keeps its settings. And for an agent: set a mode with the octal number you mean (chmod 640, chmod 755) rather than guessing with +x or +w, and say which of the three categories the change is for.

**History.** The Filesystem Hierarchy Standard, version 3.0, published by the LSB Workgroup of The Linux Foundation on March 19, 2015, "consists of a set of requirements and guidelines for file and directory placement under UNIX-like operating systems." It names each directory for its job: /etc for host-specific system configuration, /home for user home directories, /tmp for temporary files, /var/log for log files and directories. In the GNU coreutils manual there are three kinds of permission, read, write and execute, and three categories of users who may hold them: the file's owner, other users who are in the file's group, and everyone else. As a number each category takes one octal digit, read 4, write 2 and execute 1, so mode 664 is the same as the symbolic mode ug=rw,o=r. The umask removes permissions you did not mean to give away, and "its default value varies from system to system".

**Try in five minutes.** touch secret.txt, chmod 640 secret.txt, then ls -l secret.txt > perms.txt: the owner may read and write, the group may read, everyone else gets nothing.

- Docs: [The Linux Foundation, Filesystem Hierarchy Standard 3.0](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html), [GNU coreutils manual, Structure of File Mode Bits](https://www.gnu.org/software/coreutils/manual/html_node/Mode-Structure.html), [GNU coreutils manual, Numeric Modes](https://www.gnu.org/software/coreutils/manual/html_node/Numeric-Modes.html), [GNU coreutils manual, The Umask and Protection](https://www.gnu.org/software/coreutils/manual/html_node/Umask-and-Protection.html)
- Unlocks: [[Processes and signals]], [[Shell scripts that fail loudly]]
- Shelf: Terminal and shell · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
