# Rollout runbook: <agent name>

Decision owner: <name>   Runbook owner: <name>   Version: <n>, signed <YYYY-MM-DD>

## Scope

In scope: <categories, channels, regions>
Never in scope: <link to will-not-automate list>

## Stages

| Stage | Start date | Categories | Entry evidence | Exit floor (metric, value, period) | Rollback trigger |
|---|---|---|---|---|---|
| 1 Shadow | | all in scope | Eval plan signed | | |
| 2 Assisted | | | | | |
| 3 Partial autonomy | | | | | |
| 4 Full autonomy | | | | | |

## Kill switch

Flag name and location: <>
Who may flip it: <names, roles>
Automatic triggers: spend over <x> per hour; sampled error rate over <y>; action API error rate over <z>; provider status degraded
Last tested: <date>, time to humans owning the queue: <minutes>

## On-call

| Week | Primary | Secondary |
|---|---|---|
| | | |

Pages: kill-switch auto-trigger, critical-task error, spend cap reached.

## Rollback per stage

| Stage | Find actions taken | Reversible actions and owner | Customer message owner | Evidence to go forward again |
|---|---|---|---|---|
| | | | | |

## Comms log

| Date | Audience | Message | Sent by |
|---|---|---|---|
| | | | |
