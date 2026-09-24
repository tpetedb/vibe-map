---
title: "Continuous delivery and deploy strategies"
date: 2026-09-24
tags: [tech, ship]
generated: 69b6718c48fa
---
# Continuous delivery and deploy strategies

Continuous delivery means the software can be released to production at any time; continuous deployment goes one step further and puts every change that passes the pipeline into production automatically. Deploy strategies such as blue-green and canary make that release low risk, and a deploy job that names an environment has to pass that environment's protection rules first. Reach for this topic once CI is green on every push and the next question is how a change gets to users, and how you would know whether you are getting better at it: the DORA metrics. And for an agent: deploy through a job that names its environment, so the environment's protection rules and secrets apply, and keep each change small, because small changes are easier to move through delivery and to recover from.

**History.** Martin Fowler's note of 30 May 2013 defines continuous delivery as "a software development discipline where you build software in such a way that the software can be released to production at any time", and says continuous deployment means every change goes through the pipeline and automatically gets put into production. In a blue-green deployment there are two production environments, as identical as possible, and a router switches all incoming requests from the live one to the other, which also gives "a rapid way to rollback". A canary release, as Danilo Sato describes it, slowly rolls a change out to a small subset of users before rolling it out to everybody, and the rollback is to reroute users back to the old version. In GitHub Actions, jobs.<job_id>.environment names the environment a job references, and all deployment protection rules must pass before that job is sent to a runner. DORA measures software delivery with change lead time, deployment frequency, failed deployment recovery time, change fail rate and deployment rework rate, and its research "has repeatedly demonstrated that speed and stability are not tradeoffs."

**Try in five minutes.** Write deploy.yml: a workflow started by workflow_dispatch, with one job deploy that runs on ubuntu-latest, names environment: production, and has one step that runs echo deploying. Read it back and say what has to pass before GitHub sends that job to a runner.

- Docs: [Martin Fowler, ContinuousDelivery](https://martinfowler.com/bliki/ContinuousDelivery.html), [Martin Fowler, BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html), [Danilo Sato on martinfowler.com, CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html), [GitHub Docs, Workflow syntax for GitHub Actions: jobs.<job_id>.environment](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [DORA, software delivery performance metrics](https://dora.dev/guides/dora-metrics/), [Source: the Linux Foundation, announcing the Continuous Delivery Foundation](https://www.linuxfoundation.org/press/press-release/the-linux-foundation-announces-new-foundation-to-support-continuous-delivery-collaboration)
- Unlocks: [[Container images, layers and Compose]], [[Infrastructure as code with OpenTofu]], [[Observability with OpenTelemetry]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
