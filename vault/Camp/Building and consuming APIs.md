---
title: "Building and consuming APIs"
date: 2026-09-16
tags: [tech, net]
---
# Building and consuming APIs

Consuming: read the docs, get a key, make a request, parse JSON. Building: FastAPI turns a Python function into an endpoint in five lines. Keys are secrets: environment variables, never in git. This is the bridge between your data and every other system.

**History.** SOAP was designed from 1998 and published in 1999; REST-with-JSON replaced it in the 2010s; GraphQL (open sourced 2015) and gRPC (announced 2015, 1.0 in 2016) added alternatives. Today the agent-facing version of an API is an MCP server.

**Try in five minutes.** Ask Claude: 'wrap workspace/sql/per_player.sql in a FastAPI endpoint /players and run it on localhost:8000'. Open the URL.

- Docs: [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/), [httpx](https://www.python-httpx.org), [Twelve-Factor config](https://12factor.net/config), [Source: Don Box, A Brief History of SOAP (2001)](https://www.xml.com/pub/a/ws/2001/04/04/soap.html), [Source: graphql.org, GraphQL: A data query language (September 2015)](https://graphql.org/blog/2015-09-14-graphql/), [Source: gRPC 1.0 announcement (August 2016)](https://grpc.io/blog/ga-announcement/)
- Unlocks: [[MCP (Model Context Protocol)]], [[Docker and containers]]
- Shelf: Web, networks and APIs · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #net
