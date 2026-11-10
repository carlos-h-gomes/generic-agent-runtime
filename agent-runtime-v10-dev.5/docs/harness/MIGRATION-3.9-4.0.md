# Migrating Harness 3.9 to 4.0

Harness 4.0 is intentionally smaller at startup and stricter at machine boundaries. Review and merge rather than blindly overwriting project-specific instructions or memory.

## Preflight

1. Extract v4 to a staging directory; never overlay the target directly.
2. Record the target revision or file inventory and back up every colliding governance/script/schema path.
3. Back up `docs/ai/bridge/` separately. The clean v4 archive contains an empty ledger and must never replace live coordination history.
4. Preserve the project constitution, decisions, verified commands, risks, active tasks, and project-specific instructions.
5. Stop active writers or obtain a clean handoff before merging coordination/runtime files.

## Required changes

1. Replace the generic v3.9 `AGENTS.md` with the v4 kernel while preserving nearer project-specific safety constraints.
2. Reduce `CLAUDE.md` and `GEMINI.md` to `@AGENTS.md` plus true host-specific deltas; configure another host's instruction filename when it does not read `AGENTS.md`.
3. Add `harness.json` and `schemas/`; convert Level 2/3 active tasks to companion `.task.json` contracts.
4. Replace the bridge scripts and initialize v2. Existing v1 ledger events remain readable, but all new events use run/actor IDs and leases.
5. Replace core and specialist skills together; their gate IDs and statuses are coordinated with the schemas.
6. Merge clean `docs/ai` templates without erasing project-specific constitution, decisions, verified commands, risks, or current handoffs.
7. Adopt Python 3.10+ as the portable script core and use the Bash/PowerShell adapters appropriate to the host.
8. Run local validation and the behavioral suite against the target model/runtime before broad rollout.

## Bridge v1 to v2

The log CLI is intentionally breaking:

```text
# v3.9
bash scripts/bridge.sh log AGENT EVENT TASK NOTE FILES_CSV NEXT

# v4.0
python scripts/bridge.py log RUN ACTOR EVENT TASK NOTE FILES_CSV NEXT LEASE_MINUTES
```

Preserve the old ledger, install the v4 reader, then run `python scripts/bridge.py init`, `doctor`, and `claims`. V1 claims appear under run `legacy` with `legacy/unbounded` leases. Reconcile each claim with its owner; do not assume it is stale. Release a confirmed old claim with the same actor/task/path, for example:

```text
python scripts/bridge.py log legacy OLD_ACTOR release OLD_TASK "v1 claim reconciled" "path/**"
```

New claims require a positive bounded lease. `board`, `tail`, `claims`, and `doctor` are read-only; `init`, `log`, and `compact` persist derived state.

## Behavior differences

- `answer`, `inspect`, `diagnose`, and `review` are read-only unless a separate change is authorized.
- Work level no longer implies risk or permission.
- Pending approval blocks only the protected action, not safe local planning and validation.
- Native coordination is preferred within one host; the file bridge is reserved for cross-tool/session durability.
- `bridge.py board` is now a read-only derived view printed to stdout; use `init`, `log`, or `compact` when the persisted board must be regenerated.
- One agent is default; parallelism requires independent bounded work, one-writer ownership, budgets, and root synthesis.
- Gate results are separate JSON artifacts with bounded redacted evidence.
- The reflection limit is three total attempts, including the initial validation run.
- A skipped scanner or absent project stack is not reported as a pass.
- Consumer archives exclude maintainer task history and live bridge events.

## Compatibility mapping

| 3.9 | 4.0 |
|---|---|
| `triage_status: ready_for_implementation` | task `status: ready` or `in_progress` |
| `needs_clarification` | `needs_input` |
| generic `blocked` | `awaiting_approval`, `blocked_external`, `validation_failed`, or `paused_for_review` |
| task level as primary router | separate mode, work level, scope, risk, and authorization |
| three implementation/testing loops | three total validation attempts |
| bridge actor-only events | v2 run + actor + event ID + optional lease |
| manual board snapshot | board generated from ledger |

## Validation and rollback

Before accepting v4:

1. Run the target project's original tests plus `python scripts/runtime_check.py`, then the Bash or PowerShell Harness validation.
2. Inspect all skips and execute the model behavioral qualification for the chosen host/profile.
3. Confirm current bridge claims, task contracts, and project memory survived the merge.

If validation fails, stop new writers, quarantine the merged v4-only files, restore every colliding path and `docs/ai/bridge/` from the preflight backup, then rerun the original project/v3 checks. Do not rewrite task/decision history; append the failed migration evidence and reason. Keep `agent-runtime-v3.9.zip` unchanged as the audit/reference distribution, not as an automatic rollback mechanism.
