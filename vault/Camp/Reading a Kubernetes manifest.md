---
title: "Reading a Kubernetes manifest"
date: 2026-09-24
tags: [tech, ship]
generated: c9c37796781f
---
# Reading a Kubernetes manifest

A Kubernetes manifest is a YAML file that describes an object you want to exist, such as a Deployment that keeps three copies of a container running or a Service that gives them one address. You write the desired state and Kubernetes keeps working to make the cluster match it. Reach for this topic when a repository has a k8s folder you need to read, or when an agent writes a manifest you have to check, without running a cluster on your laptop. And for an agent: check that a Service's selector matches the labels on the Deployment's pod template, and that its targetPort is the port the container listens on.

**History.** Kubernetes objects are persistent entities that represent the state of a cluster, and an object is "a record of intent": once you create it, the system constantly works to ensure that it exists. Every manifest sets apiVersion, kind, metadata (which includes a name) and spec, the state you desire, while status is supplied and updated by Kubernetes itself. A Pod is the smallest deployable unit, "a group of one or more containers, with shared storage and network resources", and a Deployment provides declarative updates for Pods: the docs' nginx-deployment example asks for replicas: 3 of the image nginx:1.14.2 on containerPort: 80. A Service exposes a network application running as one or more Pods; its example my-service selects Pods labelled app.kubernetes.io/name: MyApp and maps port 80 to targetPort 9376. Kubernetes was accepted to the CNCF on 10 March 2016 and moved to the Graduated maturity level on 6 March 2018.

**Try in five minutes.** Write deployment.yaml for a Deployment named scores with replicas: 2, pod labels app: scores and one container listening on containerPort: 8000. Write service.yaml for a Service whose selector is app: scores and whose port 80 goes to targetPort: 8000. Read both against the nginx-deployment example; kubectl is not needed.

- Docs: [Kubernetes documentation, Objects In Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/), [Kubernetes documentation, Pods](https://kubernetes.io/docs/concepts/workloads/pods/), [Kubernetes documentation, Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [Kubernetes documentation, Service](https://kubernetes.io/docs/concepts/services-networking/service/), [Source: CNCF, Kubernetes project page](https://www.cncf.io/projects/kubernetes/)
- Unlocks: [[Kubernetes and platforms]], [[Infrastructure as code with OpenTofu]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
