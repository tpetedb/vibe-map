---
title: "Text tools, grep, sed and awk"
date: 2026-09-24
tags: [tech, shell]
generated: d240e21fef51
---
# Text tools, grep, sed and awk

grep, sed, awk, cut, sort and uniq are small programs that each do one thing to lines of text, and a pipe joins them into a report without a line of code. grep selects the lines that match a pattern, sed edits a stream, awk runs a little program over records and fields, cut takes columns out, and uniq collapses repeated adjacent lines. Reach for them when a log, a CSV or the output of another command has the answer in it and you want it in a minute, not after writing a script. And for an agent: uniq only compares adjacent lines, so sort before uniq, and count with grep -c rather than piping to wc when the question is how many lines match.

**History.** The Seventh Edition of Unix, released by Bell Laboratories in January 1979, is where awk and sed arrived among "many new applications". The grep utility "shall search the input files, selecting lines matching one or more patterns", and grep -c writes "only a count of selected lines". The sed utility "is a stream editor that shall read one or more text files, make editing changes according to a script of editing commands, and write the results to standard output." An awk program "is a sequence of patterns and corresponding actions", and by default a record is a line. uniq writes "one copy of each input line" but compares only adjacent lines, and uniq -c puts the number of times each line occurred in front of it.

**Try in five minutes.** printf 'ada,3\nbob,5\nada,4\ncy,1\n' > runs.csv, then cut -d, -f1 runs.csv | sort | uniq -c | sort -rn | head -1 > report.txt, then awk -F, '{ total += $2 } END { print "total", total }' runs.csv >> report.txt, then sed -n 's/^bob,/best: bob /p' runs.csv >> report.txt.

- Docs: [POSIX.1-2024, grep: search a file for a pattern](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/grep.html), [POSIX.1-2024, sed: stream editor](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/sed.html), [POSIX.1-2024, awk: pattern scanning and processing language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html), [POSIX.1-2024, uniq: report or filter out repeated lines](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/uniq.html), [POSIX.1-2024, cut: cut out selected fields of each line](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/cut.html), [Source: TUHS, Seventh Edition Unix (January 1979)](https://www.tuhs.org/cgi-bin/utree.pl?file=V7)
- Unlocks: [[Shell scripts that fail loudly]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
