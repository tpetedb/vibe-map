---
title: "cron and timers"
date: 2026-09-24
tags: [tech, shell]
generated: 843ee3412816
---
# cron and timers

cron runs a command on a schedule: one line per job, five time fields and the command, installed with crontab. A systemd timer does the same job as a unit, next to the service it starts, and can catch up on a run it missed while the timer was inactive. Reach for either when something must happen every night, every Monday or every fifteen minutes without you, and remember that the job gets a default environment of its own, not the shell you tested it in. And for an agent: in a crontab line, give the command with full paths and write its output somewhere, because the job does not see the variables of the shell you tested it in, and a % in the command field means a newline unless you escape it.

**History.** POSIX.1-2024 defines a crontab entry as lines of six fields: minute (0 to 59), hour (0 to 23), day of the month (1 to 31), month of the year (1 to 12), day of the week (0 to 6, with 0 as Sunday), and the command. Each time field is an asterisk for all values, a number, a range such as 1-5 or a list separated by commas, and its own example, 15 3 * * 1-5, runs every weekday morning at 3:15 am. The sixth field "shall be executed by sh", and a % in it "shall be translated to a <newline>". The HOME, LOGNAME, PATH and SHELL a job gets are defaults, "not affected by the settings of those variables when crontab is run". A systemd timer is a unit whose name ends in .timer, OnCalendar= gives it a wallclock schedule, and Persistent=true triggers the service immediately if a run was missed while the timer was inactive.

**Try in five minutes.** Write crontab.txt with one line that runs /usr/bin/env date at 7:30 on weekdays: 30 7 * * 1-5 /usr/bin/env date >> /tmp/cron-camp.log 2>&1. crontab -l shows what is installed now; install your file only if you mean it, with crontab crontab.txt, because that replaces your whole crontab entry.

- Docs: [POSIX.1-2024, crontab: schedule periodic background work](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/crontab.html), [systemd.timer(5), timer unit configuration](https://man7.org/linux/man-pages/man5/systemd.timer.5.html), [systemd.unit(5), unit configuration](https://man7.org/linux/man-pages/man5/systemd.unit.5.html)
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
