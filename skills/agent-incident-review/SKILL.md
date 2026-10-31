---
name: agent-incident-review
description: Run a blameless postmortem for an AI agent failure in production, such as a wrong action, runaway cost, prompt injection or silent quality degradation. Produces a timeline, impact, root causes across model, context, tools and controls, and fixes with owners. Use after any agent incident, page or customer-visible error.
---

# Agent incident review

Agent incidents look like model failures and are usually control failures. The model did something plausible with what it was given; the question is why nothing between the model and the customer caught it. Blameless means the review looks for missing controls, not for the person who wrote the prompt.

## What you produce

A postmortem from [templates/postmortem.md](templates/postmortem.md), shared within five working days, with every action item owned and dated.

## The four incident types and what to collect first

| Type | Looks like | Collect before anything is changed |
|---|---|---|
| Wrong action | A refund, booking, message or record change that should not have happened | The full trace: input, retrieved context, tool calls and their results, final action, model and prompt version |
| Runaway cost | A spend alert, a loop that kept calling the model | Iteration count, tokens per call, the stop condition that should have fired, who was paged and when |
| Prompt injection | The agent followed instructions from content it read (an email, a ticket, a web page, a document) | The injected text, where it came from, what the agent could reach from that context, what it did |
| Silent degradation | Quality fell over days or weeks with no single failing case | The eval scores over time, model or provider changes, retrieval index changes, input mix changes |

Preserve traces before the fix. A hot-patched prompt with no copy of the old one makes the review guesswork.

## The five questions

Answer each in the postmortem, in order:

1. **What did the agent see?** The exact context at the moment of the decision. Most wrong actions trace to missing, stale or contradictory context, not reasoning.
2. **What was it allowed to do?** The tools and permissions it held. If it could do the wrong thing, the scope was too wide for the risk.
3. **What should have stopped it?** The eval case, the guardrail, the human gate, the budget, the stop condition. Name the control and why it did not fire, or note that it did not exist.
4. **How did we find out?** Monitoring, sampling, an SME, or a customer. Customer-detected means detection is the first fix.
5. **Would the eval catch it now?** Add the case to the golden set and show the current version fails it. If the eval cannot express the failure, that gap is itself an action item.

## Root cause layers

Classify each cause; most incidents have more than one.

- Model: a capability limit, a provider change, a known failure mode.
- Context: retrieval, missing data, stale data, ambiguous policy text.
- Tools: an API that accepted a bad call, a missing validation, an over-broad permission.
- Controls: no human gate, a rubber-stamped gate, no budget, no stop condition, no sampling.
- Process: a change shipped without the eval gate, a stage advanced on a date rather than evidence.

## Action items

Each item is a control, not an exhortation. "Be more careful with prompts" is not an action item. "Refund tool rejects amounts above the original fare; owner, date" is.

Prefer, in order: remove the capability, add a deterministic check, add a human gate, add monitoring. Prompt changes come last because they are the easiest to regress.

## Prompt injection specifics

- Treat every piece of content the agent reads from outside (customer messages, emails, attachments, web pages, other systems' free text) as untrusted data.
- The fix is reducing what the agent can do from that context: fewer tools while reading untrusted content, approvals for actions that leave the system, no secrets in reach.
- Record the payload in the eval set as an adversarial case.

## Anti-patterns

- Closing the incident with a prompt edit and no eval case.
- "The model hallucinated" as the root cause. It is a description, not a cause.
- Reviewing only the failing case. Search the logs for the same pattern in other cases before closing.
- Naming the engineer who shipped the change. Name the missing control.
