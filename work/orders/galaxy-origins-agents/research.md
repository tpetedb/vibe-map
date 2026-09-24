# Agent and future origins

Read on 2026-09-22. These are documented milestones, not claims that an idea was invented there first. The topic histories remain unchanged. The historical-attribution audit rejected present company addresses as evidence for earlier events. Fourteen origins now describe documented online publications or announcements at the-internet. Only MIT's 1975 paper and SRI's 1962 report retain Earth locations, supported by historical evidence. No private development event was relabelled as an online event.

| Topics | Opened primary source and evidence |
| --- | --- |
| agenthooks, hooks | [Anthropic's release commit](https://github.com/anthropics/claude-code/commit/390f11039c4986f2172aae21c6380d2b5a8b251e), opened through GitHub's commits API: author date 2025-06-30, CHANGELOG.md patch adds version 1.0.38 and the release of hooks. The linked hook documentation supplies lifecycle semantics. No GitHub release tag exists for this version. |
| agentsmd | [Linux Foundation's announcement](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation), 2025-12-09, AGENTS.md section explicitly says OpenAI released it in August 2025 and describes project-specific guidance. |
| context | [Anthropic's announcement](https://www.anthropic.com/news/100k-context-windows), 2023-05-11, first paragraph gives the expansion from 9K to 100K tokens. |
| cost, harness | [Claude 3.7 Sonnet and Claude Code](https://www.anthropic.com/news/claude-3-7-sonnet), 2025-02-24. Price paragraph specifies $3/$15 per million input/output tokens, including thinking. Claude Code section describes limited research preview and file, test, git and command-line tools. This is a pricing milestone, not an unsupported claim that token billing began in 2020. |
| llm | [arXiv submission](https://arxiv.org/abs/1706.03762), first submitted 2017-06-12, named authors and Transformer abstract. The linked PDF supplies Google Brain and Google Research affiliations. This origin now describes online paper publication, not its research or conference location. |
| mcp | [Anthropic's announcement](https://www.anthropic.com/news/model-context-protocol), 2024-11-25, open sourcing the protocol and its connections to data and tools. |
| meta | [Engelbart's report](https://dougengelbart.org/content/view/138), October 1962, SRI Summary Report AFOSR-3223. Introduction 1a9 recommends spending capability gains on subsequent gains. [Engelbart and English 1968](https://dougengelbart.org/content/view/140/), reference 6c, explicitly identifies this exact October 1962 report as SRI, Menlo Park, California. This historical site citation is also added to the topic sources. The older /pubs/ URL failed in the reader, so the working institute copy is used. |
| prompting | [Anthropic's prompt engineering article](https://www.anthropic.com/news/prompt-engineering-for-business-performance), 2024-02-29. Three tips: clear task instructions, step-by-step reasoning, examples and prompt chaining. |
| promptstructure | [Prompt generator announcement](https://claude.com/blog/prompt-generator), 2024-05-20. Templates place variable inputs between XML tags; the generator itself uses tags to delimit sections. Old Anthropic URL redirects here. |
| security | [MIT's paper metadata](https://web.mit.edu/Saltzer/www/publications/protection/Meta.html) records revision/copyright 1975 and MIT affiliation. Its [front page](https://web.mit.edu/Saltzer/www/publications/protection/) names Saltzer and Schroeder and the title; [Basic Principles](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html) includes least privilege. Claim is publication, not invention of least privilege. |
| skills | [Anthropic's engineering article](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), 2025-10-16, introduces folders of resources and SKILL.md. December 18 update records the later open standard; the origin describes the October introduction. |
| subagents | [Anthropic's engineering article](https://www.anthropic.com/engineering/multi-agent-research-system), 2025-06-13, lead research agent creates parallel subagents with their own context windows. Does not claim invention of multi-agent systems. |
| symbols | [Gruber's Markdown release](https://daringfireball.net/2004/03/introducing_markdown), 2004-03-15, names readable plain-text syntax and HTML conversion. Markdown is one of this topic's symbol systems. Does not attribute IRC, shell escapes or all agent chat symbols to Gruber. |
| future | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), 2024-12-19. Distinguishes predefined workflow paths from model-directed tool use. A dated publication anchors the perspective; predictions are not recorded as historical events. |

## Verification

Before origins: all three new tests failed (missing primary origins, missing actor evidence, and MCP CLI lacking year).
After origins: new tests pass; the first combined run caught stale generated game payload, as intended. Regeneration follows before final acceptance.

Final order check: `PATH="$PWD/.venv/bin:$PATH" just work-check galaxy-origins-agents` prints OK. c1 passes 58 focused tests; c2 reports no origin defects; c3 passes lint, formatting, style, sink guard and all non-browser/non-integration tests; c4 verifies six generators. Independent source judgment and full browser verification remain pending.

## Historical-attribution correction

The independent audit reproduced 13 unsupported Earth assignments. The new regression failed on `llm` at `google-mountain-view` before the data correction. All 13 now use `the-internet` with explicit online announcement/publication wording; the already-online `symbols` line also states its announcement scope explicitly. The dates and original event sources remain except `llm`, which now cites arXiv's dated submission directly. `agentsmd` describes the Linux Foundation's online report of OpenAI's August release, without borrowing its December San Francisco dateline.

The actor assertion is now keyed by topic, so each expected actor remains mandatory without equating every online event with John Gruber. One primary origin, unique places per topic, HTTPS, and year consistency checks remain. A new assertion reserves Earth locations for the two historically supported papers and requires explicit online wording for every other topic. No reviewer notes were edited.

Re-review the corrected 14 online event lines and the new SRI location source. The earlier review's statement that institution IDs merely identify organisations is superseded by this correction; its note remains preserved as review history. Final review, full verification, commit and train integration remain pending.
