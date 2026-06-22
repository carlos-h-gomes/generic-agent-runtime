---
name: task-triage
description: "Supervise and route every non-trivial task. Use at the START of any task to convert a vague request into a strict structured task specification (intent, acceptance criteria, affected files, task level 0-3, triggered gates, approval needs, validation plan) BEFORE any implementation begins. Returns needs_clarification or blocked when the request is too ambiguous or unsafe to implement. Always load this before core/implementation."
---

# Task Triage

## Objective

Act as the task supervisor. Convert the user's request into a clear, validated, structured task specification before any specialist or implementation agent starts work.

This skill owns orchestration and routing. It does not only organize a queue; it applies a Plan-Act pattern:

1. **Plan:** clarify intent, scope, acceptance criteria, affected files, risks, gates, and required specialists.
2. **Act:** route the task only when the structured task specification is complete enough for the next agent to execute without guessing.

## When to use

Use at the beginning of any non-trivial task.

## Inputs expected

- User request.
- Current project profile.
- Known constraints.
- Files or systems likely to be touched.
- Risk triggers.
- Available project commands.
- Any prior task file or decision log entry that may affect the work.

## Process

1. Restate the user's intent in one sentence.
2. Convert abstract intent into a strict task specification.
3. Validate whether the task has, at minimum:
   - clear description;
   - acceptance criteria;
   - affected files or file discovery plan;
   - out-of-scope boundaries;
   - validation expectations.
4. If any required field is missing, return the task as `needs_clarification` or `blocked`, instead of sending an ambiguous request to implementation.
5. Classify the task:
   - Level 0: micro.
   - Level 1: simple.
   - Level 2: medium.
   - Level 3: critical.
6. Identify gates triggered by the actual work, not by fear.
7. Choose skills to load.
8. Decide whether a task document is needed.
9. Identify what context must be written before implementation.
10. Route the task to the next skill only after the task specification is valid.

## Required output contract

Task triage must output structured data before implementation. Prefer JSON. YAML is acceptable only when the target agent cannot handle JSON well.

The output must follow this shape:

```json
{
  "triage_status": "ready_for_implementation | needs_clarification | blocked",
  "intent": "One-sentence user intent.",
  "task_level": "0 | 1 | 2 | 3",
  "description": "Clear implementation-oriented description.",
  "acceptance_criteria": [
    "Observable condition that proves the task is complete."
  ],
  "affected_files": {
    "owned": ["path/or/pattern"],
    "shared": ["path/or/pattern"],
    "do_not_touch": ["path/or/pattern"],
    "discovery_needed": ["path/or/question"]
  },
  "scope": {
    "in_scope": ["What must be done."],
    "out_of_scope": ["What must not be done."]
  },
  "gates_triggered": [
    "architecture_uml",
    "code_quality_testing",
    "ux_product",
    "security_compliance",
    "data_integration",
    "finops",
    "observability_release",
    "ai_llm"
  ],
  "skills_to_load": [
    ".agents/skills/core/implementation/SKILL.md"
  ],
  "context_packet_required": true,
  "task_file_required": true,
  "human_approval_required": {
    "required": false,
    "reason": "Explain approval boundary."
  },
  "validation_plan": {
    "commands": ["./scripts/test.sh", "./scripts/lint.sh"],
    "manual_checks": ["Specific manual check if needed."],
    "quality_loop_max_attempts": 3
  },
  "missing_information": [],
  "routing_decision": "Where the task goes next and why."
}
```

## Return rules

Return as `needs_clarification` when the agent cannot define clear acceptance criteria or safe affected-file discovery from repository context.

Return as `blocked` when the task requires human approval before proceeding, conflicts with a documented constraint, or depends on unavailable secrets, environments, production access, or missing files.

Do not send a task to `core/implementation` when:

- acceptance criteria are empty;
- affected files are unknown and no discovery plan exists;
- a required architecture/UML artifact is missing for a feature that changes architecture, data, integrations, deployment, or cross-cutting workflows;
- a required UX/Product artifact is missing for a user-facing flow;
- human approval is required and not yet granted.

## Escalation triggers

Escalate to Level 3 when the task involves production, auth, customer/personal data, destructive migration, public endpoints, external LLMs with user/customer context, variable cost increase, infrastructure, billing, bulk messaging, or secrets.

## Deliverables

- Strict task specification JSON/YAML.
- Task level.
- Gates triggered.
- Skills required.
- Minimal workflow.
- Written context requirement.
- Approval requirement.
- Validation plan.
- Routing decision.

## Quality criteria

- No over-processing.
- No skipped critical gates.
- Clear reason for level selection.
- Abstract intent converted into executable structured data.
- Specialists receive enough context to avoid guessing.
- Token use proportional to risk.

## Checklist

- [ ] Intent clear.
- [ ] Structured task specification produced.
- [ ] Description clear.
- [ ] Acceptance criteria present.
- [ ] Affected files or discovery plan present.
- [ ] Level selected.
- [ ] Gates selected.
- [ ] Skills selected.
- [ ] Written context need identified.
- [ ] Human approval need identified.
- [ ] Routing decision safe.
