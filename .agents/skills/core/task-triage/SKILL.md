---
name: task-triage
description: "Create a formal task contract only for Level 2/3, multi-session, multi-writer, high-risk, or explicitly governed work; skip ordinary local changes."
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
- Level 2/3, cross-boundary/system, high/critical risk, multi-session, or multi-writer: create `docs/ai/tasks/YYYY-MM-DD-slug.task.json` plus concise Markdown notes when explanation or diagrams help.

Creating project memory is itself a write. In read-only modes, return the contract in the response and name the proposed path instead.

## 4. Route gates

Trigger gates from actual scope and risk, using the canonical IDs in the schema. Design-phase UX, architecture, data, security, and AI artifacts must exist before implementation when applicable. Record `not_applicable` only with a specific reason; do not use it to bypass a control.

Use `docs/ai/quality-gates.md` for result semantics. A specialist is a procedure, not automatically a separate agent.

For greenfield application generation, require the `python-react-hybrid` target profile. For brownfield work, preserve the observed stack and require an evidence-backed project architecture policy; migration to Python/React is a separate managed outcome. Trigger `architecture_uml` and add observable criteria for the applicable boundaries, entrypoints, contracts, compatibility, and validation. A request for a single-file monolith is not an approvable task constraint; record the compliant decomposition instead.

Material automation triggers architecture, data, security, FinOps, code-quality, and release review. Require a `code`, `n8n`, or `hybrid` decision conforming to `schemas/automation-decision.schema.json`; unknown facts keep the decision draft.

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
