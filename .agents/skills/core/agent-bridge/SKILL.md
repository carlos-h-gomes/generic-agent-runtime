---
name: agent-bridge
description: "File-based coordination protocol for multiple coding agents (Claude Code, Codex, Cursor, local models) and humans working in the same repository. Use whenever more than one agent/tool/human may touch the repo in overlapping time, when picking up work started by another agent, or when handing work off. Defines the append-only ledger, the one-page board, file claims, the fixed session boot sequence, and the token-budget rules (pointers not payloads, tail reads, compaction)."
---

# Agent Bridge

## Objective

Let multiple agents work in the same repository as if they shared memory — through files, deterministically, at a fixed and small token cost per session.

## The two surfaces

```text
docs/ai/bridge/ledger.jsonl   Append-only event log. The notification layer. Never edited, only appended. Never read in full — tail only.
docs/ai/bridge/board.md       Current-state snapshot. Overwritten in place. Max one page. Reading it replaces reading history.
```

Everything else (plans, decisions, diffs, findings) stays where it already lives: task files, `decision-log.md`, `shared-context.md`, git. **The bridge carries pointers, not payloads.**

## Ledger event schema

One JSON object per line. Short keys, hard caps.

```json
{"ts":"2026-07-02T15:04Z","a":"claude","e":"done","t":"2026-07-02-rls-fix","f":["src/db/policies.sql"],"n":"RLS policy added; tests green","nx":"codex: review policy for service-role bypass"}
```

| Key | Meaning | Rules |
|---|---|---|
| `ts` | UTC timestamp | `YYYY-MM-DDTHH:MMZ` |
| `a` | agent id | short, stable: `claude`, `codex`, `cursor`, `local-qwen`, `human-carlos` |
| `e` | event | one of: `claim`, `release`, `start`, `progress`, `done`, `blocked`, `handoff`, `note` |
| `t` | task slug | the task file name without date prefix is acceptable; must resolve to one file in `docs/ai/tasks/` |
| `f` | files touched/claimed | array of paths or globs; omit when none |
| `n` | note | **≤ 140 chars.** What happened, in one sentence |
| `nx` | next / handoff | **≤ 140 chars.** Addressed to an agent id when directed |

Hard rules:

- Never paste code, diffs, stack traces, payloads or secrets into `n`/`nx`. Put them in the task file and point to it.
- If 140 chars is not enough, the content belongs in the task file. The ledger entry then says where to look.
- Ledger is append-only. Corrections are new events, not edits.

## Session boot sequence (fixed cost)

Every session in a multi-agent repo starts with exactly this, before any change:

```bash
./scripts/bridge.sh board      # current truth (≤ 1 page)
./scripts/bridge.sh tail 15    # recent events
./scripts/bridge.sh claims     # active file claims derived from the ledger
```

Then read **only** the task file(s) for the work at hand. Do not read the full ledger, do not re-scan `docs/ai/` wholesale, do not read other agents' task files unless the board/tail points there. Target boot cost: under ~600 tokens.

## Write protocol

1. **Before touching shared files:** log `claim` with the paths in `f`. If another agent holds an unreleased claim on an overlapping path, stop — coordinate via `nx` or ask the human. Do not overwrite undocumented work (AGENTS.md §4).
2. **On starting a task:** log `start` and add/refresh the row in `board.md`.
3. **During long work:** log `progress` only at durable milestones, not per edit.
4. **On finishing:** update the task file's handoff notes first (details live there), then log `done` with a pointer, `release` the claims, and update the board row.
5. **On blocking:** log `blocked` with the reason in `n` and who/what it waits on in `nx`; move the item to "Waiting on a human" on the board when applicable.
6. **Directed handoff:** `handoff` with `nx` naming the target agent and the task file to read. The receiving agent's boot sequence will surface it.

The bridge complements, never replaces, the task-file requirements of AGENTS.md §3–§4. Owned/shared/do-not-touch lists stay in the task file; the ledger claim is the live, cheap signal on top.

## Token budget rules

- Pointers, not payloads (the single most important rule).
- Tail reads only; default 15 events, raise only with a reason.
- Board capped at one page; if it does not fit, the board is stale — prune done rows.
- Compaction: when the ledger passes 200 lines, run `./scripts/bridge.sh compact` — oldest entries move to `ledger-archive.jsonl`; anything durable in them must already be in task files or `shared-context.md` (if not, that was a protocol violation to fix, not to repeat).
- Logging is cheap by design (~50–80 tokens/event). Reading is where budgets die — the protocol optimizes reads.

## Heterogeneous agents

- **Claude Code / Codex / Cursor:** full protocol. They discover it via `AGENTS.md` §4 and this skill.
- **Local/small models:** restricted lane. Give them `prompt-templates/04-bridge-worker.txt` as their system/session prompt: Level 0/1 tasks only, must claim before editing, must log `done`/`blocked` with the same schema, must not touch governance files (`AGENTS.md`, `CLAUDE.md`, `docs/ai/**` except their own task file appends). Weaker models are executors inside the bridge, not planners.
- **Humans:** may append ledger events too (`a:"human-..."`); a human edit without an event is what "Do not overwrite undocumented work" protects against.

## Quality criteria

- A second agent can resume any in-flight task from board + tail + one task file, with zero chat context.
- No two agents edit the same file under overlapping claims.
- Boot cost stays flat as the project grows (history growth is absorbed by tail + compaction).

## Checklist

- [ ] Boot sequence run before changes.
- [ ] Claims logged before shared-file edits; released on completion.
- [ ] Events logged at milestones with pointers, not payloads.
- [ ] Task file handoff notes updated before `done`/`handoff`.
- [ ] Board reflects current state; ledger compacted past 200 lines.
