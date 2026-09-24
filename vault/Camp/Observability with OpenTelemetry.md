---
title: "Observability with OpenTelemetry"
date: 2026-09-24
tags: [tech, ship]
generated: 35c50e30dfd5
---
# Observability with OpenTelemetry

Observability is being able to understand what is going on inside a system from what it sends out: traces, metrics and logs. OpenTelemetry is the open source, vendor-neutral way to produce that data, with one set of APIs and SDKs for many languages, while storing and viewing it is left to other tools. Reach for it when a request is slow and nobody can say where the time went, or before you pick a monitoring vendor, so that switching later is not a rewrite. And for an agent: instrument with the OpenTelemetry API and send to the console exporter first, so you can read the spans before any backend is involved.

**History.** The OpenTelemetry docs define observability as "the ability to understand the internal state of a system by examining its outputs", which in software usually means analysing traces, metrics and logs, and to make a system observable it must be instrumented. OpenTelemetry is an observability framework and toolkit for generating, exporting and collecting that telemetry, vendor- and tool-agnostic, and it "is not an observability backend itself". Traces "give us the big picture of what happens when a request is made to an application", built from spans that share a trace_id, where a span with no parent_id is the root span. In Python, the ConsoleSpanExporter is included in the opentelemetry-sdk package and writes spans to the console, and tracer.start_as_current_span("parent") with a nested start_as_current_span("child") records the relationship between the two. OpenTelemetry is a CNCF project, the result of a merger between OpenTracing and OpenCensus, and it was accepted to the CNCF on 7 May 2019.

**Try in five minutes.** Write trace.py: a TracerProvider with a SimpleSpanProcessor(ConsoleSpanExporter()), a tracer, and a span named checkout with a nested span named charge. Run uv run --with opentelemetry-sdk python trace.py and find in the output which span has "parent_id": null.

- Docs: [OpenTelemetry, What is OpenTelemetry?](https://opentelemetry.io/docs/what-is-opentelemetry/), [OpenTelemetry, Traces](https://opentelemetry.io/docs/concepts/signals/traces/), [OpenTelemetry, Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/), [OpenTelemetry, Python exporters: the console exporter](https://opentelemetry.io/docs/languages/python/exporters/), [Source: CNCF, OpenTelemetry project page](https://www.cncf.io/projects/opentelemetry/)
- Unlocks: [[Incidents and blameless postmortems]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
