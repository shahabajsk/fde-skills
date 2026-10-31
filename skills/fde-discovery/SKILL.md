---
name: fde-discovery
description: Run a discovery sprint before building an AI agent for an enterprise process. Produces a one-page problem brief with baselines, a "what we will not automate" list, and floor questions for SMEs. Use when a customer says "we want an agent for X", before any prompt or code is written.
---

# FDE discovery

The most expensive mistake in enterprise AI is building the agent the sponsor described instead of the one the floor needs. Discovery exists to find the number that will decide success, the person who owns that number, and the cases the agent must never touch.

Run this before writing a single prompt. If the user asks you to skip it, produce at least the problem brief and say which fields are guesses.

## What you produce

1. `problem-brief.md` from [templates/problem-brief.md](templates/problem-brief.md). One page. Every number has a source and a date.
2. A "will not automate" list inside the brief. Each item names the reason: regulatory, irreversible, low volume, or no ground truth.
3. `floor-questions.md`: the questions for the SMEs who do the work today, from [templates/floor-questions.md](templates/floor-questions.md), cut to the 15 that matter for this process.

## How to run it

### 1. Get the process from the people who do it, not the people who bought it

Ask the user for, or help them collect:

- 20 to 50 real cases from the last 90 days, including the ugly ones. Tickets, emails, call notes, case files.
- The written SOP, and then where the floor departs from it. The gap between SOP and practice is where agents fail.
- Two SMEs who handle the work daily, plus one who handles escalations.

If none of this is available, stop and say so. A brief built only from the sponsor's description is a guess with a template around it.

### 2. Map the process as it actually runs

Draw the steps as the floor executes them: trigger, lookups, decisions, actions, handoffs. For each step record:

- Which system is read or written, and whether an API exists or someone copies between screens.
- Who decides, and on what information.
- Which steps are reversible. A refund issued, a booking cancelled, a fraud flag cleared: these are one-way doors.

### 3. Measure the baseline before anyone builds

You cannot claim improvement against a number nobody measured. Capture:

| Measure | Why it matters |
|---|---|
| Monthly volume, and the peak day | Sizing, and whether automation pays at all |
| Median and 90th percentile handle time | The 90th percentile is where the cost and the complaints live |
| First-contact resolution rate | Agents often trade handle time for repeat contacts |
| Error rate and cost of one error | Decides how much autonomy is affordable |
| Escalation rate and who receives them | The agent will change this; know what it was |
| Share of cases that follow the SOP cleanly | The ceiling for full automation |

If a measure is unknown, write "unknown" and add the question to the floor list. Do not estimate silently.

### 4. Find the decision owner and the success metric

One person must own the outcome metric and be able to say yes to production. Record their name and role. The success metric is one number with a baseline, a target and a date, for example: "Median rebooking handle time from 11 min to 4 min by end of Q2, with misrouted rebookings below the current 2.1%."

A metric with no guardrail ("faster", "cheaper") will be met by an agent that is fast and wrong.

### 5. Write the will-not-automate list

Put a case on the list when any of these hold:

- The action is irreversible and the cost of one error is above what the business would accept from a new human hire.
- Regulation requires a named human decision (money movement above a threshold, adverse credit decisions, medical judgement).
- There are fewer than about 30 examples a month, so you cannot build or monitor an eval for it.
- The floor cannot agree on the right answer. If two SMEs disagree on the same case, there is no ground truth to automate.

This list is a deliverable, not a disclaimer. Sponsors trust a team that says what it will not do.

### 6. Check data access before promising anything

For every system the agent must read or write: who grants access, how long it takes, what data leaves the boundary, and whether production data can be used for evaluation. Access is the most common cause of a discovery-to-pilot slip.

## Stop conditions

Discovery is done when:

- The brief has a named decision owner, a baselined metric and a target date.
- At least 20 real cases have been read end to end.
- The will-not-automate list exists and the sponsor has seen it.
- Every system access path is either granted or has an owner and a date.

Discovery should stop early and report back if the sponsor's metric and the floor's pain point disagree. Name the conflict in the brief; do not resolve it by picking one.

## Anti-patterns

- Demo-first discovery: building a prototype in week one and asking the floor to react. You get feedback on the demo, not the process.
- Averages only. A median handle time of 6 minutes hides the 40-minute cases that drive cost.
- Treating the SOP as ground truth.
- Accepting "all cases" as scope. Start with the highest-volume, lowest-risk slice, and say what comes next.
- A success metric chosen after the pilot.

## Next

Hand the brief to `eval-harness`: the cases you read become the first golden set.
