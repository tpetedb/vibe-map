---
title: "Incidents and blameless postmortems"
date: 2026-09-24
tags: [tech, ship]
generated: ff11951aac35
---
# Incidents and blameless postmortems

When something breaks in production, incident management gives each person who responds one clear role until it is resolved. A postmortem is the written record afterwards: what happened, its impact, what was done, the root causes and the follow-up actions, written without blaming anyone. Reach for this topic before your first outage, so the roles and the template exist when you need them. And for an agent: when you draft a postmortem, name contributing causes and systems, never a person at fault, and end with action items that each have an owner.

**History.** Google's Site Reliability Engineering book says it is better to declare an incident early, find a simple fix and close it, than to spin up the incident management framework hours into a burgeoning problem. It delegates distinct roles: the incident commander "holds the high-level state about the incident", the Ops lead works with the commander on the response, communication is "the public face of the incident response task force", and planning deals with longer-term issues such as filing bugs and arranging handoffs. "A postmortem is a written record of an incident, its impact, the actions taken to mitigate or resolve it, the root cause(s), and the follow-up actions to prevent the incident from recurring", and to be truly blameless "it must focus on identifying the contributing causes of the incident without indicting any individual or team". The book's example postmortem for Shakespeare Search, dated 2015-10-21, has a summary, impact, root causes, trigger, resolution, detection, action items, lessons learned (what went well, what went wrong, where we got lucky) and a timeline. NIST's Computer Security Incident Handling Guide, SP 800-61, published in January 2004, covers handling incidents from initial preparation through the post-incident lessons learned phase.

**Try in five minutes.** Pick a real or invented outage, even "the game would not load for ten minutes". Write postmortem.md with the headings of the SRE book's example: Summary, Impact, Root Causes, Trigger, Resolution, Detection, Action Items, Lessons Learned and Timeline, and fill each with one or two lines.

- Docs: [Google SRE book, Managing Incidents](https://sre.google/sre-book/managing-incidents/), [Google SRE book, Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/), [Google SRE book, Appendix D: Example Postmortem](https://sre.google/sre-book/example-postmortem/), [NIST SP 800-61 Rev. 3, Incident Response Recommendations and Considerations for Cybersecurity Risk Management (April 2025)](https://csrc.nist.gov/pubs/sp/800/61/r3/final), [Source: NIST SP 800-61, Computer Security Incident Handling Guide (January 2004)](https://csrc.nist.gov/pubs/sp/800/61/final)
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
