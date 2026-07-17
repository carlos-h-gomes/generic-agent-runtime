---
name: agent-bridge
description: "Use only for actual cross-tool or cross-session shared writers that need durable file claims and handoffs; do not use for ordinary sequential work or read-only workers."
---

# Agent bridge

The bridge coordinates cooperative participants; it is not an authentication, authorization, or sandbox boundary. A process with filesystem access can bypass or alter it. Enforce real security through filesystem permissions, isolated worktrees, tool policy, and action approvals.

## When to use it

- Prefer native subagent/thread tools for workers inside one shared host session.
- Use the bridge for cross-tool, cross-session, human/agent, or durable shared-writer coordination.
- Read-only native workers do not need bridge events unless a durable handoff is required.

## Entrypoints

From the repository root:

```text
python scripts/bridge.py doctor
python scripts/bridge.py board
python scripts/bridge.py tail 15
python scripts/bridge.py claims
python scripts/bridge.py log RUN ACTOR EVENT TASK NOTE [FILES] [NEXT] [LEASE_MINUTES]
```

Use `scripts/bridge.sh` on POSIX and `scripts/bridge.ps1` on PowerShell when convenient. Never assume a bare `.sh` command works on Windows.

`doctor`, `board`, `tail`, and `claims` are read-only; `board` renders the current ledger view to stdout. `init`, `log`, and `compact` are mutating commands and persist the generated board.

## Session protocol

1. Generate a unique run ID; give each writer a unique actor ID.
2. Read the generated board, last 15 events, and the active task contract/notes.
3. Check active claims. Claim every path a writer may edit, including task/coordination files when shared.
4. Use repository-relative normalized paths or directory globs. Overlapping exact, ancestor/descendant, or glob claims conflict.
5. Refresh a claim before its lease expires. Never edit through another active overlapping claim.
6. Log only milestones: `start`, `progress`, `blocked`, `handoff`, `done`, plus `claim`/`release`.
7. Write detail to task files; events contain pointers and notes of at most 140 characters.
8. Release claims and write the handoff before completion.

The ledger uses `schemas/bridge-event.schema.json` v2. The tool reads legacy v1 events for migration, but new events are v2. The board is derived state and may be regenerated; the ledger is append-only except controlled compaction.

## Concurrency and recovery

- The bridge writer uses a short-lived lock and atomic replacement for derived files.
- Claims have leases so crashed workers do not block forever.
- `compact` must retain every event needed to reconstruct active claims plus a recent event window.
- If the ledger is invalid, locked beyond its timeout, or has conflicting live claims, stop writes, run `doctor`, and escalate with the exact pointer.
- Same-filesystem editing remains advisory. Use isolated worktrees or a single root writer for hostile or unreliable participants.

## Event safety

Never put secrets, raw logs, customer records, prompts, exploit payloads, or long explanations in events. Use sanitized pointers. Validate delegated findings before any mutation; the root/integrator owns final synthesis.
