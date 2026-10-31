---
name: rollout-runbook
description: Plan and run the staged rollout of an AI agent into an enterprise process, from shadow mode to full autonomy, with entry and exit criteria per stage, a kill switch, on-call, rollback and stakeholder comms. Use when an agent has passed offline evals and someone asks "when do we turn it on?".
---

# Rollout runbook

Passing the offline eval earns the right to watch the agent on live traffic, not the right to let it act. Each stage widens what the agent may do only after the previous stage has produced evidence. The runbook is written before stage 1 starts and changed only with the decision owner's sign-off.

## What you produce

A runbook from [templates/runbook.md](templates/runbook.md) with: the stages and their numbers, the kill switch and who may pull it, the on-call rota, the rollback steps, and the comms plan.

## The four stages

| Stage | The agent | A human | Moves to next stage when | Rolls back when |
|---|---|---|---|---|
| 1. Shadow | Sees live cases, proposes an outcome, takes no action | Works every case as today; proposals are logged and compared | Agreement with humans meets the eval floor on at least 2 weeks and a few hundred cases of live traffic, per category | Never acts, so no rollback; stop if logging fails or data leaks |
| 2. Assisted | Drafts the action; a human approves, edits or rejects each one | Approves every action before it happens | Approve-without-edit rate meets the floor, edits are minor, and no critical error has been approved | A human approves a wrong critical action, or reviewers start approving without reading (approval time collapses) |
| 3. Partial autonomy | Acts alone on the low-risk categories named in the runbook; everything else stays assisted | Samples a fixed share of autonomous actions daily; owns all escalations | Sampled error rate stays under the floor for the agreed period, escalation recall holds | Any critical error, error rate over the floor, or cost per correct outcome over the limit |
| 4. Full autonomy for the scope | Acts on the whole agreed scope; escalates what it should | Reviews samples and escalations; owns the metric | Steady state; review cadence drops on a schedule | Same triggers as stage 3, checked continuously |

The numbers in "moves to next stage" come from the eval plan and are written into the runbook with dates. "A few hundred cases" is a floor for statistical sense, not a target; low-volume categories may need longer.

Watch the human in stage 2. Rubber-stamping is the main failure mode: when median approval time falls below what reading the case takes, the human gate has stopped working. Track approval time and insert known-wrong drafts at a low rate to check reviewers still catch them.

## Kill switch

- One flag, checked before every action, that sends all traffic back to humans. Not a deploy, not a config PR: a flag the on-call can flip in under a minute.
- Named people who may flip it without asking: on-call engineer, operations lead, decision owner.
- Automatic triggers that flip it: spend per hour over the cap, error rate over the cap on sampled actions, the action API returning errors above a threshold, the model provider degraded.
- Tested before stage 3: flip it in production during a quiet hour and measure how long until humans have the queue.

## On-call

- Primary and secondary on-call for every hour the agent can act. If nobody is on call, the agent is in assisted mode.
- The runbook lists the three alerts that page: kill-switch auto-trigger, critical-task error, spend cap reached. Everything else is a ticket.
- Every page gets a short write-up within a working day; patterns go to `agent-incident-review`.

## Rollback

Rollback means moving back one stage, not switching off the project. Write down for each stage:

1. How actions already taken are found (query, log, audit trail).
2. Which of them can be reversed and who reverses them.
3. Who tells affected customers, and with what message.
4. What evidence is needed to move forward again.

## Comms

| Audience | When | What |
|---|---|---|
| Floor staff | Before each stage | What the agent will and will not do, how to report a bad action, who to call |
| Decision owner | Weekly, and on every rollback | The stage metrics against floors, decisions needed |
| Customer-facing teams | Before stage 3 | What customers may notice, approved wording for questions |
| Risk and compliance | Before stage 3 and stage 4 | Evidence pack: eval results, stage metrics, incident log, kill-switch test |

## Stop conditions

Do not start stage 1 without a signed eval plan. Do not start stage 3 without a tested kill switch, an on-call rota and a rollback written for every irreversible action.

## Anti-patterns

- Skipping shadow because "the eval already passed". Live traffic always has cases the golden set did not.
- A percentage rollout by traffic instead of by category. Five percent of all traffic still includes the worst cases.
- A kill switch that requires a deploy.
- Measuring stage success by handle time alone. Watch repeat contacts and complaints in the weeks after.
- Moving to the next stage because the date in the plan arrived.
