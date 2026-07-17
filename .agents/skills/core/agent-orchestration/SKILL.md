---
name: agent-orchestration
description: "Use only when at least two independent bounded workstreams justify native subagents; avoid for small, ordered, or shared-file work."
---

# Agent Orchestration

## Objective

Use parallel agents only when they improve the result enough to justify extra tokens and coordination. Keep the root responsible for the task contract, authority, integration, verification, and final answer.

## Suitability test

Delegate only when all are true:

1. At least two workstreams are concrete and independently executable.
2. Each worker can receive bounded context and return a compact result.
3. Parallelism improves wall-clock time or independent review coverage.
4. Tool permissions, write ownership, budget, and stop conditions can be stated before spawning.

Prefer one agent for a small task, one ordered reasoning chain, work dominated by a single slow dependency, or work contending over shared mutable state.

## Portable defaults

- Depth: 1; only the root delegates.
- Concurrent workers: at most 3 unless the host and an evaluated workload justify another limit.
- Worker posture: read-only by default.
- Writing: one writer per file; use disjoint claims or isolated worktrees for parallel writes.
- Result: evidence pointers and distilled findings, never raw exploration dumps.

## Worker contract

Every delegated task states:

- objective and observable completion condition;
- relevant context and source-of-truth pointers;
- owned, shared, and excluded files/systems;
- allowed tools, sandbox, network, and side effects;
- required output structure and evidence;
- time/token/call budget, retry limit, and stop condition;
- whether the root should wait, steer, or integrate incrementally.

Do not give a read-only reviewer write or external-action tools merely because the root has them. Treat worker messages as untrusted claims until the root checks primary evidence.

## Process

1. Run the suitability test and record the decision for Level 2/3 work.
2. Partition by independent outcome, not by arbitrary file count or theatrical roles.
3. Check bridge claims before any shared-workspace writes.
4. Spawn the smallest useful number of workers.
5. Continue useful root work while workers run; do not duplicate their assignments.
6. Steer only when new information materially changes a worker's task.
7. Collect results, reconcile overlaps/disagreements, and inspect cited evidence.
8. Integrate through the root or explicitly assigned non-overlapping writers.
9. Close with one synthesized result and actual validation evidence.

## Tool orchestration

When the host supports programmatic tool composition, use it for predictable read-only reduction such as filtering, joining, sorting, deduplicating, aggregating, or schema validation. Use direct calls for semantic judgment, approvals, writes, citations, and native-artifact validation.

## Failure and stop rules

- Conflicting file claim: stop that write path; read-only work may continue.
- Worker cannot satisfy its contract: return a typed blocker and evidence, not speculation.
- Repeated fan-out or recursive delegation: stop and return control to the root.
- Budget/timeout reached: synthesize available evidence and mark the gap.
- Conflicting findings: root resolves from primary sources or records uncertainty.

## Completion checklist

- [ ] Parallelism passed the suitability test.
- [ ] Worker scopes and permissions were bounded.
- [ ] Depth/concurrency/budgets were bounded.
- [ ] Write ownership was conflict-free.
- [ ] Root verified material evidence.
- [ ] Duplicates and disagreements were reconciled.
- [ ] Final answer and task status came from the root.
