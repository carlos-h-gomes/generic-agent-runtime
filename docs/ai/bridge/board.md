# Agent Board — current state

> Materialized view of the bridge. **Overwrite in place; keep under one page.** History lives in `ledger.jsonl` (append-only, read with `./scripts/bridge.sh tail`). Reading this board must be enough to know who is doing what right now. Details never live here — they live in the task file each row points to.

Updated: (never) by (nobody)

## Active tasks

| Task file (docs/ai/tasks/) | Level | Owner (agent) | Status | Blocked on |
|---|---|---|---|---|
| _none_ | | | | |

## File claims

Claims are derived from ledger `claim`/`release` events — refresh with `./scripts/bridge.sh claims`. Snapshot below is advisory; the ledger is authoritative.

| Path / glob | Claimed by | Since | Task |
|---|---|---|---|
| _none_ | | | |

## Waiting on a human

- _none_

## Do not touch (global)

- _none_
