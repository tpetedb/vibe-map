---
title: "Cloud and servers"
date: 2026-09-16
tags: [tech, ship]
---
# Cloud and servers

A server is a computer that is always on. The cloud rents you one by the hour (AWS 2006, Azure 2010, GCP 2008) or runs your code without one (serverless: Lambda 2014, Vercel, Cloudflare Workers). For most people's first project, a static host (GitHub Pages) or a small VPS (Hetzner, Fly.io) is enough.

**History.** AWS launched S3 in March and EC2 in August 2006; renting compute by the hour changed who could start a company. Google App Engine followed in April 2008 and Windows Azure went live in February 2010. Serverless (AWS Lambda, November 2014) removed the server from view; today agents can provision all of it with one prompt, which is why understanding the bill matters.

**Try in five minutes.** Deploy the game to GitHub Pages (free). Later: fly launch on the FastAPI endpoint.

- Docs: [AWS getting started](https://aws.amazon.com/getting-started/), [Fly.io docs](https://fly.io/docs/), [Cloudflare Pages](https://developers.cloudflare.com/pages/), [Source: AWS, Announcing Amazon S3 (March 2006)](https://aws.amazon.com/about-aws/whats-new/2006/03/announcing-amazon-s3---simple-storage-service), [Source: AWS, Announcing Amazon EC2 beta (August 2006)](https://aws.amazon.com/about-aws/whats-new/2006/08/24/announcing-amazon-elastic-compute-cloud-amazon-ec2---beta/), [Source: Google blog, Developers, start your engines (April 2008)](https://googleblog.blogspot.com/2008/04/developers-start-your-engines.html), [Source: Microsoft, Windows Azure general availability (February 2010)](https://blogs.microsoft.com/blog/2010/02/01/windows-azure-general-availability/), [Source: AWS, Introducing AWS Lambda (November 2014)](https://aws.amazon.com/about-aws/whats-new/2014/11/13/introducing-aws-lambda/)
- Unlocks: [[Kubernetes and platforms]], [[Cost, tokens and model choice]]
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
