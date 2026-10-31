---
name: eval-harness
description: Build an offline evaluation set from real cases before building an enterprise AI agent, then score every agent version with pass^k, escalation precision and recall, cost per correct outcome, and a regression gate. Use when starting an agent project, before changing a prompt or model, or when someone asks "is it good enough to ship?".
---

# Eval harness

An agent that is right 85% of the time on a single try can be right on all four tries less than half the time. A customer gets one try. Build the eval before the agent, so every change is measured against the same cases and the same bar.

This skill uses `scripts/evalkit.py` (Python standard library, no model calls). You run the agent with whatever model and harness you use, write the outputs to a file, and evalkit scores them.

## What you produce

1. `golden.jsonl`: one line per real case with the correct outcome, labelled by the floor.
2. `eval-plan.md` from [templates/eval-plan.md](templates/eval-plan.md): metrics, floors, who signs off.
3. A scored report per agent version, and a CI gate that blocks a release that regresses.

## Step 1. Build the golden set from real cases

- Start from the cases read in discovery. Aim for 50 to 200 to start, covering every category in scope.
- Over-sample the cases that hurt: the 90th-percentile handle time, the ones that were escalated, the ones a customer complained about. A golden set of easy cases measures nothing.
- Each case gets one expected outcome, labelled by two SMEs independently. Where they disagree, the case goes to the decision owner. If the decision owner cannot decide, the case goes on the will-not-automate list, not into the golden set.
- Mark `should_escalate: true` for cases a human must handle. The agent is graded on recognising them, not on solving them.
- Mark `critical: true` for cases where a wrong outcome causes money movement, a regulatory breach or harm. One error here fails the release, whatever the averages say.
- Freeze a holdout: 20% of cases nobody looks at while tuning prompts. Check it only before a release.

Golden line:

```json
{"id": "D04", "expected_action": "refund_original_payment", "should_escalate": false, "critical": true, "category": "refund"}
```

## Step 2. Run k trials per case

Run each case at least 4 times with the production settings (same model, temperature, tools, retrieval). Variance between trials is the finding; one run hides it. Write one line per trial:

```json
{"id": "D04", "trial": 3, "action": "issue_travel_credit", "escalated": false, "cost_usd": 0.0105}
```

`cost_usd` comes from the provider's usage report or your own token count. If you use local or open models, record compute time instead and convert with your own rate.

## Step 3. Score

```
python scripts/evalkit.py golden.jsonl predictions.jsonl --k 4 --json report.json
```

| Metric | What it answers | Typical floor for a customer-facing agent |
|---|---|---|
| pass^1 | How often is one try right? | Context only, never the release metric |
| pass^k | How often are all k tries right? This is reliability. | Set with the decision owner, per category |
| Escalation recall | Of the cases a human must handle, how many reached a human? | 0.95 or higher; a miss here is a customer harmed |
| Escalation precision | Of the escalations, how many were needed? | Lower is tolerable; it costs time, not trust |
| Cost per correct outcome | Spend divided by correct trials, so retries and wrong answers count | Below the human cost per case, with margin |
| Critical-task errors | Wrong outcomes on cases marked critical | Zero |

pass^k is the estimator from [tau-bench](https://arxiv.org/abs/2406.12045) (Yao et al., 2024): for a case with c correct out of n trials, C(c, k) / C(n, k), averaged over cases.

The floors in the table are starting points to argue about with the decision owner. Write the agreed numbers in the eval plan before the first run, not after.

## Step 4. Gate every change

```
python scripts/evalkit.py golden.jsonl predictions.jsonl --gate \
  --min-pass-k 0.85 --min-recall 0.95 --baseline last_release.json --max-drop 0.02
```

The gate fails on any critical-task error, on a floor breach, or on a drop of more than `--max-drop` against the last release. Wire it into CI so a prompt change cannot ship on a demo. Store each release's `report.json` as the next baseline.

## Step 5. Read the failures, not the averages

For each release candidate, open every failed trial in the weakest category and write one line on why it failed: retrieval missed, policy misread, tool error, ambiguous case. Two or more failures with the same cause get a fix and a new golden case. A failure the floor calls ambiguous goes back to labelling.

## Stop conditions

The eval is ready when the golden set covers every in-scope category, the floors are signed off by the decision owner, the holdout exists, and the gate runs in CI. Do not start tuning prompts before this point: you will tune to the cases you happen to remember.

## Anti-patterns

- Reporting accuracy from one run. Reliability lives in pass^k.
- An LLM as the only grader of an LLM. Use exact outcome labels where the process has them; where you need a model grader, calibrate it against human labels first and report its agreement rate.
- Synthetic cases written by the team building the agent. They test what the team already thought of.
- Ignoring cost until the pilot. A correct answer at 20 retries can cost more than the human.
- Editing the golden set to make a release pass.

## Try it

The `examples/` folder holds a synthetic airline-disruption queue: 12 cases, 4 trials each, with planted errors.

```
python scripts/evalkit.py examples/golden.jsonl examples/predictions.jsonl --gate --min-pass-k 0.8 --min-recall 0.95
```

It reports 85.4% accuracy and 50.0% pass^4, misses 2 of 12 escalation trials (3 cases, 4 tries each, both misses on case D11), and fails the gate on one critical error: a travel credit issued where a refund to the original payment was due.
