---
title: "Linus Torvalds"
date: 2026-09-16
tags: [people]
---
# Linus Torvalds

*Creator of Linux and git*

Wrote git in 2005 in about two weeks after the Linux kernel lost its previous version-control tool. Designed it around content-addressed snapshots and cheap branching, which is why every command at Stops 3 and 4 makes sense once you know that model.

**What they would tell you**
- A commit is a snapshot of everything, named by its hash.
- Branches are cheap; use them for every idea.
- History is data; rewriting it locally is fine, rewriting it after sharing is rude.

**Going deeper**
The official git book is free and the first three chapters are enough for everything in this course. The Pro Git chapter on internals explains the content-addressed model in ten pages; read it once and the commands stop feeling arbitrary.

**Rolinda asks:** Two weeks? For the thing everyone uses?

## The encounter
- What is a commit, really?
- Linus Torvalds: A snapshot with a name. Git stores content as objects and names each one by the SHA-1 of a small header plus the content itself. ([git internals chapter](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects))
- The hash of the file?
- Linus Torvalds: Of the word blob, a space, the byte count, a zero byte, then the content. The book hashes 'what is up, doc?' and gets bd9dbf5 and the rest. ([git internals chapter](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects))
- Why should that matter to me?
- Linus Torvalds: Because once the name is the content, losing work gets hard. Branches are cheap for the same reason: they are only a name pointing at one of those objects. ([git internals chapter](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects))

## Your exercise: Hash a blob the way git does
About 12 minutes, in `workspace/mentors/torvalds/`. Status: not yet.

1. Write workspace/mentors/torvalds/hash.py using hashlib.
2. Build the bytes b'blob ' + the length + b'\x00' + b'what is up, doc?' and take the SHA-1 hexdigest.
3. Print exactly: bd9dbf5aae1a3862dd1526723246b20206e5fc37
4. Check yourself: echo -n 'what is up, doc?' | git hash-object --stdin. Then add notes.md with ## What I learned.

Checked by `vibe check --mentor torvalds`: python3 hash.py prints the same hash as git hash-object.

The plaque on the island reads: The name is the content.


## Sources
- [Pro Git (free book)](https://git-scm.com/book/en/v2)
- [git internals chapter](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)

Back to [[Your path]]

#people
