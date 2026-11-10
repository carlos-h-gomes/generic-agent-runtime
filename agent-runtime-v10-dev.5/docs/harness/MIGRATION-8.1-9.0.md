# Migration from Harness 8.1 to 9.0

Status: v9-dev.2 local candidate guidance dated 2026-09-05.

V9 preserves v8.1 contracts and workspace-hygiene behavior. It adds the `grill-me` skill, communication policy v1, environment policy v2, promotion record v2, and a read-only semantic validator.

## Required migration decisions

1. Verify the v8.1 rollback archive SHA-256 `5d7f083a4ccd8bed2a3df6c4023be41606a41611175facd33478c6fdfb7932f6` through a trusted channel.
2. Use Harness adoption plan/apply/verify. Do not extract v9 over an active repository and do not overwrite project-owned memory.
3. Reconcile shared `AGENTS.md` deliberately so v9 communication, interview, and promotion authority rules are not lost.
4. Preserve an existing project communication policy. Initialize the v1 defaults only when absent; mandatory safety content cannot be disabled.
5. Preserve any existing environment/deployment facts. Map them into `docs/ai/environment-policy.json` only from verified evidence. Unknown isolation and missing staging remain incomplete.
6. Treat `docs/ai/releases/` as project-owned audit history. Never fabricate old promotion receipts or retroactively claim staging evidence.
7. Run the local environment validator before release review. Its pass covers only supplied records, not live cloud state.
8. Keep environment provisioning, credentials, billing, deployment, production mutation, Git, and publication as separately scoped approvals.

Rollback restores the verified v8.1 distribution and adoption rollback copies. Rolling back GAR does not reverse application, infrastructure, data, secret, migration, promotion, or deployment changes; those require project-specific recovery evidence.

## Migrating an earlier GAR 9 development candidate

The reviewed v9-dev.1 environment/promotion contracts used schema 1.0. v9-dev.2 requires 2.0 and rejects 1.0 with exit 2. Keep prior candidate artifacts and receipts as historical evidence; do not overwrite or relabel them.

Create a separate v2 policy from observed facts and attach a reviewed parity receipt bound to the current environment hashes and allowed differences. A planned v2 policy can retain null parity and remains incomplete. Record staging verification, explicit validity and check evidence; prepare monitoring ownership and a rehearsed rollback plan. Use `production_approved` to represent exact approval before deployment. Approval must bind the current policy and staging evidence digests plus source revision; obtain approval again after an identity/evidence change. Never fabricate past verification or approvals to make an old receipt qualify.

Existing task/GateResult, communication, adoption and workspace-hygiene schemas keep their versions. Behavioral qualification must be repeated against the final corrected archive digest; passing results from an earlier candidate or another model are not transferable.
