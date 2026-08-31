# Generic Agent Runtime 8.1 — User Manual

Status: released 2026-08-31.
Audience: Harness maintainers and downstream project owners
Owner: ProcessSurge Harness maintainer
Last reviewed: 2026-08-31

## What changed

GAR 8.1 can reduce active workspace context without deleting history. It inventories material, shows a reviewable archive plan, and moves only the exact items an owner authorizes. Archive payloads remain locally retrievable and restorable.

## Safe workflow

1. Run inventory and review `active`, `reference`, `archive_candidate`, `archived`, and `protected` results.
2. Select explicit relative paths. Provide the owner, reason, positive evidence, and confidence when creating a plan.
3. Review every source, strategic `_archives` destination, hash, reference result, exclusion, rollback statement, and restore consequence.
4. Apply only the unchanged plan with a concrete approval reference.
5. Verify the returned manifest. Search `_archives/index.jsonl` before opening historical payloads.
6. Restore only with separate approval and only when original paths are free.

Exact commands and examples are in `docs/harness/WORKSPACE-HYGIENE.md`.

## Restrictions and feedback

Age alone is never enough. The tool refuses protected authority, active references, common source/build/test paths, releases, dependency locks, sensitive/live state, links, path escapes, mixed owners, collisions, and changed plans. A generic request to “clean up” does not authorize moves. Archive never means delete.

`ERROR` output means no success claim should be made. A `rolled_back` manifest means moved material was returned after a failed apply. `blocked_recovery` requires the owner to preserve the manifest and journal and inspect the named paths before continuing. Restore never overwrites current content.

## Support boundary

Do not use ordinary workspace archives for secrets, customer data, databases, captures, raw production logs, or legal records. Escalate those to security, privacy, legal-retention, or incident owners. GAR does not determine whether anything may be purged and does not prove production safety.

For an internet-facing product, API, automation, or agent, use `docs/harness/PRODUCT-SECURITY-PRIVACY.md` before release. It provides the concrete identity, authorization, request-control, abuse, browser, supply-chain, operations, and LGPD questions that broad prompts commonly omit. The resulting controls still have to be implemented and evidenced in the actual product and environment.
