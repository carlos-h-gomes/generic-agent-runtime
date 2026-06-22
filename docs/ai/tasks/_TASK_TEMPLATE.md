# Task — <title>

Date: YYYY-MM-DD
Level: 0 / 1 / 2 / 3
Status: draft / in-progress / blocked / ready-for-review / done

## User request

## Intent

## Acceptance criteria

## Clarifications

Resolve ambiguities and unstated assumptions before planning (Level 2/3). Record question/answer pairs here. If something blocks safe acceptance criteria or file discovery, set triage to `needs_clarification`.

| Question | Answer / decision |
|---|---|
|  |  |

## Structured task specification

```json
{
  "triage_status": "ready_for_implementation | needs_clarification | blocked",
  "intent": "",
  "task_level": "0 | 1 | 2 | 3",
  "description": "",
  "acceptance_criteria": [],
  "affected_files": {
    "owned": [],
    "shared": [],
    "do_not_touch": [],
    "discovery_needed": []
  },
  "scope": {
    "in_scope": [],
    "out_of_scope": []
  },
  "gates_triggered": [],
  "skills_to_load": [],
  "context_packet_required": true,
  "task_file_required": true,
  "human_approval_required": {
    "required": false,
    "reason": ""
  },
  "validation_plan": {
    "commands": [],
    "manual_checks": [],
    "quality_loop_max_attempts": 3
  },
  "missing_information": [],
  "routing_decision": ""
}
```

## Scope

## Out of scope

## Context packet

### Project docs read

- [ ] AGENTS.md
- [ ] CLAUDE.md
- [ ] docs/ai/constitution.md
- [ ] docs/ai/project-profile.md
- [ ] docs/ai/commands.md
- [ ] docs/ai/conventions.md
- [ ] docs/ai/shared-context.md
- [ ] docs/ai/risks.md

### Relevant files inspected

| File/path | Why it matters | Notes |
|---|---|---|

### Business rules / constraints

| Rule | Source | Impact |
|---|---|---|

### Open assumptions

| Assumption | Impact | How to verify |
|---|---|---|

## File coordination

### Owned files

### Shared files

### Do-not-touch files

### Handoff notes

## Gates triggered

For each gate, mark `triggered`, `not applicable`, or `deferred`, and write the reason.

- [ ] Architecture/UML — status/reason:
- [ ] Code Quality/Testing — status/reason:
- [ ] UX/Product — status/reason:
- [ ] Security/Compliance — status/reason:
- [ ] Data/Integration — status/reason:
- [ ] FinOps — status/reason:
- [ ] Observability/Release — status/reason:
- [ ] AI/LLM — status/reason:

## Legacy specialist mapping used

List any old-style specialist responsibility covered by the consolidated gates, when relevant.

## Architecture / UML notes

Include only useful diagrams or model notes. Architecture artifact required before implementation when the task changes architecture, data, integrations, deployment, or cross-cutting workflows.

```text
Optional Mermaid/PlantUML/text diagram
```

## Cross-artifact consistency check (analyze)

Read-only check before implementation (Level 2/3). Confirm the task spec, UX/Product artifact and Architecture/UML artifact agree with each other and the codebase. List gaps to fix before coding.

- [ ] Every acceptance criterion is covered by the plan/artifacts.
- [ ] UX and architecture artifacts do not contradict each other or the spec.
- [ ] No required artifact is missing for a triggered gate.
- [ ] Constitution principles and hard constraints are respected.

Gaps found:

## Technical plan

## Implementation notes

## Reflection loop

Maximum attempts: 3 implementation/testing loops unless project docs define another value.

| Attempt | Commands run | Result | Failure output / notes | Next action |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

Pause for human review if validation still fails after the maximum attempts.

## Validation

### Commands run

### Manual checks

### Not validated

## Risks and pending items

## Release / rollback

## Level 3 critical checklist

Use only for critical tasks.

- [ ] Acceptance criteria status
- [ ] Tests/lint/typecheck/build/manual checks
- [ ] Architecture/UML impact
- [ ] Security impact
- [ ] Privacy/compliance impact
- [ ] Data/integration impact
- [ ] Cost/FinOps impact
- [ ] Operational impact
- [ ] Observability impact
- [ ] Release plan
- [ ] Rollback plan
- [ ] Incident response path
- [ ] Human approval status
- [ ] Residual risks and owner/handoff

## Final handoff

## Reusable lessons

If this task hit a non-obvious failure, wrong assumption, or a fix worth reusing, copy a one-line lesson into `docs/ai/decision-log.md` under "Lessons learned".

-
