---
title: "Artifacts"
date: 2026-09-17
tags: [concept]
---
# Artifacts

Things on the island that explain one idea each. Walk up to the yellow ring and press Inspect; a found one turns green. The CLI learns about them through the progress code.

- not yet: **The cafe** (the terrace of the Hospitality Hub): client, server, protocol. You are the client, Rolinda is the server, the menu is the protocol. You send a request; she sends a response with a status code and a body. Every API on the internet is this cafe with more tables. See [[HTTP and APIs]], [[Building and consuming APIs]].
- not yet: **The fountain** (the fountain by the lake): a cache. The first cup takes a walk to the well. The fountain keeps a copy, so the second cup is instant. A cache is a remembered answer: fast, cheap, and wrong once the world moves on. Claude's prompt cache does the same for the start of your prompt. See [[HTTP and APIs]], [[Context window and prompts]], [[Cost, tokens and model choice]].
- not yet: **The well** (the stone well): a database. Pulling a bucket is a query. Without a rope marked in metres you go down the whole well; an index is that rope. Two buckets at once is a transaction: both come up, or neither. See [[SQL and DuckDB]], [[Data - files, schemas, warehouses]].
- not yet: **The lighthouse** (the lighthouse on the point): DNS, names to addresses. Ships know the harbour by name; packets need a number. The lighthouse is the resolver: it turns tpetedb.github.io into an address and remembers the answer for a while. It never carries you anywhere. See [[localhost and ports]], [[HTTP and APIs]].
- not yet: **The dock** (the harbour): containers and deployment. A crate packed here opens the same on every island: the code, its runtime and its libraries in one box. Build packs it, push ships it, run unloads it. That is why it works on the other machine too. See [[Docker and containers]], [[CI-CD and automation]].
- not yet: **The windmill** (the windmill on the hill): schedules and cron. The mill turns without you. A schedule is five fields (minute, hour, day, month, weekday) and a command; a hook is the same command fired by an event instead of a clock. Both are how agents work while you sleep. See [[Headless agents and scheduling]], [[CI-CD and automation]].
- not yet: **The balloon** (the hot-air balloon): the cloud, rented by the hour. The cloud is a computer you rent and never see. The meter runs while the balloon is up, whether you look at it or not; region, size, storage and traffic are four meters, not one. Landing it is the only way to stop paying. See [[Cloud and servers]], [[Cost, tokens and model choice]].
- not yet: **The mountain** (the mountain in the north): the stack, layer by layer. Hardware at the foot, then the operating system, the runtime, the libraries, your app, and the agent at the summit reading and writing all of it. Every layer stands on the one below; a bug can live on any of them. See [[Unix and the terminal]], [[Python]], [[Python libraries - what they are for]].
- not yet: **The market stall** (the stall by the Hub): an API and its documentation. The menu on the stall is the API: what you may ask for, in which words, and what comes back. Order without reading it and you get a 400. Show your key and you get the good stuff. See [[Building and consuming APIs]], [[Security and permissions]].
- not yet: **The bridge** (the bridge over the river): an integration, MCP. On the other bank lives a tool the agent does not have. The bridge has a rulebook: first ask what is over there, then call it by name with the arguments it expects. That rulebook is MCP, and every connector is one more bridge. See [[MCP (Model Context Protocol)]], [[Security and permissions]].

Back to [[Tonight]]

#concept
