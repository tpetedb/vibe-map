---
title: "Container images, layers and Compose"
date: 2026-09-24
tags: [tech, ship]
generated: 5a438da186d4
---
# Container images, layers and Compose

An image is a stack of immutable layers, each one a set of filesystem changes, and a multi-stage build uses one stage to build and a later stage to keep only what should ship. Compose describes an application of several containers in one compose.yaml, as services that talk over networks. Reach for this topic once docker run works and your images are too big, your builds too slow, or your app needs a database next to it. And for an agent: name build stages with AS and copy from them by name, so reordering the Dockerfile cannot break a COPY --from, and put the Compose file at compose.yaml, the name Compose prefers.

**History.** The Open Container Initiative was launched on 22 June 2015 by Docker, CoreOS and other leaders in the container industry, under the auspices of the Linux Foundation, and its image specification defines an image as an image manifest, a filesystem (layer) serialization and an image configuration. In Docker's docs, container images are composed of layers, each layer "contains a set of filesystem changes - additions, deletions, or modifications", each layer is immutable once created, and layers can be reused between images. With multi-stage builds "you use multiple FROM statements in your Dockerfile", each FROM begins a new stage, and you selectively copy artifacts from one stage to another, "leaving behind everything you don't want in the final image". A stage is named by adding AS <NAME> to the FROM instruction, so COPY --from=build keeps working even if the instructions are reordered, and docker build --target build stops at that stage. Compose reads a YAML file, by default compose.yaml, that follows the Compose Specification: the computing components of an application are services, and services communicate with each other through networks.

**Try in five minutes.** Write a Dockerfile with two stages: FROM python:3.12-slim AS build that writes a file, and a second FROM python:3.12-slim that does COPY --from=build of only that file. Then write compose.yaml with a services: block that builds it. If Docker is running, docker build --target build -t camp-build . stops at the first stage; the check reads the files and needs no Docker.

- Docs: [Docker Docs, Understanding the image layers](https://docs.docker.com/get-started/docker-concepts/building-images/understanding-image-layers/), [Docker Docs, Multi-stage builds](https://docs.docker.com/build/building/multi-stage/), [Docker Docs, How Compose works](https://docs.docker.com/compose/intro/compose-application-model/), [Open Container Initiative, About the OCI](https://opencontainers.org/about/overview/)
- Unlocks: [[Reading a Kubernetes manifest]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
