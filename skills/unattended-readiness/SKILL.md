---
name: unattended-readiness
description: Check whether the agent loops in a repository (CI jobs calling Claude Code, Codex or Gemini CLI, shell loops, Python model loops, Stop hooks) are safe to leave running without a person watching, and fix them to level L3. Uses the walkaway CLI for a deterministic scan and paranoid-sre for destructive-action guards. Use before scheduling any agent to run unattended.
---

# Unattended readiness

An agent you schedule overnight needs six things a supervised one can borrow from the person at the keyboard: a stop condition, a budget, an independent verifier, a human escalation path, a limited blast radius, and state that survives between runs. This skill checks them with a static scan and fixes what is missing.

## Steps

1. Install the scanner (public from 17 November 2026): `pipx install git+https://github.com/shahabajsk/walkaway`
2. Scan: `walkaway scan . -f json -o walkaway.json --fail-below none`
3. For each loop below L3, fix the findings in this order: blast radius (untrusted triggers, injection, permission bypass), then stop conditions, budget, verifier, escalation, state. `walkaway explain <RULE>` prints the reason and the fix for any rule.
4. Rescan. The scanner is the verifier, not your judgement: a fix counts when `walkaway scan .` reports L3 for that loop.
5. For agents that run commands on real systems, add the guard hook from [paranoid-sre](https://github.com/shahabajsk/paranoid-sre) so destructive commands need explicit confirmation.

## What L3 does not mean

A pass means the controls are declared, not that they work: a test step counts as a verifier even if the suite is thin. Pair the scan with `eval-harness` for the agent's actual outcomes and with `rollout-runbook` before widening its permissions.
