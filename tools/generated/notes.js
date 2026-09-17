"Unix and the terminal":{t:"dark",md:`# Unix and the terminal
The terminal is a text conversation with the computer. Every tool in this tree is a command you type; every agent in the Imperial Age is, underneath, typing those same commands for you. Learning ten commands (ls, cd, cat, mkdir, cp, mv, rm, grep, find, man) covers most of daily use.
**History.** Unix was born at Bell Labs in 1969 (Thompson, Ritchie). macOS is a certified Unix, so your Mac terminal is the direct descendant. Linux (1991, Torvalds) is the free reimplementation that servers, clouds and containers run on.
**Try in five minutes.** Open Terminal.app. Type pwd, then ls -la, then man ls (q to quit).
- Docs: [The Missing Semester (MIT)](https://missing.csail.mit.edu), [Linux Journey](https://linuxjourney.com), [Source: Ritchie, The Evolution of the Unix Time-sharing System (1984)](https://www.read.seas.harvard.edu/~kohler/class/aosref/ritchie84evolution.pdf), [Source: The Open Group register of UNIX certified products](https://www.opengroup.org/openbrand/register/), [Source: Torvalds' 1991 Linux announcements (CMU archive)](https://www.cs.cmu.edu/~awb/linux.history.html)
- Unlocks: [[Bash and shell scripts]], [[Files, folders and paths]], [[Git]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Bash and shell scripts":{t:"dark",md:`# Bash and shell scripts
Bash is the language the terminal speaks. A shell script is a text file of commands; pipes (|) chain small tools into big ones. This is also what hooks and setup scripts are written in.
**History.** The Bourne shell shipped with Seventh Edition Unix in January 1979; bash (the Bourne-again shell, written by Brian Fox) went into beta as the GNU replacement in June 1989. macOS switched its default login shell to zsh with macOS 10.15 Catalina in 2019; zsh is bash-compatible for everything you will meet tonight.
**Try in five minutes.** cat data/scores.csv | sort -t, -k3 -n | tail -3 (the three highest scores, no code written).
- Docs: [Bash Guide (Greg's wiki)](https://mywiki.wooledge.org/BashGuide), [ShellCheck, lint your scripts](https://www.shellcheck.net), [Source: GNU Bash manual, What is Bash?](https://www.gnu.org/software/bash/manual/html_node/What-is-Bash_003f.html), [Source: TUHS, Seventh Edition Unix (January 1979)](https://www.tuhs.org/cgi-bin/utree.pl?file=V7), [Source: GNU's Bulletin, June 1989](https://www.gnu.org/bulletins/bull7.html), [Source: Apple, Use zsh as the default shell on your Mac](https://support.apple.com/en-us/102360)
- Unlocks: [[zsh and your shell config]], [[Dotfiles]], [[Docker and containers]], [[Hook]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"zsh and your shell config":{t:"dark",md:`# zsh and your shell config
~/.zshrc runs every time you open a terminal: it sets PATH (the folders where commands are looked up), aliases (short names for long commands), the prompt, and small functions. zsh is the macOS default; it is bash-compatible for daily use and adds better completion and globbing. oh-my-zsh bundles plugins and themes; starship is a fast prompt that works in any shell. Keep .zshrc in your dotfiles repo so a new machine is one clone away.
**History.** zsh was written by Paul Falstad while a student at Princeton, around 1990. Apple made it the default login shell with macOS 10.15 Catalina in October 2019, replacing bash.
**Try in five minutes.** source scripts/vibe.zsh then g status.
- Docs: [zsh manual](https://zsh.sourceforge.io/Doc/), [oh-my-zsh](https://ohmyz.sh), [starship prompt](https://starship.rs), [Source: zsh FAQ, 1.1 What is it?](https://zsh.sourceforge.io/FAQ/zshfaq01.html), [Source: Apple, Use zsh as the default shell on your Mac](https://support.apple.com/en-us/102360), [Source: Apple newsroom, macOS Catalina is available today (October 2019)](https://www.apple.com/newsroom/2019/10/macos-catalina-is-available-today/)
- Unlocks: [[Dotfiles]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Files, folders and paths":{t:"dark",md:`# Files, folders and paths
A project is a folder. A path is an address inside it: absolute (/Users/lotte/vibe-map) or relative (./data/scores.csv). Agents work inside one folder at a time and see the world as files, which is why structure matters more than in a GUI.
**History.** The hierarchical file system with directories comes from Multics (Daley and Neumann, 1965) via Unix. Hidden dotfiles are, according to Rob Pike, the result of an early Unix shortcut: ls skipped every name starting with a dot to hide . and .., and people started using it on purpose.
**Try in five minutes.** In the template: find . -type f -not -path './.venv/*' | head -30 and read what each path is for.
- Docs: [Unix filesystem basics](https://missing.csail.mit.edu/2020/course-shell/), [Source: Daley and Neumann, A General-Purpose File System for Secondary Storage (FJCC 1965)](https://multicians.org/fjcc4.html), [Source: Rob Pike, A lesson in shortcuts (2012, archived copy)](https://www.moldvan.com/hidden-dot-files-linux-came-rob-pike-g/)
- Unlocks: [[Dotfiles]], [[Config formats: JSON, YAML, TOML, Markdown]], [[Git]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Dotfiles":{t:"dark",md:`# Dotfiles
Hidden files and folders (.zshrc, .gitconfig, .claude/, .agents/) that configure your tools. Your agent setup is dotfiles: AGENTS.md is the exception that chose to be visible. Keep them in a repo and your setup becomes portable.
**History.** Sharing dotfile repos on GitHub took off after GitHub launched in 2008; the community guide dotfiles.github.io followed in 2012. Today the same idea configures AI agents: .claude/settings.json, .agents/skills/.
**Try in five minutes.** ls -la ~ and open ~/.zshrc. Add one alias: alias g='uv run vibe'.
- Docs: [dotfiles.github.io](https://dotfiles.github.io), [Claude Code settings](https://code.claude.com/docs/en/settings), [Source: GitHub launch post (April 2008)](https://github.blog/2008-04-10-we-launched/), [Source: dotfiles.github.io repository (created April 2012)](https://github.com/dotfiles/dotfiles.github.com)
- Unlocks: [[Config formats: JSON, YAML, TOML, Markdown]], [[.env files and secrets]], [[Your harness: AGENTS.md, CLAUDE.md, dotfiles for agents]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Config formats: JSON, YAML, TOML, Markdown":{t:"dark",md:`# Config formats: JSON, YAML, TOML, Markdown
Tools read settings from text files in a few formats. JSON: strict, braces, what APIs speak. YAML: indentation, what CI and Docker Compose use. TOML: sections, what Python packaging uses. Markdown: prose with light structure, what agents and Obsidian read.
**History.** JSON was first presented at json.org by Douglas Crockford in 2001; YAML began in 2001 (1.0 spec in 2004); Markdown by John Gruber in 2004; TOML by Tom Preston-Werner in 2013. Agents made Markdown the config format for instructions (AGENTS.md, SKILL.md) because it is readable by both people and models.
**Try in five minutes.** Open .claude/settings.json (JSON) and .agents/skills/duckdb-sql/SKILL.md (Markdown with YAML frontmatter). Spot the three formats in one repo.
- Docs: [JSON](https://www.json.org/json-en.html), [YAML](https://yaml.org/spec/1.2.2/), [TOML](https://toml.io), [Markdown](https://daringfireball.net/projects/markdown/), [Source: ECMA-404, The JSON data interchange syntax (2nd edition)](https://ecma-international.org/wp-content/uploads/ECMA-404_2nd_edition_december_2017.pdf), [Source: YAML 1.0 specification (2004)](https://yaml.org/spec/1.0/), [Source: Markdown 1.0.1 (December 2004)](https://daringfireball.net/projects/markdown/), [Source: TOML v0.1.0 release (March 2013)](https://github.com/toml-lang/toml/releases/tag/v0.1.0)
- Unlocks: [[.env files and secrets]], [[YAML in practice: CI and Compose]], [[TOML in practice: pyproject.toml]], [[AGENTS.md]], [[Agent Skills standard]]
- Age: Dark Age · Level: Intern
#tech #dark`},
".env files and secrets":{t:"dark",md:`# .env files and secrets
A .env file holds KEY=VALUE pairs (API tokens, database URLs) that your code reads at startup, so the secret lives on the machine and not in the repo. The pattern: .env is listed in .gitignore and never committed; .env.example (in this repo env.example, without the dot, because some agent guardrails refuse anything that looks like a real .env) is committed with the same keys and empty values so the next person knows what to fill in; python-dotenv loads .env into os.environ. A token that lands in a commit has to be rotated, because git history is forever.
**History.** The twelve-factor app (Adam Wiggins at Heroku, 2011) made 'store config in the environment' a rule. The dotenv convention started with Brandon Keepers' Ruby dotenv gem in July 2012; python-dotenv followed on PyPI in September 2014.
**Try in five minutes.** Copy env.example to .env in this repo and print one variable: uv run python -c "from dotenv import dotenv_values; print(dotenv_values('.env'))".
- Docs: [Twelve-Factor config](https://12factor.net/config), [python-dotenv](https://github.com/theskumar/python-dotenv), [GitHub: removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository), [Source: The Twelve-Factor App](https://12factor.net/), [Source: Adam Wiggins, writing (The Twelve-Factor App, 2011)](https://adamwiggins.com/), [Source: bkeepers/dotenv repository (July 2012)](https://github.com/bkeepers/dotenv), [Source: python-dotenv release history on PyPI (September 2014)](https://pypi.org/project/python-dotenv/#history)
- Unlocks: [[Security and permissions]], [[Docker and containers]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"localhost and ports":{t:"dark",md:`# localhost and ports
localhost (127.0.0.1) is your own machine talking to itself over the network stack. A port is a numbered door; a dev server on port 8000 means open http://localhost:8000. Everything web starts here before it goes anywhere.
**History.** Network 127 is set aside for loopback in the Assigned Numbers RFCs (RFC 990, 1986); TCP/IP became the ARPANET standard on 1 January 1983 (RFC 801). Port numbers were assigned by hand by Jon Postel for years, in those same RFCs.
**Try in five minutes.** python3 -m http.server 8000 in the game folder, open http://localhost:8000/game/ in a browser. Ctrl-C to stop.
- Docs: [MDN: How the web works](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works), [Source: RFC 990, Assigned Numbers (1986)](https://www.rfc-editor.org/rfc/rfc990), [Source: RFC 801, NCP/TCP Transition Plan (1981)](https://www.rfc-editor.org/rfc/rfc801)
- Unlocks: [[HTTP and APIs]], [[Docker and containers]], [[MCP]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Git":{t:"dark",md:`# Git
A time machine for a folder. Commit = named snapshot, branch = parallel line of work, merge = bring them together, revert = undo safely. Agents can produce a lot of change fast; git is what makes that safe.
**History.** Linus Torvalds wrote git in April 2005, in about ten days, after the Linux kernel lost its previous tool (BitKeeper). GitHub launched in 2008 and made it social; today git is the default version control system almost everywhere.
**Try in five minutes.** git log --oneline | head, then change one line, git diff, git commit -am 'why', git revert HEAD.
- Docs: [Git tutorial](https://git-scm.com/docs/gittutorial), [Oh Shit, Git!?!](https://ohshitgit.com), [Claude Code common workflows](https://code.claude.com/docs/en/common-workflows), [Source: Pro Git, A Short History of Git](https://git-scm.com/book/en/v2/Getting-Started-A-Short-History-of-Git), [Source: Linux Foundation, 10 Years of Git interview with Linus Torvalds (2015)](https://www.linuxfoundation.org/blog/blog/10-years-of-git-an-interview-with-git-creator-linus-torvalds), [Source: GitHub launch post (April 2008)](https://github.blog/2008-04-10-we-launched/)
- Unlocks: [[GitHub, pull requests, Pages]], [[Hook]], [[CI/CD and automation]], [[Semantic Versioning]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Python":{t:"feudal",md:`# Python
The general-purpose language of data, automation and AI tooling. Readable, batteries included, the language agents write most fluently. Use it for scripts, data, glue, and small services.
**History.** Guido van Rossum released Python 0.9.0 in February 1991; Python 3.0 (December 2008) broke compatibility and Python 2 was only retired in January 2020. It became the language of machine learning through NumPy, pandas and PyTorch, and of AI agents through their SDKs.
**Try in five minutes.** python3 python/scores.py, then add one line that prints the worst run.
- Docs: [Official tutorial](https://docs.python.org/3/tutorial/), [Exercism track](https://exercism.org/tracks/python), [uv](https://docs.astral.sh/uv/), [Source: Guido van Rossum, A Brief Timeline of Python](https://python-history.blogspot.com/2009/01/brief-timeline-of-python.html), [Source: python.org, Sunsetting Python 2](https://www.python.org/doc/sunset-python-2/)
- Unlocks: [[TOML in practice: pyproject.toml]], [[Python libraries: what they are for]], [[SQL and DuckDB]], [[Building and consuming APIs]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"TOML in practice: pyproject.toml":{t:"feudal",md:`# TOML in practice: pyproject.toml
TOML is INI with types. [tables] group keys; key = "value" pairs are typed (strings, numbers, booleans, dates, arrays); \`[[arrays.of.tables]]\` repeat asection, one block per item. Python packaging chose it because it is unambiguous, has a small spec, and stays readable when hand-edited: pyproject.toml declares the package, its dependencies and the tool settings (ruff, pytest) in one file.
**History.** TOML was started by Tom Preston-Werner in 2013 and reached 1.0.0 in January 2021. PEP 518 (2016) introduced pyproject.toml for build requirements, PEP 621 (2020) added the [project] table, and tomllib joined the standard library with Python 3.11 in October 2022.
**Try in five minutes.** Read pyproject.toml in this repo and add a dependency, then uv sync.
- Docs: [TOML 1.0.0 spec](https://toml.io/en/v1.0.0), [Python packaging: writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [tomllib](https://docs.python.org/3/library/tomllib.html), [Source: TOML v0.1.0 release (March 2013)](https://github.com/toml-lang/toml/releases/tag/v0.1.0), [Source: TOML 1.0.0 release (January 2021)](https://github.com/toml-lang/toml/releases/tag/1.0.0), [Source: PEP 518 (created May 2016)](https://peps.python.org/pep-0518/), [Source: PEP 621 (created June 2020)](https://peps.python.org/pep-0621/), [Source: Python 3.11.0 release (October 2022, PEP 680 tomllib)](https://www.python.org/downloads/release/python-3110/)
- Unlocks: [[Python libraries: what they are for]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"Python libraries: what they are for":{t:"feudal",md:`# Python libraries: what they are for
pandas (tables), numpy (numbers), matplotlib/plotly (charts), requests/httpx (talk to APIs), duckdb (SQL on files), pydantic (validate data), fastapi (build an API), typer/click (build a CLI), playwright (drive a browser), pytest (tests). Install with uv; import only what removes real work.
**History.** NumPy 2005 (1.0 in 2006), pandas 2008 (Wes McKinney, at a hedge fund), requests 2011, pytest 2004 lineage, FastAPI 2018, pydantic 2017, Playwright 2020, DuckDB 2019 (started at CWI in 2018). The stack is young; most of it postdates the iPhone.
**Try in five minutes.** uv pip install pandas, then python3 -c "import pandas as pd; print(pd.read_csv('data/scores.csv').describe())".
- Docs: [pandas 10 minutes](https://pandas.pydata.org/docs/user_guide/10min.html), [Requests](https://requests.readthedocs.io), [pytest](https://docs.pytest.org), [FastAPI](https://fastapi.tiangolo.com), [Source: numpy.org, About NumPy](https://numpy.org/about/), [Source: pandas.pydata.org, About pandas](https://pandas.pydata.org/about/), [Source: requests release history on PyPI (February 2011)](https://pypi.org/project/requests/#history), [Source: pytest history](https://docs.pytest.org/en/stable/history.html), [Source: FastAPI release history on PyPI (December 2018)](https://pypi.org/project/fastapi/#history), [Source: pydantic v0.1 release (June 2017)](https://github.com/pydantic/pydantic/releases/tag/v0.1), [Source: Playwright v1.0.0 release (May 2020)](https://github.com/microsoft/playwright/releases/tag/v1.0.0), [Source: DuckDB v0.1.0 release (June 2019)](https://github.com/duckdb/duckdb/releases/tag/v0.1.0)
- Unlocks: [[Building and consuming APIs]], [[Tests and evals]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"SQL and DuckDB":{t:"feudal",md:`# SQL and DuckDB
SQL asks questions of tables: select what, from where, filter, group, order. DuckDB runs it on CSV and Parquet files with no server, which is why the data hour uses it. Window functions (lag, row_number) are the step from junior to medior.
**History.** SQL was designed at IBM in 1974 (as SEQUEL, by Chamberlin and Boyce) and standardised by ANSI in 1986 and ISO in 1987. It has outlived every technology that promised to replace it. DuckDB (started at CWI Amsterdam in 2018, first release 2019) brought analytics SQL to a single file.
**Try in five minutes.** duckdb < sql/streaks.sql, then change limit 3 to limit 10 and read the lag() comment.
- Docs: [DuckDB docs](https://duckdb.org/docs/), [SQLBolt](https://sqlbolt.com), [Mode SQL tutorial](https://mode.com/sql-tutorial/), [Source: Chamberlin and Boyce, SEQUEL (1974), university copy](https://course.khoury.northeastern.edu/cs3200f20s2/ssl/readings/boyce.pdf), [Source: The Open Group, SQL: The Standard and the Language](http://archive.opengroup.org/public/tech/datam/sql.htm), [Source: DuckDB Foundation](https://duckdb.foundation/), [Source: DuckDB v0.1.0 release (June 2019)](https://github.com/duckdb/duckdb/releases/tag/v0.1.0)
- Unlocks: [[Data: files, schemas, warehouses]], [[Building and consuming APIs]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"HTML, CSS and JavaScript":{t:"feudal",md:`# HTML, CSS and JavaScript
The three languages of a web page: structure, style, behaviour. A single HTML file can hold all three, which is why the game is one file. JavaScript is also the language of Node and most CLIs you install with npm.
**History.** Tim Berners-Lee's first web software ran in 1990 and HTML was written up as an IETF draft in 1993; CSS1 became a W3C Recommendation in 1996; Brendan Eich prototyped JavaScript in ten days in May 1995. Node.js (2009) put JavaScript on servers; npm calls itself the world's largest software registry.
**Try in five minutes.** Open game/index.html in a text editor and in a browser side by side. Change the h1, reload.
- Docs: [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Learn_web_development), [three.js (what the game uses)](https://threejs.org/docs/), [Source: Berners-Lee and Connolly, HTML Internet-Draft (June 1993)](https://www.w3.org/MarkUp/draft-ietf-iiir-html-01.txt), [Source: W3C, Cascading Style Sheets level 1 (December 1996)](https://www.w3.org/TR/REC-CSS1-961217), [Source: Brendan Eich, New JavaScript Engine Module Owner (2011)](https://brendaneich.com/2011/06/new-javascript-engine-module-owner/), [Source: Node.js v0.x source archive (2009)](https://github.com/nodejs/node-v0.x-archive), [Source: npm docs, About npm](https://docs.npmjs.com/about-npm)
- Unlocks: [[HTTP and APIs]], [[localhost and ports]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"Other languages and what they are for":{t:"feudal",md:`# Other languages and what they are for
TypeScript: JavaScript with types, most web apps. Go: servers and CLIs, one binary. Rust: speed and safety, the new systems language. Java/Kotlin, C#: enterprise and Android. Swift: Apple. C/C++: everything underneath. Bash: gluing them. You do not learn them all; you learn to read them, and agents write them.
**History.** C 1972, C++ 1985, Java 1995, C# 2002, Go 2009, Rust 2015 (1.0), Swift 2014, TypeScript 2012. Each language is a bet on what is expensive: programmer time (Python), machine time (Rust), or organisational scale (Java).
**Try in five minutes.** Ask Claude: 'rewrite python/scores.py in Go, explain each line to a Python person'. Read it. Delete it.
- Docs: [Stack Overflow developer survey](https://survey.stackoverflow.co), [Rust book](https://doc.rust-lang.org/book/), [Go tour](https://go.dev/tour/), [Source: Ritchie, The Development of the C Language (Harvard copy)](https://cscie26.dce.harvard.edu/~dce-lib113/reference/c/c_history.html), [Source: Bjarne Stroustrup's FAQ](https://www.stroustrup.com/bs_faq.html), [Source: java.com, What is Java?](https://www.java.com/en/download/help/whatis_java.html), [Source: Microsoft Learn, The history of C#](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history), [Source: Go FAQ, history](https://go.dev/doc/faq), [Source: Announcing Rust 1.0 (May 2015)](https://blog.rust-lang.org/2015/05/15/Rust-1.0/), [Source: Apple newsroom, iOS 8 SDK and Swift (June 2014)](https://www.apple.com/newsroom/2014/06/02Apple-Releases-iOS-8-SDK-With-Over-4-000-New-APIs/), [Source: Announcing TypeScript 1.0 (first release October 2012)](https://devblogs.microsoft.com/typescript/announcing-typescript-1-0/)
- Unlocks: [[Docker and containers]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"Markdown and Obsidian":{t:"feudal",md:`# Markdown and Obsidian
Markdown is prose with a little structure (#, -, **, \`[[links]]\`). It is the file format of documentation, READMEs, AGENTS.md, skills, and Obsidian notes. Obsidian is a Markdown editor with a graph, so your notes are plain files an agent can read and write.
**History.** Markdown 2004; GitHub's own flavour was public by 2009 and made it the format of READMEs; Obsidian (2020) made it a second brain; agent instruction files in 2024 to 2025 made it a config language.
**Try in five minutes.** Write vault/Camp/Me.md with three sentences and two \`[[links]]\`. Open the graph.
- Docs: [Markdown guide](https://www.markdownguide.org), [Obsidian help](https://help.obsidian.md), [Mermaid](https://mermaid.js.org/intro/), [Source: Markdown 1.0.1 (December 2004)](https://daringfireball.net/projects/markdown/), [Source: Daring Fireball on GitHub Flavored Markdown (October 2009)](https://daringfireball.net/linked/2009/10/23/github-flavored-markdown), [Source: Obsidian, About](https://obsidian.md/about)
- Unlocks: [[Claude and Obsidian]], [[AGENTS.md]], [[README and the quickstart]], [[Architecture decision records]], [[Obsidian features]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"Obsidian features":{t:"feudal",md:`# Obsidian features
Obsidian is more than a Markdown editor: properties (typed frontmatter), callouts, embeds, a canvas, bases (database views over your notes), templates, daily notes, bookmarks, a graph, a URI scheme, a CLI, Sync and Publish. The vault carries one note per feature, each with the exact commands, the syntax and a five-minute try taken from the official help; \`vibe vault feature --all\` writes them.
**History.** Obsidian left beta with 1.0.0 on 13 October 2022, added Canvas in December 2022, Properties with 1.4 on 31 August 2023, Bases (table and cards views) in the 1.9 line, and a command line interface that needs the 1.12 installer; kanban views arrived in 1.14 early access.
**Try in five minutes.** Run \`uv run vibe vault feature --all\`, open the vault in Obsidian, open \`Camp map.canvas\`, then \`Tech notes.base\`, then run Slides: Start presentation on Camp deck.
- Docs: [Obsidian Help](https://help.obsidian.md/), [The feature table](https://github.com/tpetedb/vibe-map/blob/main/docs/OBSIDIAN.md), [Source: Obsidian 1.0.0 changelog (13 October 2022)](https://obsidian.md/changelog/2022-10-13-desktop-v1.0.0/), [Source: Obsidian 1.4 changelog, Properties (31 August 2023)](https://obsidian.md/changelog/2023-08-31-desktop-v1.4.5/), [Source: Obsidian Help, Bases views (table and cards since 1.9)](https://help.obsidian.md/Bases/Views), [Source: Obsidian Help, Obsidian CLI (requires the 1.12 installer)](https://help.obsidian.md/Extending+Obsidian/Obsidian+CLI), [Source: Wikipedia, Obsidian (software): Canvas introduced December 2022](https://en.wikipedia.org/wiki/Obsidian_(software))
- Unlocks: [[Claude and Obsidian]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"Data: files, schemas, warehouses":{t:"feudal",md:`# Data: files, schemas, warehouses
Data lives in files (CSV, Parquet), databases (Postgres, SQLite), and warehouses (Snowflake, BigQuery, DuckDB locally). A schema is the contract: column names and types. Most data pain is schema drift, which is why AGENTS.md pins the columns of scores.csv.
**History.** Relational databases: Codd 1970. Postgres 1986 (Berkeley). SQLite 2000, in every phone. Cloud warehouses (BigQuery 2011, Redshift 2012, Snowflake 2015) separated storage from compute. Parquet (2013, Twitter and Cloudera) is the file format they all read.
**Try in five minutes.** duckdb -c "copy 'data/scores.csv' to 'data/scores.parquet'" then query the parquet file. Same SQL, smaller file.
- Docs: [Parquet](https://parquet.apache.org/docs/), [SQLite](https://www.sqlite.org/docs.html), [Postgres tutorial](https://www.postgresql.org/docs/current/tutorial.html), [Source: IBM, The relational database (Codd, 1970)](https://www.ibm.com/history/relational-database), [Source: PostgreSQL docs, A Brief History of PostgreSQL](https://www.postgresql.org/docs/current/history.html), [Source: SQLite release history (2000-05-29)](https://www.sqlite.org/changes.html), [Source: SQLite, Most Widely Deployed Database](https://www.sqlite.org/mostdeployed.html), [Source: Google Cloud blog, Google BigQuery Service (November 2011)](https://cloudplatform.googleblog.com/2011/11/google-bigquery-service-big-data.html), [Source: AWS, Announcing Amazon Redshift (November 2012)](https://aws.amazon.com/about-aws/whats-new/2012/11/28/announcing-amazon-redshift/), [Source: Dageville et al., The Snowflake Elastic Data Warehouse (SIGMOD 2016)](https://info.snowflake.net/rs/252-RFO-227/images/Snowflake_SIGMOD.pdf), [Source: Twitter Engineering, Announcing Parquet 1.0 (2013)](https://blog.x.com/engineering/en_us/a/2013/announcing-parquet-10-columnar-storage-for-hadoop)
- Unlocks: [[Building and consuming APIs]], [[Tests and evals]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"HTTP and APIs":{t:"castle",md:`# HTTP and APIs
HTTP is request and response: a URL, a method (GET, POST), headers, a body, a status code (200, 404, 500). An API is an HTTP endpoint that returns data instead of a page, usually JSON. Every AI model you call is an HTTP API; MCP is a layer on top of the same idea.
**History.** HTTP 0.9 in 1991, HTTP/1.1 in 1997 (RFC 2068), HTTP/2 in 2015 (RFC 7540). REST was named in Roy Fielding's 2000 dissertation. The OpenAI API (June 2020) made calling a model one POST request.
**Try in five minutes.** curl -s https://api.github.com/repos/duckdb/duckdb | head -20. You just used an API.
- Docs: [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview), [curl](https://curl.se/docs/manual.html), [Postman](https://learning.postman.com), [Source: W3C, The original HTTP as defined in 1991](https://www.w3.org/Protocols/HTTP/AsImplemented.html), [Source: RFC 2068, HTTP/1.1 (January 1997)](https://www.rfc-editor.org/rfc/rfc2068), [Source: RFC 7540, HTTP/2 (May 2015)](https://www.rfc-editor.org/rfc/rfc7540), [Source: Fielding, Architectural Styles and the Design of Network-based Software Architectures (2000)](https://ics.uci.edu/~fielding/pubs/dissertation/top.htm), [Source: OpenAI API announcement (June 2020)](https://openai.com/index/openai-api/)
- Unlocks: [[Building and consuming APIs]], [[MCP]], [[SSH and remote machines]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"Building and consuming APIs":{t:"castle",md:`# Building and consuming APIs
Consuming: read the docs, get a key, make a request, parse JSON. Building: FastAPI turns a Python function into an endpoint in five lines. Keys are secrets: environment variables, never in git. This is the bridge between your data and every other system.
**History.** SOAP was designed from 1998 and published in 1999; REST-with-JSON replaced it in the 2010s; GraphQL (open sourced 2015) and gRPC (announced 2015, 1.0 in 2016) added alternatives. Today the agent-facing version of an API is an MCP server.
**Try in five minutes.** Ask Claude: 'wrap sql/per_player.sql in a FastAPI endpoint /players and run it on localhost:8000'. Open the URL.
- Docs: [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/), [httpx](https://www.python-httpx.org), [Twelve-Factor config](https://12factor.net/config), [Source: Don Box, A Brief History of SOAP (2001)](https://www.xml.com/pub/a/ws/2001/04/04/soap.html), [Source: graphql.org, GraphQL: A data query language (September 2015)](https://graphql.org/blog/2015-09-14-graphql/), [Source: gRPC 1.0 announcement (August 2016)](https://grpc.io/blog/ga-announcement/)
- Unlocks: [[MCP]], [[Docker and containers]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"SSH and remote machines":{t:"castle",md:`# SSH and remote machines
SSH is an encrypted terminal to another computer. ssh user@host gives you a shell on a server; the same key pair authenticates you to GitHub. Once you can SSH somewhere, everything in the Dark Age works there too, including running an agent on a remote box.
**History.** SSH was written by Tatu Ylonen at Helsinki University of Technology and published in July 1995, after a password sniffer was found on the university network; OpenSSH (first shipped with OpenBSD in December 1999) is what every Mac and Linux ships.
**Try in five minutes.** ssh-keygen -t ed25519, then gh ssh-key add ~/.ssh/id_ed25519.pub, then ssh -T git@github.com.
- Docs: [OpenSSH manual](https://www.openssh.com/manual.html), [GitHub: connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh), [Source: SSH Academy, SSH history](https://www.ssh.com/academy/ssh), [Source: Ylonen, SSH: Secure Login Connections over the Internet (USENIX 1996)](https://www.usenix.org/legacy/publications/library/proceedings/sec96/full_papers/ylonen/), [Source: OpenSSH project history](https://www.openssh.org/history.html)
- Unlocks: [[Cloud and servers]], [[Docker and containers]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"YAML in practice: CI and Compose":{t:"castle",md:`# YAML in practice: CI and Compose
YAML is data shaped by indentation: a map is key: value, a list is lines starting with a dash, nesting is two spaces. Strings rarely need quotes, which is the trap: no, yes, on and 3:30 can turn into booleans or numbers unless you quote them. One file can hold several documents separated by ---, so a stray separator silently splits your config. CI (GitHub Actions) and Docker Compose chose it because a pipeline is a nested list of steps that people read and diff more often than machines do.
**History.** YAML began in 2001 and the 1.0 spec was published in 2004 by Clark Evans, Oren Ben-Kiki and Ingy dot Net; the 1.2.2 revision (October 2021) clarified the spec without changing it. GitHub Actions became generally available in November 2019 with YAML workflows.
**Try in five minutes.** Read .github/workflows/ci.yml and change the Python version in one place.
- Docs: [GitHub Actions workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions), [Docker Compose file reference](https://docs.docker.com/reference/compose-file/), [Source: YAML 1.0 specification (2004)](https://yaml.org/spec/1.0/), [Source: YAML 1.2.2 specification (revision 2021-10-01)](https://yaml.org/spec/1.2.2/), [Source: GitHub changelog, Actions generally available (November 2019)](https://github.blog/changelog/2019-11-11-github-actions-is-generally-available/)
- Unlocks: [[CI/CD and automation]], [[Docker and containers]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"Docker and containers":{t:"castle",md:`# Docker and containers
A container is a packaged process: your code, its dependencies, and a slice of an operating system, running the same on any machine. A Dockerfile is the recipe; an image is the result; a container is a running copy. It ends 'works on my machine'.
**History.** Chroot arrived with Seventh Edition Unix in 1979; Linux mount namespaces in 2002 (kernel 2.4.19) and cgroups in January 2008 (2.6.24). Docker (Solomon Hykes, dotCloud) was first shown at PyCon in March 2013 and made them usable; Kubernetes (Google, open sourced 2014) made them run in fleets. Much of cloud software today runs in containers.
**Try in five minutes.** Install Docker Desktop or OrbStack. docker run -it python:3.12 python -c 'print(1)'. You just ran Python in a box you did not install.
- Docs: [Docker get started](https://docs.docker.com/get-started/), [OrbStack (lighter on Mac)](https://orbstack.dev), [Dev containers](https://containers.dev), [Source: TUHS, V7 chdir/chroot(2) manual page](https://www.tuhs.org/cgi-bin/utree.pl?file=V7/usr/man/man2/chdir.2), [Source: TUHS, Seventh Edition Unix (January 1979)](https://www.tuhs.org/cgi-bin/utree.pl?file=V7), [Source: mount_namespaces(7), history](https://man7.org/linux/man-pages/man7/mount_namespaces.7.html), [Source: cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7.html), [Source: Docker blog, Docker: Nine Years Young (2022)](https://www.docker.com/blog/docker-nine-years-young/), [Source: Google Cloud, the Kubernetes origin story (2016)](https://cloud.google.com/blog/products/containers-kubernetes/from-google-to-the-world-the-kubernetes-origin-story)
- Unlocks: [[Cloud and servers]], [[CI/CD and automation]], [[Kubernetes and platforms]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"GitHub, pull requests, Pages":{t:"castle",md:`# GitHub, pull requests, Pages
GitHub hosts git repositories and adds the social layer: issues, pull requests (proposed changes with review), Actions (CI), Pages (free static hosting). A PR is how professionals let others check work before it lands; it is also how you check an agent's work.
**History.** GitHub launched in 2008 (pull requests arrived in February 2008), was acquired by Microsoft in 2018, and passed 100 million developers in January 2023. Pull requests turned code review into a habit; Copilot (technical preview June 2021) put a model in the editor; Copilot's coding agent and OpenAI's Codex (2025) now open PRs themselves.
**Try in five minutes.** gh repo create, gh pr create after a branch, then enable Pages. The 22:30 workstream.
- Docs: [GitHub docs](https://docs.github.com/en), [GitHub CLI](https://cli.github.com/manual/), [Pages quickstart](https://docs.github.com/en/pages/quickstart), [Source: GitHub blog, pull requests (February 2008)](https://github.blog/2008-02-23-oh-yeah-there-s-pull-requests-now/), [Source: Microsoft to acquire GitHub (June 2018)](https://news.microsoft.com/2018/06/04/microsoft-to-acquire-github-for-7-5-billion/), [Source: GitHub, 100 million developers and counting (January 2023)](https://github.blog/news-insights/company-news/100-million-developers-and-counting/), [Source: Introducing GitHub Copilot (June 2021)](https://github.blog/2021-06-29-introducing-github-copilot-ai-pair-programmer/), [Source: GitHub Copilot coding agent (May 2025)](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/), [Source: openai/codex repository (April 2025)](https://github.com/openai/codex)
- Unlocks: [[CI/CD and automation]], [[Cloud and servers]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"CI/CD and automation":{t:"castle",md:`# CI/CD and automation
Continuous integration: every push runs the tests and checks in a clean machine. Continuous delivery: passing pushes deploy. GitHub Actions is a YAML file in .github/workflows/. This is where headless agents also live: a PR review bot is claude -p in a workflow.
**History.** CruiseControl (ThoughtWorks) was registered in March 2001, Hudson was renamed Jenkins in January 2011, Travis CI started in 2011, GitHub Actions became generally available in November 2019. CI made 'it works' a machine's opinion instead of a person's.
**Try in five minutes.** Ask Claude: 'add a GitHub Actions workflow that runs python3 python/scores.py and the three DuckDB queries on every push'. Push. Watch the tab.
- Docs: [GitHub Actions quickstart](https://docs.github.com/en/actions/quickstart), [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions), [Source: SourceForge, CruiseControl project (registered 2001-03-23)](https://sourceforge.net/projects/cruisecontrol/), [Source: Jenkins blog, Jenkins! (January 2011)](https://www.jenkins.io/blog/2011/01/29/jenkins/), [Source: travis-ci/travis-ci repository (February 2011)](https://github.com/travis-ci/travis-ci), [Source: GitHub changelog, Actions generally available (November 2019)](https://github.blog/changelog/2019-11-11-github-actions-is-generally-available/)
- Unlocks: [[Headless agents and scheduling]], [[Tests and evals]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"Cloud and servers":{t:"castle",md:`# Cloud and servers
A server is a computer that is always on. The cloud rents you one by the hour (AWS 2006, Azure 2010, GCP 2008) or runs your code without one (serverless: Lambda 2014, Vercel, Cloudflare Workers). For most people's first project, a static host (GitHub Pages) or a small VPS (Hetzner, Fly.io) is enough.
**History.** AWS launched S3 in March and EC2 in August 2006; renting compute by the hour changed who could start a company. Google App Engine followed in April 2008 and Windows Azure went live in February 2010. Serverless (AWS Lambda, November 2014) removed the server from view; today agents can provision all of it with one prompt, which is why understanding the bill matters.
**Try in five minutes.** Deploy the game to GitHub Pages (free). Later: fly launch on the FastAPI endpoint.
- Docs: [AWS getting started](https://aws.amazon.com/getting-started/), [Fly.io docs](https://fly.io/docs/), [Cloudflare Pages](https://developers.cloudflare.com/pages/), [Source: AWS, Announcing Amazon S3 (March 2006)](https://aws.amazon.com/about-aws/whats-new/2006/03/announcing-amazon-s3---simple-storage-service), [Source: AWS, Announcing Amazon EC2 beta (August 2006)](https://aws.amazon.com/about-aws/whats-new/2006/08/24/announcing-amazon-elastic-compute-cloud-amazon-ec2---beta/), [Source: Google blog, Developers, start your engines (April 2008)](https://googleblog.blogspot.com/2008/04/developers-start-your-engines.html), [Source: Microsoft, Windows Azure general availability (February 2010)](https://blogs.microsoft.com/blog/2010/02/01/windows-azure-general-availability/), [Source: AWS, Introducing AWS Lambda (November 2014)](https://aws.amazon.com/about-aws/whats-new/2014/11/13/introducing-aws-lambda/)
- Unlocks: [[Kubernetes and platforms]], [[Cost, tokens and model choice]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"LLM versus harness":{t:"imperial",md:`# LLM versus harness
The LLM is the model: text in, text out, no memory, no hands. The harness is everything around it: the loop that calls it repeatedly, the tools it can run (bash, edit file), the files it reads first (AGENTS.md), permissions, hooks, memory. Claude Code, Codex CLI, Cursor are harnesses. Most of the difference in results comes from the harness and what you put in it, not from the model.
**History.** Transformer 2017 (Google, 'Attention is all you need'). GPT-3 2020. ChatGPT November 2022. Claude March 2023. MCP November 2024. Agentic coding harnesses: Cursor's agent mode November 2024, Claude Code February 2025, Codex CLI April 2025. AGENTS.md August 2025.
**Try in five minutes.** Run claude in the template folder and ask 'what files did you read before answering?'. That list is the harness.
- Docs: [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents), [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works), [Source: Attention Is All You Need (arXiv, June 2017)](https://arxiv.org/abs/1706.03762), [Source: Language Models are Few-Shot Learners (arXiv, May 2020)](https://arxiv.org/abs/2005.14165), [Source: OpenAI, Introducing ChatGPT (November 2022)](https://openai.com/index/chatgpt/), [Source: Anthropic, Introducing Claude (March 2023)](https://www.anthropic.com/news/introducing-claude), [Source: Anthropic, Introducing the Model Context Protocol (November 2024)](https://www.anthropic.com/news/model-context-protocol), [Source: Cursor changelog 0.43 (November 2024)](https://cursor.com/changelog/0-43-x), [Source: Anthropic, Claude 3.7 Sonnet and Claude Code (February 2025)](https://www.anthropic.com/news/claude-3-7-sonnet), [Source: openai/codex repository (April 2025)](https://github.com/openai/codex), [Source: openai/agents.md repository (August 2025)](https://github.com/openai/agents.md)
- Unlocks: [[Context window and prompts]], [[Your harness: AGENTS.md, CLAUDE.md, dotfiles for agents]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Context window and prompts":{t:"imperial",md:`# Context window and prompts
The context window is the model's working memory for one conversation: everything it can see right now, in tokens. Files, instructions, tool output all compete for it. Specificity, scope and 'what not to touch' win because the model cannot read your mind and cannot remember last week without a file.
**History.** GPT-3 had a 2,048-token window (2020); Claude went to 100k in May 2023; Gemini 1.5 ran a million tokens in February 2024 and Claude Sonnet 4 in August 2025. Bigger windows did not remove the need for good instructions; they moved it to what you load.
**Try in five minutes.** Give the same task twice: 'make it cooler' and 'add a purple badge, keep stats, touch nothing else'. Compare the diff.
- Docs: [Claude prompt engineering](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview), [Claude Code best practices](https://code.claude.com/docs/en/best-practices), [Source: GPT-3 paper, section 2 (context window of 2048 tokens)](https://arxiv.org/abs/2005.14165), [Source: Anthropic, Introducing 100K context windows (May 2023)](https://www.anthropic.com/news/100k-context-windows), [Source: Google, Gemini 1.5 (February 2024)](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/), [Source: Claude Sonnet 4 1M token context (August 2025)](https://claude.com/blog/1m-context)
- Unlocks: [[AGENTS.md]], [[Agent Skills standard]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Your harness: AGENTS.md, CLAUDE.md, dotfiles for agents":{t:"imperial",md:`# Your harness: AGENTS.md, CLAUDE.md, dotfiles for agents
Your standing instructions, per repo and per machine, in files the agent reads before it starts. AGENTS.md for every agent; CLAUDE.md importing it for Claude; .claude/settings.json for permissions and hooks; ~/.claude/ for personal defaults. This is your operating model, versioned.
**History.** Cursor's rules files came first, then CLAUDE.md with Claude Code (February 2025) and AGENTS.md (August 2025, stewarded since December 2025 by the Agentic AI Foundation under the Linux Foundation). In one year instruction files went from a hack to a standard read by dozens of tools and used in tens of thousands of repos.
**Try in five minutes.** Edit AGENTS.md, add 'always end with one line: what changed'. Next session, check it does.
- Docs: [agents.md](https://agents.md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Settings](https://code.claude.com/docs/en/settings), [Source: Anthropic, Claude 3.7 Sonnet and Claude Code (February 2025)](https://www.anthropic.com/news/claude-3-7-sonnet), [Source: openai/agents.md repository (August 2025)](https://github.com/openai/agents.md), [Source: Linux Foundation, formation of the Agentic AI Foundation (December 2025)](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- Unlocks: [[Agent Skills standard]], [[Hook]], [[MCP]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Git hooks":{t:"dark",md:`# Git hooks
Scripts git runs at moments in its own lifecycle: pre-commit before a commit is written, commit-msg to check the message, pre-push before anything leaves the machine, post-checkout and post-merge after a switch. A non-zero exit aborts the step. They live in .git/hooks (not versioned), or in a folder you commit and point at with core.hooksPath; the pre-commit framework and lefthook manage them from a config file.
**History.** Hooks have been in git since the first releases (the githooks manual page lists thirty of them); core.hooksPath arrived in Git 2.9 (June 2016) so a team can version its hooks; pre-commit (Yelp, 2014) and lefthook (Evil Martians, 2019) turned them into a one-line install.
**Try in five minutes.** In this repo: \`mkdir -p .githooks && printf '#!/bin/sh
uv run ruff check vibemap tests tools
' > .githooks/pre-commit && chmod +x .githooks/pre-commit && git config core.hooksPath .githooks\`. Then commit something with a lint error and watch it refuse.
- Docs: [githooks manual](https://git-scm.com/docs/githooks), [Pro Git, Customizing Git: Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks), [pre-commit framework](https://pre-commit.com/), [lefthook](https://github.com/evilmartians/lefthook), [Source: githooks manual, default hooks directory and core.hooksPath](https://git-scm.com/docs/githooks), [Source: Git 2.9.0 release notes (core.hooksPath)](https://github.com/git/git/blob/master/Documentation/RelNotes/2.9.0.txt)
- Unlocks: [[Agent hooks]], [[CI/CD and automation]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Agent hooks":{t:"imperial",md:`# Agent hooks
The same idea inside a coding agent: shell commands (or HTTP endpoints, MCP tools, prompts) that Claude Code runs at points in its lifecycle. PreToolUse can block a tool call, PostToolUse can react to an edit (this repo backs up data/ after every edit), UserPromptSubmit can add context, Stop can keep the agent working, SessionStart can load state. Configured under hooks in settings.json, filtered by a matcher, fed JSON on stdin; exit 2 blocks, JSON on stdout decides.
**History.** Claude Code documents thirty-two hook events, from SessionStart and PreToolUse to PreCompact and WorktreeCreate, in five configuration scopes (user, project, local, managed policy, plugins); the vibe-map repo uses one PostToolUse hook and Tom's toolbox ships guard hooks as a template.
**Try in five minutes.** Open .claude/settings.json in this repo, read the PostToolUse hook, then add a PreToolUse hook with matcher Bash whose command is \`jq -e '.tool_input.command | test("rm -rf") | not' >/dev/null || exit 2\`. Ask Claude to delete a folder with rm -rf and watch the refusal.
- Docs: [Claude Code hooks reference](https://code.claude.com/docs/en/hooks), [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide), [This repo's hook](https://github.com/tpetedb/vibe-map/blob/main/.claude/settings.json), [Source: Claude Code hooks reference (events, scopes, exit codes)](https://code.claude.com/docs/en/hooks)
- Unlocks: [[Security and permissions]], [[Headless agents and scheduling]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Interfaces: GUI, TUI, CLI, API":{t:"dark",md:`# Interfaces: GUI, TUI, CLI, API
Four ways to talk to a program. A CLI takes a command and flags and prints text (\`vibe status\`, git, uv). A TUI draws a screen inside the terminal you can move around in (\`just start\`, htop, the Claude Code chat). A GUI is windows and a pointer (Obsidian, Zed, the browser game). An API is for programs, not people: HTTP endpoints that return JSON (GitHub's REST API), or a protocol two programs agree on, such as MCP between an agent and a tool server and ACP between an editor and an agent. One program can have all four: Obsidian has a GUI, a URI scheme and a CLI.
**History.** The command line came with time-sharing systems and Unix (1969); full-screen terminal programs followed once terminals could address the screen, with vi (1976) and the curses library (1978); the graphical desktop was prototyped on the Xerox Alto (1973) and sold with the Macintosh (1984); REST named the web's API style in Roy Fielding's dissertation (2000); MCP was published by Anthropic on 25 November 2024 and ACP by Zed in August 2025.
**Try in five minutes.** Run the same thing four ways: \`uv run vibe status\` (CLI), \`just start\` then Campaign map (TUI), the Roadmap button in game/vibe-map.html (GUI), and \`gh api repos/tpetedb/vibe-map\` (API). Notice what each one is good at.
- Docs: [Textual, TUIs in Python](https://textual.textualize.io/), [click, CLIs in Python](https://click.palletsprojects.com/), [GitHub REST API](https://docs.github.com/en/rest), [Model Context Protocol](https://modelcontextprotocol.io/), [Agent Client Protocol](https://agentclientprotocol.com/), [Source: Roy Fielding, Architectural Styles and the Design of Network-based Software Architectures (2000)](https://ics.uci.edu/~fielding/pubs/dissertation/top.htm), [Source: Anthropic, Introducing the Model Context Protocol (25 November 2024)](https://www.anthropic.com/news/model-context-protocol), [Source: Zed, Bring your own agent to Zed (ACP, August 2025)](https://zed.dev/blog/bring-your-own-agent-to-zed), [Source: Wikipedia, Text-based user interface (curses, 1978)](https://en.wikipedia.org/wiki/Text-based_user_interface), [Source: Wikipedia, Xerox Alto (1973) and Macintosh (1984)](https://en.wikipedia.org/wiki/Xerox_Alto)
- Unlocks: [[Unix and the terminal]], [[MCP]], [[Building and consuming APIs]]
- Age: Dark Age · Level: Intern
#tech #dark`},
"Subagents and multi-agent":{t:"imperial",md:`# Subagents and multi-agent
A subagent is a second model instance with its own instructions and context, called by the first for a bounded job (scorekeeper). Teams of agents split large work; the risk is coordination cost and compounding errors, so keep each one's job small and testable.
**History.** AutoGPT (March 2023) showed loops of agents; they mostly wandered. 2025 harnesses added typed subagents with their own tools and permissions, which is what made delegation reliable.
**Try in five minutes.** The 23:00 workstream: create the scorekeeper, run it, read its note.
- Docs: [Subagents](https://code.claude.com/docs/en/sub-agents), [Source: Significant-Gravitas/AutoGPT repository (created March 2023)](https://github.com/Significant-Gravitas/AutoGPT)
- Unlocks: [[Headless agents and scheduling]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Headless agents and scheduling":{t:"imperial",md:`# Headless agents and scheduling
claude -p runs the agent as a command: prompt in, result out, no chat. Put it in launchd, cron, a GitHub Action or a webhook and you have automation that reasons. This is where the leverage is for a business: one boring job, done on a timer, forever.
**History.** Cron is older than almost everything in this tree: its manual page is in Sixth Edition Unix, dated October 1974. The new part is that the scheduled job can now read a mailbox, decide, and write a note. Programmatic agents (2025) are the successor of the scheduled script.
**Try in five minutes.** The 23:00 workstream: schedule the scorekeeper for 08:00.
- Docs: [Run Claude Code programmatically](https://code.claude.com/docs/en/headless), [launchd tutorial](https://www.launchd.info), [Source: TUHS, V6 cron(8) manual page](https://www.tuhs.org/cgi-bin/utree.pl?file=V6/usr/man/man8/cron.8)
- Unlocks: [[Tests and evals]], [[Cost, tokens and model choice]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Tests and evals":{t:"imperial",md:`# Tests and evals
A test runs code and checks the result. An eval does the same for an agent: a set of tasks with known good answers, run after every change to AGENTS.md or a skill. Without tests, an agent will happily make things worse faster.
**History.** JUnit was written by Kent Beck and Erich Gamma on a flight to OOPSLA in 1997, pytest's lineage starts in 2004, property-based testing arrived with QuickCheck (ICFP 2000). Model evals became an engineering discipline around 2023; today teams keep an eval set next to their instruction files.
**Try in five minutes.** Ask Claude: 'write pytest tests for python/scores.py and run them'. Then break scores.py and watch them fail.
- Docs: [pytest](https://docs.pytest.org), [Anthropic: evals guide](https://docs.claude.com/en/docs/test-and-evaluate/develop-tests), [Source: Martin Fowler, xUnit (Kent Beck's account of JUnit's origin)](https://martinfowler.com/bliki/Xunit.html), [Source: pytest history](https://docs.pytest.org/en/stable/history.html), [Source: QuickCheck (Claessen and Hughes, ICFP 2000)](https://www.cse.chalmers.se/~rjmh/QuickCheck/)
- Unlocks: [[CI/CD and automation]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Security and permissions":{t:"imperial",md:`# Security and permissions
Agents run commands. Give them the least they need: a folder, a permission list, hooks that veto dangerous commands, secrets in the environment, and a git history to undo. Prompt injection (instructions hidden in data the agent reads) is the new phishing.
**History.** Least privilege dates to Saltzer and Schroeder, 1975: 'every program and every user of the system should operate using the least set of privileges necessary to complete the job'. It applies unchanged to agents; the harness enforces it with permissions and hooks.
**Try in five minutes.** Open .claude/settings.json; add a PreToolUse hook that blocks 'rm -rf'. Test it.
- Docs: [Claude Code permissions](https://code.claude.com/docs/en/permissions), [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/), [Source: Saltzer and Schroeder, The Protection of Information in Computer Systems (1975)](https://web.mit.edu/Saltzer/www/publications/protection/)
- Unlocks: [[Cost, tokens and model choice]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Cost, tokens and model choice":{t:"imperial",md:`# Cost, tokens and model choice
You pay per token in and out. A big context and a strong model cost more per call; a scheduled job that runs hourly multiplies it. Pick the smallest model that passes your evals, cache what repeats, and read the bill weekly.
**History.** Per-token pricing arrived with the OpenAI API (2020). Prices per token for equal capability have fallen steeply since; usage rose faster.
**Try in five minutes.** In Claude Code, /cost after a session. Write the number in your vault.
- Docs: [Claude Code costs](https://code.claude.com/docs/en/costs), [Claude pricing](https://claude.com/pricing), [Source: OpenAI API announcement (June 2020)](https://openai.com/index/openai-api/)
- Unlocks: [[The future perspective]]
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"Kubernetes and platforms":{t:"future",md:`# Kubernetes and platforms
Kubernetes runs containers across many machines: scheduling, scaling, self-healing. Most knowledge workers never need to touch it; they need to know it is why 'the cloud' can scale, and that agents can now write its YAML for them.
**History.** Google's internal Borg (running containers for over a decade by 2016) became Kubernetes (open sourced 2014). In the 2020s it became the default substrate of cloud software; platform engineering teams now hide it behind internal tools.
**Try in five minutes.** Read one Deployment YAML and identify: image, replicas, port.
- Docs: [Kubernetes basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/), [Source: Google Cloud, the Kubernetes origin story (2016)](https://cloud.google.com/blog/products/containers-kubernetes/from-google-to-the-world-the-kubernetes-origin-story), [Source: Kubernetes blog, Borg: the predecessor to Kubernetes (2015)](https://kubernetes.io/blog/2015/04/borg-predecessor-to-kubernetes/)
- Unlocks: [[The future perspective]]
- Age: Future Age · Level: Expert
#tech #future`},
"The future perspective":{t:"future",md:`# The future perspective
Every age here shortened the distance between an idea and a working thing: the terminal (hours), languages (days), the web (weeks to ship), the cloud (minutes to deploy), agents (a sentence). What does not change: someone has to know what they want, check the result, and own the consequences. For a knowledge worker: learn to specify, verify and version. For a founder: your moat moves from building to judgement, data and distribution. Expect agents to run inside every tool, models on the laptop, memory as files you own, and audits of what agents did as a routine compliance question.
**History.** 1969 Unix, 1991 Python and the web, 2005 git, 2013 Docker, 2017 Transformer, 2022 ChatGPT, 2024 MCP, 2025 coding agents and AGENTS.md. The interval keeps shrinking.
**Try in five minutes.** Write vault/Camp/Bets.md: three things you think will be true in two years, dated. Reread in two years.
- Docs: [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents), [Agentic AI Foundation](https://agents.md), [Source: W3C, The original HTTP as defined in 1991](https://www.w3.org/Protocols/HTTP/AsImplemented.html), [Source: Anthropic, Introducing the Model Context Protocol (November 2024)](https://www.anthropic.com/news/model-context-protocol)
- Age: Future Age · Level: Expert
#tech #future`},
"Semantic Versioning":{t:"castle",md:`# Semantic Versioning
A version number that makes a promise: MAJOR.MINOR.PATCH, where a MAJOR change breaks something, MINOR adds, PATCH fixes. Read one and you know whether an upgrade can hurt you; write one and you have to know what you changed. Before 1.0.0 anything may change, which is what this repo's 0.2.0 says out loud.
**History.** Tom Preston-Werner, cofounder of GitHub, wrote the spec. The 1.0.0 text dates from September 2011; 2.0.0, the version everyone links, was merged on 18 June 2013. It is written with the RFC 2119 keywords (MUST, SHOULD, MAY), so a version is something a tool can check, not a feeling.
**Try in five minutes.** uv run vibe --version, then open pyproject.toml and vibemap/__init__.py: the number lives in both. With the semver skill, decide what 0.3.0 would need.
- Docs: [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html), [Source: semver.org, About (authored by Tom Preston-Werner)](https://semver.org/), [Source: semver/semver, merge of release-2.0 (18 June 2013)](https://github.com/semver/semver/commit/7c834b3f3a4940d77ab593bc32583004d6a426a9), [Source: semver/semver, the commit tagged v1.0.0 (September 2011)](https://github.com/semver/semver/commit/ec80195ed310aab3ae1f1ce797b7ba88b4246d27)
- Unlocks: [[Changelogs (Keep a Changelog)]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"Changelogs (Keep a Changelog)":{t:"castle",md:`# Changelogs (Keep a Changelog)
A CHANGELOG.md lists what changed for the person using your thing: newest first, one section per version with its date, six kinds of change (Added, Changed, Deprecated, Removed, Fixed, Security) and an Unreleased section on top. It is not the git log. Commits are for the people who wrote them; the changelog is for everyone else.
**History.** Olivier Lacan started Keep a Changelog on 31 May 2014 as a CHANGELOG that documents itself, under the motto 'Don't let your friends dump git logs into changelogs.' Version 1.0.0 followed on 20 June 2017, 1.1.0 on 15 February 2019 and 2.0.0 on 7 June 2026. The site is MIT licensed; this repo follows 1.1.0.
**Try in five minutes.** cat CHANGELOG.md. Then make one change to the repo and add its line under Unreleased in the same commit.
- Docs: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), [Source: keep-a-changelog, its own CHANGELOG.md (dated releases since 2014-05-31)](https://github.com/olivierlacan/keep-a-changelog/blob/main/CHANGELOG.md), [Source: Keep a Changelog 2.0.0 (2026-06-07)](https://keepachangelog.com/en/2.0.0/)
- Unlocks: [[CI/CD and automation]]
- Age: Castle Age · Level: Medior
#tech #castle`},
"Architecture decision records":{t:"imperial",md:`# Architecture decision records
An ADR is one short file per decision: Title, Status, Context (the forces), Decision (we will ...), Consequences (all of them). Numbered, never deleted, superseded instead. It is the memory an agent cannot infer from the code: why the repo is MIT, why the game is one file, why XP is verified. AGENTS.md says what the rules are; docs/adr/ says why.
**History.** Michael Nygard published Documenting Architecture Decisions on 15 November 2011: a page per decision, kept in the repo with the code, in a form borrowed from Alexandrian patterns. The GitHub adr organisation (adr.github.io) collects the templates and tools that followed; MADR, the Markdown variant with drivers and options, reached 4.0.0 in September 2024.
**Try in five minutes.** ls docs/adr, then cat docs/adr/0004-quests-verify-real-work.md. Write ADR 0005 with the adr skill for the next thing you decide.
- Docs: [ADR home (the GitHub adr organisation)](https://adr.github.io), [MADR](https://adr.github.io/madr/), [Source: Nygard, Documenting Architecture Decisions (15 November 2011)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), [Source: MADR 4.0.0 (September 2024)](https://adr.github.io/madr/)
- Age: Imperial Age · Level: Senior
#tech #imperial`},
"README and the quickstart":{t:"feudal",md:`# README and the quickstart
The README is the front page: what this is, for whom, and the commands that get a stranger from clone to a working run, on the first screen. GitHub shows it under the file list, agents read it first, and it is the last thing maintainers update, which is why every command in it must be one you just ran.
**History.** The name is older than most of this tree. Seventh Edition Unix (1979) shipped /usr/doc/README, a few lines telling you how to format the manual's papers, and DECUS library tapes for the PDP-10 carried READ.ME files of 'random notes' for whoever installed the software. Markdown and GitHub turned README.md into the page a repository opens on; makeareadme.com is the modern checklist.
**Try in five minutes.** head -30 README.md, then run the first Quickstart command exactly as written. If it fails, fix the README, not the reader.
- Docs: [Make a README](https://www.makeareadme.com), [GitHub docs, About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), [Source: TUHS, V7 /usr/doc/README (listed 1979-01-11)](https://www.tuhs.org/cgi-bin/utree.pl?file=V7/usr/doc/README), [Source: Trailing-Edge PDP-10 archive, DECUS UCI LISP READ.ME](http://pdp-10.trailing-edge.com/decuslib10-04/01/43,50322/read.me.html), [Source: GitHub docs, About READMEs (often the first item a visitor sees)](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- Unlocks: [[GitHub, pull requests, Pages]]
- Age: Feudal Age · Level: Junior
#tech #feudal`},
"Tech tree":{t:"future",md:`# Tech tree
The roadmap from intern to expert, Age of Empires style. Each age has a level; each technology says what it is, real history, a five-minute try, docs, and what it unlocks.
**Dark Age (Intern).** The terminal and files. Everything else is built on this; nobody skips it, everybody wishes they had learned it earlier. [[Unix and the terminal]], [[Bash and shell scripts]], [[zsh and your shell config]], [[Files, folders and paths]], [[Dotfiles]], [[Config formats: JSON, YAML, TOML, Markdown]], [[.env files and secrets]], [[localhost and ports]], [[Git]], [[Git hooks]], [[Interfaces: GUI, TUI, CLI, API]]
**Feudal Age (Junior).** Languages and data. You can now make the machine do a specific thing and keep the result. [[Python]], [[TOML in practice: pyproject.toml]], [[Python libraries: what they are for]], [[SQL and DuckDB]], [[HTML, CSS and JavaScript]], [[Other languages and what they are for]], [[Markdown and Obsidian]], [[Obsidian features]], [[Data: files, schemas, warehouses]], [[README and the quickstart]]
**Castle Age (Medior).** Networks and shipping. Your thing runs somewhere other than your laptop, repeatably. [[HTTP and APIs]], [[Building and consuming APIs]], [[SSH and remote machines]], [[YAML in practice: CI and Compose]], [[Docker and containers]], [[GitHub, pull requests, Pages]], [[CI/CD and automation]], [[Cloud and servers]], [[Semantic Versioning]], [[Changelogs (Keep a Changelog)]]
**Imperial Age (Senior).** The AI harness. You stop typing code and start directing agents, with guardrails you wrote. [[LLM versus harness]], [[Context window and prompts]], [[Your harness: AGENTS.md, CLAUDE.md, dotfiles for agents]], [[AGENTS.md]], [[Agent Skills standard]], [[Hook]], [[Agent hooks]], [[MCP]], [[Subagents and multi-agent]], [[Headless agents and scheduling]], [[Tests and evals]], [[Security and permissions]], [[Cost, tokens and model choice]], [[Architecture decision records]]
**Future Age (Expert).** What is coming, what stays the same, and what a knowledge worker or founder should actually do about it. [[Kubernetes and platforms]], [[Claude and Obsidian]], [[The future perspective]]
- See also: [[Resources]], [[Template repo]], [[Tonight]]
#overview`}