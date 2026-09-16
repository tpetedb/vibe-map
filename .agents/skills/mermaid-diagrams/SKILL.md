---
name: mermaid-diagrams
description: Draw diagrams as Mermaid code blocks (flowcharts, sequence, ER, Gantt, mindmaps). Use when asked for a diagram, map, flow, architecture picture, or to visualise a plan. Renders natively in Obsidian and GitHub.
---
# Mermaid diagrams

Docs: https://mermaid.js.org/intro/ . Obsidian and GitHub render ```mermaid blocks with no plugin.

Pick the type:
- process or flow: `flowchart LR` or `flowchart TD`
- who calls whom over time: `sequenceDiagram`
- tables and keys: `erDiagram`
- a plan over dates: `gantt`
- ideas around a centre: `mindmap`

Rules:
- Under 25 nodes per diagram; split otherwise.
- Short node ids, words in the label: `db[(scores.csv)]`.
- `classDef done fill:#34D399` and `class a,b done` to colour finished items.
- Put the diagram in the note where the reader needs it.

Example:

```mermaid
flowchart LR
  a[18:00 Innovation Hub] --> b[19:00 Centre of Excellence] --> c[20:00 Data Warehouse]
  classDef done fill:#34D399,color:#0b2b1c
  class a,b done
```
