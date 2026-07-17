---
name: implementation
description: "Implement an authorized repository change with the smallest coherent diff while preserving existing work and established boundaries."
---

# Implementation

Implementation follows the user request and established repository evidence. Fast-path work may use an inline plan; managed work follows its task contract.

## Preconditions

Confirm:

- mode is `change` and local writes are authorized;
- the intended outcome, affected area, and validation approach are sufficiently clear;
- for managed work only, the task contract and required design gates permit implementation;
- approvals cover the next action, not merely a related one;
- working-tree and active-claim checks reveal no overlapping undocumented work.

If a precondition is missing, return to task triage or the owning specialist. Do not fill a boundary decision by guesswork.

## Execution

1. Inspect the narrow code path and existing conventions.
2. Apply `core/minimalism`: prefer no new concept, then platform/standard library, then an existing dependency/pattern, then the smallest coherent new implementation.
3. Keep one writer per file. Read-only workers may research or review; the root integrates and verifies.
4. Validate all external input and model/tool output. Preserve authorization, privacy, accessibility, compatibility, and data-loss controls.
5. Handle expected failures explicitly. Add tests at the lowest useful level for changed behavior and boundaries.
6. Avoid unrelated cleanup, dependency additions, generated artifacts, commits, pushes, deployments, or external actions unless explicitly in scope.
7. Update task status and material handoff facts without copying logs or sensitive payloads.

Use `apply_patch` or the repository's safe edit mechanism. Preserve pre-existing user changes. Never use destructive reset, checkout, or recursive delete to simplify integration.

## Handoff to testing

Return changed paths, behavior mapped to acceptance criteria, assumptions resolved, known risks, and the smallest relevant validation commands. `specialists/code-quality-testing` owns the corrective loop; `core/validation` owns final proof.
