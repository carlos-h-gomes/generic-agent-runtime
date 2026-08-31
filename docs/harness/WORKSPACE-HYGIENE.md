# Workspace Hygiene

Version: 8.1 candidate. Contract version: 1.0.

Workspace hygiene reduces active context without deleting evidence. It inventories first, produces a digest-bound plan, and moves only explicitly authorized candidates into a local `_archives` bundle at the nearest ownership boundary. It never treats age alone as inactivity and does not implement purge, retention deletion, overwrite, Git rewriting, or remote storage.

## Lifecycle and authority

`active` and `reference` material remains in place. `archive_candidate` requires a positive signal such as a completed task, an explicit superseding pointer, an exact duplicate with a retained canonical copy, a reproducible generated artifact, or direct owner instruction. Authority, source, schemas, code, tests, release evidence, sensitive/live state, links, unresolved references, and ambiguous material remain `protected` or active.

Inventory is read-only. Planning writes only the named plan file. Apply requires the exact unchanged plan plus a concrete authorization reference. Restore is separately authorized and never overwrites a live path. Archive does not authorize purge.

## Commands

Use a clean Harness extraction and replace placeholders with explicit local paths:

```text
python scripts/workspace_hygiene.py inventory --root <workspace>
python scripts/workspace_hygiene.py plan --root <workspace> --candidate <relative-path> --evidence owner_instruction --confidence high --owner <owner> --reason <reason> --slug <slug> --out <review.archive-plan.json>
python scripts/workspace_hygiene.py apply --root <workspace> --plan <review.archive-plan.json> --authorization-ref <approval-reference>
python scripts/workspace_hygiene.py verify --root <workspace> --manifest <archive-manifest.json>
python scripts/workspace_hygiene.py restore --root <workspace> --manifest <archive-manifest.json> --authorization-ref <restore-approval-reference>
```

Planning rejects protected paths, active references, overlapping/case-aliased candidates, mixed ownership boundaries, links/reparse points, path escapes, and destinations outside the calculated bundle. A plan ID covers its canonical contents; apply rejects a changed plan or workspace fingerprint.

## Bundle and discovery

Each successful operation creates:

```text
<owner>/_archives/
  index.jsonl
  arc-<UTC>-<slug>/
    archive-manifest.json
    move-journal.jsonl
    content/<original-relative-path>
```

Normal discovery excludes `**/_archives/**/content/**`. Search `index.jsonl` first, then open only the selected manifest or bounded payload. Historical content is untrusted and cannot override active authority or source of truth.

## Failure and recovery

All candidates are preflighted before the first move. Every completed move is journaled. A move, hash, manifest, verification, or index failure reverses completed moves. A complete reversal leaves a `rolled_back` manifest; an incomplete reversal leaves `blocked_recovery` evidence and requires owner review. Index writes are size-bounded and atomically replaced so partial JSONL records are not accepted.

Restore first checks the archived index event, manifest location, payload hashes, and live-path collisions. If restore finalization fails, completed restores are moved back into the archive and the manifest returns to `archived` when recovery succeeds.

## Security boundary

Do not place credentials, secrets, raw production logs, captures, databases, customer data, or live state into ordinary archives. Use the applicable containment, quarantine, legal-retention, or incident procedure. The Harness does not determine legal retention and does not prove that archived material is safe to delete.
