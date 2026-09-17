---
title: "Docker and containers"
date: 2026-09-16
tags: [tech, ship]
generated: 19dccb7a1702
---
# Docker and containers

A container is a packaged process: your code, its dependencies, and a slice of an operating system, running the same on any machine. A Dockerfile is the recipe; an image is the result; a container is a running copy. It ends 'works on my machine'.

**History.** Chroot arrived with Seventh Edition Unix in 1979; Linux mount namespaces in 2002 (kernel 2.4.19) and cgroups in January 2008 (2.6.24). Docker (Solomon Hykes, dotCloud) was first shown at PyCon in March 2013 and made them usable; Kubernetes (Google, open sourced 2014) made them run in fleets. Much of cloud software today runs in containers.

**Try in five minutes.** Install Docker Desktop or OrbStack. docker run -it python:3.12 python -c 'print(1)'. You just ran Python in a box you did not install.

- Docs: [Docker get started](https://docs.docker.com/get-started/), [OrbStack (lighter on Mac)](https://orbstack.dev), [Dev containers](https://containers.dev), [Source: TUHS, V7 chdir/chroot(2) manual page](https://www.tuhs.org/cgi-bin/utree.pl?file=V7/usr/man/man2/chdir.2), [Source: TUHS, Seventh Edition Unix (January 1979)](https://www.tuhs.org/cgi-bin/utree.pl?file=V7), [Source: mount_namespaces(7), history](https://man7.org/linux/man-pages/man7/mount_namespaces.7.html), [Source: cgroups(7)](https://man7.org/linux/man-pages/man7/cgroups.7.html), [Source: Docker blog, Docker: Nine Years Young (2022)](https://www.docker.com/blog/docker-nine-years-young/), [Source: Google Cloud, the Kubernetes origin story (2016)](https://cloud.google.com/blog/products/containers-kubernetes/from-google-to-the-world-the-kubernetes-origin-story)
- Unlocks: [[Cloud and servers]], [[CI-CD and automation]], [[Kubernetes and platforms]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
