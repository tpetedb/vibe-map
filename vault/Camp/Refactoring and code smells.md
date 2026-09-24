---
title: "Refactoring and code smells"
date: 2026-09-24
tags: [tech, code]
generated: 2bbccf6df39d
---
# Refactoring and code smells

Refactoring is changing the structure of code without changing what it does, in steps small enough that each one is unlikely to go wrong. A code smell is a quick sign on the surface, such as a long function, that often points at a deeper problem. Reach for refactoring before adding a feature to code that makes the feature awkward, and after getting a feature working, when the code is not as clear as it could be. And for an agent: run the tests before and after every refactoring step, name the refactoring you are applying (Extract Function, Inline Function), and keep a refactoring out of the same change as new behaviour.

**History.** On refactoring.com Martin Fowler defines refactoring as "a disciplined technique for restructuring an existing body of code, altering its internal structure without changing its external behavior", whose "heart is a series of small behavior preserving transformations". Because each refactoring is small, "the system is kept fully working after each refactoring", and Fowler writes that he refactors first so a new feature is easy to add, then again once the feature works. His Code Smell note says a smell is "a surface indication that usually corresponds to a deeper problem in the system", a term first coined by Kent Beck, and that smells "don't always indicate a problem". The online catalog lists each refactoring by its second edition name, such as Extract Function, with the aliases it replaces, such as Extract Method. In 1992 William F. Opdyke's PhD thesis at the University of Illinois at Urbana-Champaign, with Ralph E. Johnson as advisor, defined "a set of program restructuring operations (refactorings)" and wrote that they "are defined to be behavior preserving, provided that their preconditions are met". The book's first edition came out in 1999, and Fowler's summary of 5 September 2018 says the second edition's testing chapter was redone for the change from Java to JavaScript.

**Try in five minutes.** Write owing.py with a function print_owing(customer, amounts) that prints a banner, adds up the amounts, then prints name: and amount: lines, and call print_owing("Ada", [30, 12]) at the bottom. Run python3 owing.py and keep the output. Now apply Extract Function: move the two print lines into print_details(customer, outstanding) and call it. Run it again: the output must not change, because a refactoring alters the structure and never the behaviour.

- Docs: [Martin Fowler, refactoring.com](https://refactoring.com/), [Martin Fowler, CodeSmell](https://martinfowler.com/bliki/CodeSmell.html), [Martin Fowler, Catalog of Refactorings: Extract Function](https://refactoring.com/catalog/extractFunction.html), [Martin Fowler, Refactoring: Improving the Design of Existing Code](https://martinfowler.com/books/refactoring.html), [Source: Martin Fowler, Changes for the 2nd Edition of Refactoring](https://martinfowler.com/articles/refactoring-2nd-changes.html), [William F. Opdyke, Refactoring Object-Oriented Frameworks, PhD thesis, University of Illinois at Urbana-Champaign, 1992](https://www.laputan.org/pub/papers/opdyke-thesis.pdf)
- Unlocks: [[Code review as a practice]]
- Shelf: Languages and code · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
