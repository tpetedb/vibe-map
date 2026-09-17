---
title: "localhost and ports"
date: 2026-09-16
tags: [tech, shell]
generated: f0924e41ea5a
---
# localhost and ports

localhost (127.0.0.1) is your own machine talking to itself over the network stack. A port is a numbered door; a dev server on port 8000 means open http://localhost:8000. Everything web starts here before it goes anywhere.

**History.** Network 127 is set aside for loopback in the Assigned Numbers RFCs (RFC 990, 1986); TCP/IP became the ARPANET standard on 1 January 1983 (RFC 801). Port numbers were assigned by hand by Jon Postel for years, in those same RFCs.

**Try in five minutes.** python3 -m http.server 8000 in the game folder, open http://localhost:8000/game/ in a browser. Ctrl-C to stop.

- Docs: [MDN: How the web works](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works), [Source: RFC 990, Assigned Numbers (1986)](https://www.rfc-editor.org/rfc/rfc990), [Source: RFC 801, NCP/TCP Transition Plan (1981)](https://www.rfc-editor.org/rfc/rfc801)
- Unlocks: [[HTTP and APIs]], [[Docker and containers]], [[MCP (Model Context Protocol)]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
