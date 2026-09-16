---
title: "HTTP and APIs"
date: 2026-09-16
tags: [tech, castle]
---
# HTTP and APIs

HTTP is request and response: a URL, a method (GET, POST), headers, a body, a status code (200, 404, 500). An API is an HTTP endpoint that returns data instead of a page, usually JSON. Every AI model you call is an HTTP API; MCP is a layer on top of the same idea.

**History.** HTTP 0.9 in 1991, HTTP/1.1 in 1997 (RFC 2068), HTTP/2 in 2015 (RFC 7540). REST was named in Roy Fielding's 2000 dissertation. The OpenAI API (June 2020) made calling a model one POST request.

**Try in five minutes.** curl -s https://api.github.com/repos/duckdb/duckdb | head -20. You just used an API.

- Docs: [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview), [curl](https://curl.se/docs/manual.html), [Postman](https://learning.postman.com), [Source: W3C, The original HTTP as defined in 1991](https://www.w3.org/Protocols/HTTP/AsImplemented.html), [Source: RFC 2068, HTTP/1.1 (January 1997)](https://www.rfc-editor.org/rfc/rfc2068), [Source: RFC 7540, HTTP/2 (May 2015)](https://www.rfc-editor.org/rfc/rfc7540), [Source: Fielding, Architectural Styles and the Design of Network-based Software Architectures (2000)](https://ics.uci.edu/~fielding/pubs/dissertation/top.htm), [Source: OpenAI API announcement (June 2020)](https://openai.com/index/openai-api/)
- Unlocks: [[Building and consuming APIs]], [[MCP (Model Context Protocol)]], [[SSH and remote machines]]
- Age: Castle Age · Level: Medior

<!-- generated from tools/tech.py; edit there -->

Back to [[Tech tree]]

#tech #castle
