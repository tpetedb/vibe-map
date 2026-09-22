# Recovery notes

PR 171 changed the Claude Code builder role from Opus to Fable after measured
mixed-model usage was higher, matching the existing reviewer and team-manager
roles. Recovery narrowed the two explanatory documents so the policy applies
only to Claude Code work-order roles and does not describe Codex's model.

The original pull request was green before recovery. The combined support
train reruns the focused work, repository, template and style checks and then
the full repository gate on the final integrated tree.
