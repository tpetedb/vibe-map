---
title: "Licences and open source etiquette"
date: 2026-09-24
tags: [tech, docs]
generated: 38cf771d4308
---
# Licences and open source etiquette

Code you publish is under exclusive copyright by default, so without a licence nobody can safely copy, change or share it; an open source licence says what they may do. choosealicense.com starts from three common situations, and an SPDX identifier puts that licence in every file in one line that people and tools can read. Reach for this topic before you make a repository public, before you copy code from one, and before you open your first issue or pull request on someone else's project. And for an agent: check a dependency's licence before you add it, write the SPDX-License-Identifier line in the comment style of each file, and read a project's CONTRIBUTING file before opening an issue or pull request there.

**History.** choosealicense.com, curated by GitHub, says that when you make a creative work, including code, "the work is under exclusive copyright by default", and that software without a licence generally means you have no permission to use, modify or share it. For someone who wants it simple and permissive it points to the MIT License, "a short and simple permissive license with conditions only requiring preservation of copyright and license notices", and for someone who cares about sharing improvements to the GNU GPLv3. The MIT text goes in a file typically named LICENSE or LICENSE.txt in the root of the source code, with [year] and [fullname] replaced by the year and the copyright holders. SPDX short-form identifiers label a file's licence with a single line such as // SPDX-License-Identifier: MIT, human-readable and machine-readable, drawn from the SPDX License List. The etiquette side is in Open Source Guides: before you open an issue or pull request, check the project's contributing docs, usually a file called CONTRIBUTING or a section of the README.

**Try in five minutes.** In a new folder, write LICENSE with the MIT text from choosealicense.com, with the year and your name in place of [year] and [fullname]. Then write hello.py whose first line is # SPDX-License-Identifier: MIT and whose second prints hello.

- Docs: [Choose a License, Choose an open source license](https://choosealicense.com/), [Choose a License, MIT License](https://choosealicense.com/licenses/mit/), [Choose a License, No License](https://choosealicense.com/no-permission/), [SPDX, Handling license info: SPDX License IDs](https://spdx.dev/learn/handling-license-info/), [Open Source Guides, How to Contribute to Open Source](https://opensource.guide/how-to-contribute/), [Source: SPDX, About: overview and history](https://spdx.dev/about/overview/)
- Shelf: Docs and versioning · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #docs
