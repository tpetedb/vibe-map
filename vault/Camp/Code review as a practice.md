---
title: "Code review as a practice"
date: 2026-09-24
tags: [tech, git]
generated: 9eeaf6172913
---
# Code review as a practice

Code review is a second person reading a change before it is merged, to keep the health of the whole codebase improving over time. Google publishes the guidelines its engineers use: what a reviewer looks for, how small a change should be, and how to disagree. Reach for them when you review a pull request, when yours sits unreviewed because it is too big, or when an agent opens a pull request that has to pass the same gates as a person. And for an agent: keep each pull request small and about one thing, put refactorings in their own change, and mark a comment that is only polish with Nit: so the author knows it is optional.

**History.** Google's engineering practices documentation says "the primary purpose of code review is to make sure that the overall code health of Google's code base is improving over time", and gives the senior principle: reviewers "should favor approving a CL once it is in a state where it definitely improves the overall code health of the system being worked on, even if the CL isn't perfect." A CL is a changelist, what other organisations call a change, a patch or a pull request, and LGTM, "Looks Good to Me", is what a reviewer says when approving one. A comment that is only a point of polish is prefixed with "Nit:", and "technical facts and data overrule opinions and personal preferences", while the style guide is the absolute authority on style. What to look for in a code review starts with the overall design of the CL, then functionality, complexity, tests, naming, comments, style, consistency and documentation. On size, "100 lines is usually a reasonable size for a CL, and 1000 lines is usually too large", and it is usually best to do refactorings in a separate CL from feature changes.

**Try in five minutes.** Take a small diff, your own last commit or git show HEAD in any repository. Write review.md with at least one comment under each of Design:, Tests: and Nit:, then end it with your verdict: LGTM, or what has to change first.

- Docs: [Google engineering practices, The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html), [Google engineering practices, What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [Google engineering practices, Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html), [Google engineering practices documentation, terminology](https://google.github.io/eng-practices/), [Source: the commit history of google/eng-practices](https://github.com/google/eng-practices/commits/master/README.md)
- Unlocks: [[Continuous delivery and deploy strategies]]
- Shelf: Git and GitHub · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #git
