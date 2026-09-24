---
title: "Describing an API with OpenAPI"
date: 2026-09-24
tags: [tech, net]
generated: 011f60cbad21
---
# Describing an API with OpenAPI

An OpenAPI description is a YAML or JSON document that says what an HTTP API offers: its paths, the operations on each, and what they return. People read it as documentation, and tools use the same file to generate clients, servers and tests. Reach for it when an API is used by someone other than its author, or when you want the documentation to be something a machine can check. And for an agent: keep the openapi field (the version of the specification) apart from info.version (the version of your document), and start every path with a slash.

**History.** The OpenAPI Specification "defines a standard, programming language-agnostic interface description for HTTP APIs", so that humans and computers can understand a service without access to its source code. It is versioned major.minor.patch, the major.minor part (for example 3.1) designates the feature set, and patch versions only fix or clarify the document; the latest published version on 24 September 2026 is 3.2.1, dated 10 September 2026. The root object requires the openapi field, the version of the specification the document uses, and an info object with a title and a version, plus at least one of components, paths or webhooks. Every path in the Paths object is relative to the server and must begin with a forward slash. In November 2015 a group of companies including SmartBear, Google, IBM and Microsoft announced the OpenAPI Initiative as an open source project under the Linux Foundation, and the specification was based on the Swagger 2.0 specification that SmartBear donated.

**Try in five minutes.** Write openapi.yaml for one endpoint: openapi: 3.1.1, an info block with a title and version: 0.1.0, and paths with /scores and a get operation whose responses list 200 with a description. Read it back top to bottom and name the specification object each block is.

- Docs: [OpenAPI Specification, latest published version](https://spec.openapis.org/oas/latest.html), [OpenAPI Initiative, About](https://www.openapis.org/about), [Source: OpenAPI Initiative, FAQ](https://www.openapis.org/faq)
- Shelf: Web, networks and APIs · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #net
