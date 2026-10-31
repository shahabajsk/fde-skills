# fde-skills for coding agents

This repository holds seven skills for deploying AI agents into enterprise and regulated processes. Each skill is a folder under `skills/` with a `SKILL.md` (instructions) and, where useful, `templates/` and `scripts/`.

When a task matches a skill below, read that skill's `SKILL.md` in full and follow it. Produce the artifacts it names, in the templates it links.

| Task | Skill |
|---|---|
| Scoping an agent project, "we want an agent for X" | `skills/fde-discovery/SKILL.md` |
| Building an eval set, scoring agent outputs, release gates | `skills/eval-harness/SKILL.md` |
| Planning go-live, staged rollout, kill switch, on-call | `skills/rollout-runbook/SKILL.md` |
| Postmortem after an agent failure | `skills/agent-incident-review/SKILL.md` |
| Risk, compliance or audit readiness in banking, payments, insurance, airlines, healthcare | `skills/regulated-readiness/SKILL.md` |
| Executive status or go/no-go page | `skills/stakeholder-readout/SKILL.md` |
| Making scheduled or CI agent loops safe to run unattended | `skills/unattended-readiness/SKILL.md` |

Rules that apply across all skills:

- Every number carries its source and date. Unknown values are written as unknown, never estimated silently.
- Decisions are written as made; open decisions get an owner and a date.
- The eval script is `skills/eval-harness/scripts/evalkit.py` (Python standard library, no network, no model calls).
- Regulatory points in `regulated-readiness` are an engineering checklist, not legal advice; check `references.md` dates before relying on them.
