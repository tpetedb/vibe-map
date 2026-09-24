---
title: "Designing an HTTP API"
date: 2026-09-24
tags: [tech, net]
generated: 3690f7169999
---
# Designing an HTTP API

Designing an HTTP API well starts with using HTTP's own meanings instead of inventing new ones: which methods are safe to repeat, which status code says what went wrong, and a standard shape for an error body. Retiring an old version is part of the design too, and HTTP has header fields for announcing it. Reach for this topic before you add an endpoint other people will call, and when you decide how to change or retire one they already call. And for an agent: pick the method by its meaning in RFC 9110 (a retried PUT or DELETE must be harmless, a retried POST may not be), return errors as application/problem+json, and announce a retirement with the Deprecation and Sunset header fields.

**History.** RFC 9110, HTTP Semantics, published by the IETF in June 2022, calls a request method "safe" if its defined semantics are essentially read-only, and of the methods it defines, GET, HEAD, OPTIONS and TRACE are safe. A method is "idempotent" if the intended effect of multiple identical requests is the same as the effect of a single one, and PUT, DELETE and the safe methods are idempotent. RFC 9457 (July 2023) defines a "problem detail" to carry machine-readable details of errors in an HTTP response, with the media type application/problem+json and members such as type, title, status, detail and instance, and it obsoletes RFC 7807. RFC 9745 (March 2025) defines the Deprecation response header field, which signals that a resource will be or has been deprecated, with the example Deprecation: @1688169599 for 30 June 2023 at 23:59:59 UTC. RFC 8594 (May 2019) defines the Sunset header field, which indicates that a URI is likely to become unresponsive at a specified point in the future.

**Try in five minutes.** Write methods.txt with one line per method, GET, HEAD, PUT, DELETE and POST, each followed by the words safe and idempotent where RFC 9110 gives them, and neither where it gives neither. Then write problem.json, the body a 404 would carry, with type, title and status.

- Docs: [RFC 9110, HTTP Semantics, section 9.2 Common Method Properties](https://www.rfc-editor.org/rfc/rfc9110.html), [RFC 9457, Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html), [RFC 9745, The Deprecation HTTP Response Header Field](https://www.rfc-editor.org/rfc/rfc9745.html), [RFC 8594, The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594.html)
- Unlocks: [[Describing an API with OpenAPI]], [[OAuth 2.0 and OpenID Connect]]
- Shelf: Web, networks and APIs · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #net
