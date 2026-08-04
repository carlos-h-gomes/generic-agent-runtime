---
name: implementation
description: "Implement an authorized repository change with the smallest coherent diff while preserving existing work and established boundaries."
---

# Implementation

Implementation follows the user request and established repository evidence. Fast-path work may use an inline plan; managed work follows its task contract.

For greenfield or already conformant application work, preserve the Python API/React boundary and minimum extensible topology in `docs/ai/architecture-policy.json`. Brownfield adoption preserves the observed stack until a separate migration is authorized. Keep `main.py`, `server.py`, `App.jsx`, and `App.tsx` as thin composition roots when that profile applies. If a request would centralize routes, persistence, HTTP clients, business rules, feature state/data, or reusable UI in one of them, reject that constraint and implement or propose the compliant modular decomposition.

Do not implement a material automation until its execution-plane decision is schema-valid. Keep authoritative behavior in code, and implement n8n only as bounded orchestration under the recorded reliability, security, operations, cost, rollback, and kill-switch controls.

Additional directories are allowed when a distinct responsibility needs them; document the new layer and permitted dependencies rather than forcing unrelated behavior into an existing folder.

## Preconditions

Confirm:

- mode is `change` and local writes are authorized;
- the intended outcome, affected area, and validation approach are sufficiently clear;
- for managed work only, the task contract and required design gates permit implementation;
- approvals cover the next action, not merely a related one;
- working-tree and active-claim checks reveal no overlapping undocumented work.
- any project-owned command to be executed has been reviewed and explicit project-code trust is recorded.

If a precondition is missing, return to task triage or the owning specialist. Do not fill a boundary decision by guesswork.

## Execution

1. Inspect the narrow code path and existing conventions.
2. Apply `core/minimalism`: prefer no new concept, then platform/standard library, then an existing dependency/pattern, then the smallest coherent new implementation.
3. Keep one writer per file. Read-only workers may research or review; the root integrates and verifies.
4. Validate all external input and model/tool output. Preserve authorization, privacy, accessibility, compatibility, and data-loss controls.
5. Handle expected failures explicitly. Add tests at the lowest useful level for changed behavior, authority boundaries, malicious inputs, and recovery.
6. Avoid unrelated cleanup, dependency additions, generated artifacts, commits, pushes, deployments, or external actions unless explicitly in scope.
7. Update task status and material handoff facts without copying logs or sensitive payloads.

Use `apply_patch` or the repository's safe edit mechanism. Preserve pre-existing user changes. Never use destructive reset, checkout, or recursive delete to simplify integration. Do not pass the full host environment to project commands; use the Harness policy allowlist unless a separately reviewed command requires a named value.

## Handoff to testing

Return changed paths, behavior mapped to acceptance criteria, assumptions resolved, known risks, and the smallest relevant validation commands. `specialists/code-quality-testing` owns the corrective loop; `core/validation` owns final proof.
