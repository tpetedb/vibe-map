---
title: "Infrastructure as code with OpenTofu"
date: 2026-09-24
tags: [tech, ship]
generated: 13981a2c3d1e
---
# Infrastructure as code with OpenTofu

Infrastructure as code means your servers, networks and DNS entries are described in configuration files you can version, review and share, and a tool makes the real world match them. OpenTofu is an open source tool of that kind: you write the configuration, it shows a plan of what it would create, change or destroy, and it applies the plan only on approval. Reach for this topic when someone clicks the same settings into a cloud console twice, or when a change to infrastructure should go through a pull request like any other change. And for an agent: run tofu plan and show the plan before any tofu apply, and treat terraform.tfstate with care: it holds the bindings to real resources, and the docs recommend keeping state in TACOS, versioned and encrypted, rather than in the local file.

**History.** OpenTofu "is an infrastructure as code tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share", and providers let it work with virtually any platform or service with an accessible API. Its core workflow has three steps: write, plan, where it "creates an execution plan describing the infrastructure it will create, update, or destroy", and apply, where on approval it performs the proposed operations in the correct order. OpenTofu stores state about your managed infrastructure, by default in a local file named terraform.tfstate, and the primary purpose of state is to store bindings between remote objects and the resources in your configuration. The terraform_data resource needs no provider to be configured, because it is always available through a built-in provider, and its input argument is stored in state and reflected in its output attribute after apply. The Linux Foundation announced OpenTofu on 20 September 2023 as an open source alternative to Terraform, after Terraform's licence changed from the Mozilla Public License v2.0 to the Business Source License v1.1.

**Try in five minutes.** Write main.tf with one resource "terraform_data" "greeting" whose input is "hello, camp", and one output "greeting" whose value is terraform_data.greeting.output. If you have OpenTofu installed, run tofu init and tofu plan in that folder and read the plan: one resource to add, no cloud account and no provider to configure.

- Docs: [OpenTofu documentation, Getting started](https://opentofu.org/docs/intro/), [OpenTofu documentation, Working with OpenTofu](https://opentofu.org/docs/intro/core-workflow/), [OpenTofu documentation, State](https://opentofu.org/docs/language/state/), [OpenTofu documentation, The terraform_data Managed Resource Type](https://opentofu.org/docs/language/resources/tf-data/), [Source: the Linux Foundation, Linux Foundation Launches OpenTofu](https://www.linuxfoundation.org/press/announcing-opentofu)
- Unlocks: [[Observability with OpenTelemetry]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
