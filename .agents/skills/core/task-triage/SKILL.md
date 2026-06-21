# Task Triage

## Objective

Classify the task and choose the smallest safe workflow.

## When to use

Use at the beginning of any non-trivial task.

## Inputs expected

- User request.
- Current project profile.
- Known constraints.
- Files or systems likely to be touched.
- Risk triggers.

## Process

1. Restate the user's intent in one sentence.
2. Classify the task:
   - Level 0: micro.
   - Level 1: simple.
   - Level 2: medium.
   - Level 3: critical.
3. Identify gates triggered by the actual work, not by fear.
4. Choose skills to load.
5. Decide whether a task document is needed.
6. Identify what context must be written before implementation.

## Escalation triggers

Escalate to Level 3 when the task involves production, auth, customer/personal data, destructive migration, public endpoints, external LLMs with user/customer context, variable cost increase, infrastructure, billing, bulk messaging, or secrets.

## Deliverables

- Task level.
- Gates triggered.
- Skills required.
- Minimal workflow.
- Written context requirement.
- Approval requirement.

## Quality criteria

- No over-processing.
- No skipped critical gates.
- Clear reason for level selection.
- Token use proportional to risk.

## Checklist

- [ ] Intent clear.
- [ ] Level selected.
- [ ] Gates selected.
- [ ] Skills selected.
- [ ] Written context need identified.
- [ ] Human approval need identified.
