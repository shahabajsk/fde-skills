---
name: stakeholder-readout
description: Turn discovery notes, eval results, rollout metrics or an incident into a one-page executive readout with the verdict first, decisions made, open decisions with owners and dates, and named risks. Use when a sponsor, steering committee or customer executive needs a status or a go/no-go decision on an AI deployment.
---

# Stakeholder readout

An executive reads the first two lines and decides whether to read the rest. Put the verdict and the decision you need from them in those two lines. Everything after is evidence.

## What you produce

One page from [templates/readout.md](templates/readout.md). If it does not fit on one page, the extra material goes in an appendix the reader can skip.

## Rules

1. **Verdict first.** One line: on track, at risk, or off track, plus the reason. "At risk: rebooking accuracy meets the floor but escalation recall is 0.83 against 0.95."
2. **The ask second.** The decision you need, from whom, by when. If there is no decision, say "No decision needed this week."
3. **Decisions written as made.** "We are starting with rebookings only" not "we recommend considering a phased approach".
4. **Open decisions named, with an owner and a date.** An open decision without an owner will still be open next week.
5. **Numbers against their floor and baseline.** "pass^4 0.62 (floor 0.85, last week 0.58)". A number alone means nothing to someone who did not set it.
6. **Risks named, not hedged.** Say what could go wrong, how likely, and what you are doing about it. "There may be some challenges with data" is not a risk.
7. **No method narrative.** The reader does not need to know what you tried in order. Headers follow the argument: what is working, what is not, what we need.
8. **Plain words.** No "leverage", "robust", "seamless", "cutting-edge". No adjectives the numbers do not support.

## Inputs to pull from

- Problem brief (`fde-discovery`): metric, baseline, target, decision owner.
- Eval report (`eval-harness`): pass^k by category, escalation recall, cost per correct, gate result.
- Runbook (`rollout-runbook`): current stage, stage floors, incidents.
- Incident reviews (`agent-incident-review`): open action items.

## Check before sending

- Could the reader act on the first two lines alone?
- Does every open decision have a name and a date?
- Does every number have a floor or baseline beside it?
- Is there anything in the page the reader cannot verify or ask about?

## Anti-patterns

- A status page that is all green until the week it is red.
- Burying a missed floor under three wins.
- Asking for a decision in the last paragraph.
- Sending a deck when a page would do.
