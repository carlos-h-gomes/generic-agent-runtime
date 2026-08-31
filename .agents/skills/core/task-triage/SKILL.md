---
name: task-triage
description: "Classify work and create a formal task contract only for authorized managed changes; keep answers, inspections, diagnoses, and reviews read-only."
---

# Task triage

Own formal managed-task intake. Do not create a contract for fast-path work and do not implement the work.

## 1. Classify independently

Record each axis without inferring one from another:

- `mode`: `answer`, `inspect`, `diagnose`, `review`, `change`, or `monitor`;
- `work_level`: 0 micro, 1 local, 2 multi-file/cross-boundary, or 3 broad system/program scope;
- `scope.size`: `micro`, `local`, `multi_file`, `cross_boundary`, or `system`;
- risk, reversibility, and external effect;
- local-write and external-action authorization.

Answer, inspect, diagnose, and review are read-only unless the user separately authorizes a change. A change request authorizes only the local reversible work reasonably required; it does not authorize commits, pushes, deployments, messages, production actions, or destructive effects.

## 2. Build the contract

Use `schemas/task-contract.schema.json`. The minimum useful contract states:

- observable outcome and acceptance criteria;
- documentation impact as `none`, `technical`, `user_manual`, or `both`, with a concrete reason and required artifact pointers;
- affected files or a bounded discovery plan;
- owned, shared, and do-not-touch paths;
- scope, risk, assumptions, and explicit exclusions;
- triggered skills and gates, each with a concrete reason;
- scoped approval requirements;
- coordination strategy and limits;
- validation commands, manual checks, evidence plan, and attempt limit;
- one next action.

Reject placeholders such as `see above`, `TBD`, or copied boilerplate. Ask only when missing information materially changes outcome, risk, cost, or authority. Safe read-only discovery may resolve file and command unknowns first.

## 3. Choose persistence

- Level 0: a compact working contract may remain in the response.
- Level 1: use a compact inline or scratch contract unless continuity requires a file.
- For authorized change work, Level 2/3, cross-boundary/system, high/critical risk, multi-session, or multi-writer: create `docs/ai/tasks/YYYY-MM-DD-slug.task.json` plus concise Markdown notes only when explanation or diagrams help. Persist and schema-validate a Level 2/3 contract before implementation, and report the validated contract path in the handoff.

Creating project memory is itself a write. Mode and authorization take precedence over risk-based persistence: in answer, inspect, diagnose, or review modes, return the contract, production-readiness decision, gate conclusions, and proposed paths in the response unless the user authorized project writes or an existing governed workflow explicitly requires an update. A production review can block approval without creating a task bundle. Do not initialize `docs/ai`, duplicate existing decisions, or create one file per gate merely because the subject is high risk.

When persistence is authorized, reuse an active contract or decision when it remains authoritative. Create a new formal artifact only for a real continuity, ownership, approval, or release-evidence need. Start from the canonical templates under `docs/ai/tasks/` and validate task, decision, and GateResult JSON against their canonical schemas before returning or citing them. Schema-invalid output remains incomplete evidence and must not be presented as a completed control.

## 4. Route gates

Trigger gates from actual scope and risk, using the canonical IDs in the schema. Design-phase UX, architecture, data, security, and AI artifacts must exist before authorized implementation when applicable; a read-only review may report the same conclusions inline. Record `not_applicable` only with a specific reason; do not use it to bypass a control.

Use `docs/ai/quality-gates.md` for result semantics. A specialist is a procedure, not automatically a separate agent.

For brownfield application work, preserve the observed stack and require an evidence-backed architecture profile; migration is separate. For greenfield work, reuse an explicit user choice. If a material language, stack, platform, or tool choice is missing, record user decision as pending, present relevant options and tradeoffs, and block only application implementation until the user decides. Trigger `architecture_uml` and require boundaries, responsibilities, dependency direction, thin composition roots, contracts, compatibility, and validation. A single-file monolith is not approvable; record the modular decomposition instead. `python-react-hybrid` remains an optional bundled compatibility profile.

Material automation or integration triggers architecture, data, security, FinOps, code-quality, and release review. Require an open component decision conforming to `schemas/solution-decision.schema.json`; user-named tools are allowed, but unknown authority, system-of-record, recovery, security, or cost facts keep it draft.

## 5. Set a typed state

Use the schema states. Typical transitions:

```text
draft -> ready -> in_progress -> ready_for_review -> done
       -> needs_input
       -> awaiting_approval
       -> blocked_external
       -> validation_failed -> paused_for_review
```

Pending approval blocks only the protected action. Continue safe, authorized planning or local validation when useful. Use `blocked_external` only when no meaningful in-scope progress remains.

## Handoff

For managed work, return the contract path, mode/level/risk, applicable gates, approval boundaries, and next authorized action. For fast-path work, return only a compact plan and proceed without a persisted contract.
