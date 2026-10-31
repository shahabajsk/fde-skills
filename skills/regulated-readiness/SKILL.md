---
name: regulated-readiness
description: Check whether an AI agent is ready to run inside a regulated business (banking, payments, insurance, airlines, healthcare) before production. Covers data residency, personal data, audit trail, human approval for money movement, model risk management, and India (RBI, DPDP Act) and EU AI Act points. Produces a readiness checklist with evidence and gaps. Use before a risk or compliance review, or when a customer in a regulated industry asks "can we put this in production?".
---

# Regulated readiness

This is an engineering checklist, not legal advice. Its job is to make sure the questions a risk, compliance or audit team will ask have evidence behind them before the meeting, and to surface the gaps early enough to fix. Every regulatory point below links to its source in [references.md](references.md), with the date it was checked. Regulations change; recheck the references before relying on them.

## What you produce

A checklist with three columns per item: status (met, gap, not applicable), evidence (a link, a log query, a document), and owner. Gaps get a date or go on the risk register.

## 1. Data: where it goes and what it is

- [ ] Data map: every field the agent reads, where it is stored, where it is sent (model provider, vector store, logs, analytics), and in which country.
- [ ] Personal data minimised before it reaches the model. Mask or tokenise identifiers the task does not need (card numbers, government IDs, full dates of birth).
- [ ] Model provider terms checked: retention, training on inputs, region of processing. Recorded in the data map.
- [ ] Logs and traces hold the same classification as the source data, with the same retention and access rules. Agent traces are a common leak.
- [ ] Payments in India: payment system data must be stored only in India; if processed abroad it must be deleted there and brought back within one business day or 24 hours of processing, whichever is earlier (RBI, April 2018 circular and FAQ). Check whether the agent's model calls or logs count as processing abroad.
- [ ] India personal data: the DPDP Rules 2025 were notified on 13 November 2025 with phased commencement; most obligations apply after 18 months. Plan now for consent and notice, erasure when the purpose ends, and breach notification to the Data Protection Board without delay with a detailed report within 72 hours. Penalties in the Act's schedule run up to INR 250 crore for failing to take reasonable security safeguards and up to INR 200 crore for failing to notify a breach.

## 2. Actions: what the agent can change

- [ ] Every tool the agent can call is listed with what it changes, whether it is reversible, and its limits (amount caps, rate limits, allowed record types).
- [ ] Money movement (refunds, payouts, credits, fee waivers) needs human approval above a threshold agreed with risk, and a hard cap enforced in the tool, not the prompt.
- [ ] Adverse decisions about a person (declining credit, cancelling a policy, denying a claim) are made or approved by a named human role.
- [ ] The agent's credentials are its own service identity with least privilege, never a human's account.
- [ ] Kill switch and staged rollout per `rollout-runbook`.

## 3. Evidence: can you reconstruct any decision?

- [ ] For any action: the input, retrieved context, model and prompt version, tool calls and results, and the human approver (if any) can be retrieved by case id.
- [ ] Audit records are append-only and retained for the period the business already uses for that record type.
- [ ] Customer-facing disclosure that an AI is involved, worded with compliance, where policy or regulation requires it.
- [ ] Complaint and grievance route for customers who dispute an agent outcome, with a human reviewer.

## 4. Model risk management

- [ ] The agent is on the model inventory with an owner, intended use, limits and a risk tier.
- [ ] Validation evidence: the eval plan, golden set, pass^k by category, escalation recall, and the holdout result (see `eval-harness`).
- [ ] Ongoing monitoring: sampled outcome review, drift in input mix, eval rerun on every model or prompt change.
- [ ] Third-party models: document what you cannot validate from the provider and the compensating controls.
- [ ] US banks: the OCC, Federal Reserve and FDIC replaced the 2011 model risk guidance (SR 11-7 / OCC 2011-12) with revised guidance on 17 April 2026. Per law-firm summaries, generative and agentic AI is excluded from its scope by footnote, with banks expected to apply broader risk management meanwhile. Expect reviewers to ask for SR 11-7 style evidence anyway; it is the vocabulary they know.

## 5. India: RBI FREE-AI

The RBI's Framework for Responsible and Ethical Enablement of AI (released August 2025) sets out seven principles ("sutras") and 26 recommendations. Points to prepare evidence for:

- [ ] A board-approved AI policy covering permitted use cases, risk appetite and governance.
- [ ] Accountability stays with the regulated entity; it cannot be assigned to a model.
- [ ] Humans can override the AI, and final authority rests with people.
- [ ] Disclosures, explainability and grievance redressal for customers.
- [ ] Independent audit, impact assessment and continuous monitoring.

Read the full report for the recommendation text; the summaries used here do not list all 26 (uncertain beyond the points above).

## 6. EU AI Act

- [ ] Prohibited practices and AI literacy have applied since 2 February 2025. Under the Digital Omnibus the literacy duty became one to support literacy, not guarantee a level.
- [ ] Rules for general-purpose AI models have applied since 2 August 2025 (they bind the model provider; check the provider's documentation).
- [ ] High-risk systems in Annex III, which include creditworthiness assessment and credit scoring of individuals (fraud detection excluded) and risk assessment and pricing in life and health insurance, now carry obligations from 2 December 2027. Annex I systems follow on 2 August 2028. The Omnibus was published in the Official Journal on 24 July 2026.
- [ ] Transparency duties under Article 50 apply from 2 August 2026, with Article 50(2) for synthetic content moved to 2 December 2026.
- [ ] If the agent is a customer service agent that only routes and resolves service requests, record why it is not high-risk. If it scores or decides on credit or insurance, plan for high-risk obligations now.

## 7. Industry notes

- Airlines, US: automatic refunds are required when a flight is cancelled or significantly changed (3 hours domestic, 6 hours international) and the passenger does not accept an alternative; prompt means 7 business days for card payments and 20 calendar days otherwise. An agent that offers travel credit by default where a refund is due is a compliance error, so mark refund cases `critical` in the eval.
- Healthcare and insurance: treat health data as the most restricted class in the data map and confirm the provider agreement covers it before any pilot. This skill does not cover HIPAA or other health-data rules in detail (not verified here).

## Stop conditions

Do not take the agent to a risk committee with any item in sections 2 or 3 marked as a gap without a date and an owner. Section 1 gaps that involve data leaving the country or the regulated boundary block production.

## Anti-patterns

- Treating the provider's compliance certificate as the agent's compliance.
- Logging full prompts and responses into a general-purpose log store.
- A human approval step with no record of who approved and what they saw.
- Writing the readiness pack after the go-live date is announced.
