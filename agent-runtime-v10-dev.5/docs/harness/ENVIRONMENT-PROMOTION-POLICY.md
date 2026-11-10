# Environment and Promotion Policy

Version: 2.0. Machine contracts: `schemas/environment-policy.schema.json` and `schemas/promotion-record.schema.json`. Introduced in the v9-dev.2 local correction, 2026-09-05; this is not a published release.

Every governed greenfield project plans at least two distinct managed targets: `staging` and `production`. Local development does not replace staging. GAR creates and validates contracts; infrastructure provisioning and deployment remain separate, provider-specific, explicitly authorized actions.

## Environment policy

`docs/ai/environment-policy.json` records owners, lifecycle state, identity/secrets/data/storage/network boundaries, non-secret configuration and topology digests, staging-data strategy, allowed structural differences, promotion controls, and cost guardrails.

Staging and production must use separate identity, secrets, data, storage, and network boundaries for production readiness. Structural parity means equivalent required topology and policy, not identical scale, domains, credentials, quotas, or data. Staging defaults to synthetic or anonymized data. A production-data exception requires a controlled evidence reference covering purpose, minimization, access, retention/deletion, owner, and privacy/legal review.

Brownfield and upgrade adoption inventories what exists. Missing staging or uncertain isolation becomes an incomplete release condition; it never authorizes automatic infrastructure mutation.

### Structural parity evidence

A ready v2 policy requires a `parity` receipt; planned defaults leave it null. An authorized reviewer records a bounded evidence reference, review timestamp, policy revision, both observed configuration/topology hashes, matching normalized topology hashes, and the observed difference categories. The categories must be contained in `allowed_structural_differences`. Distinct raw hashes require an explanation; equal raw hashes do not replace a review. Unknown reviewer, identity, normalized comparison or evidence is incomplete.

The reviewer compares equivalent required services, interfaces, isolation and deployment structure after excluding only the declared differences. GAR checks the supplied receipt and bindings; it cannot compute or authenticate the underlying environment comparison without a provider adapter. Never invent a normalized hash or reference to make the check pass. A changed raw configuration/topology hash invalidates the corresponding parity receipt.

## Promotion record

Each `docs/ai/releases/<release-id>.promotion.json` is one candidate lifecycle and its release receipt. It binds source revision, artifact digest, non-secret configuration digest, migration identity, policy revision, staging deployment/checks/gates/rollback, exact approval, production deployment, smoke check, monitoring, and rollback status.

Normal production promotion requires:

- a verified staging target;
- the exact same artifact digest tested in staging;
- unchanged configuration, migration, policy revision, and required gate evidence;
- passed staging tests/gates and rehearsed rollback;
- exact scoped production approval;
- no conflicting production promotion;
- a monitoring owner/window and rollback trigger.

Any identity drift invalidates downstream evidence and requires a new staging revision. Approval for one digest or policy revision cannot be reused for another.

### Identity and exact approval

The candidate `configuration_sha256` identifies its immutable release configuration bundle. Environment policy hashes identify resolved non-secret target configuration and may legitimately differ. Their relationship is bound by `environment_policy_sha256`, computed over the full current policy with only the top-level `$schema` metadata removed. Canonical encoding is UTF-8 JSON with sorted keys, `ensure_ascii=False`, compact comma/colon separators, and no trailing newline. `canonical_digest()` in `scripts/environment_check.py` implements this format.

Approval binds source revision, artifact/configuration/migration identity, policy revision and full policy digest, and `staging_evidence_sha256`. The last digest uses the same canonical encoding over the complete staging object. Changing check status, check evidence reference, rollback rehearsal or the validity window requires fresh review and exact approval. These hashes detect mismatches; they are not signatures or authorization to deploy. Supply the current policy from a separately trusted source; replacing both a record and its purported authority cannot be detected by self-consistency checks alone.

### States, time and prerequisites

The normal path is `draft -> staged -> staging_verified -> awaiting_production_approval -> production_approved -> promoted -> monitoring -> completed`. `production_approved` is the undeployed readiness state. Recording that state requires exact approval, a monitoring owner/window, rollback plan reference, measurable trigger, rehearsal and available recovery. Those prerequisites remain required in normal deployed states. Actual monitoring may be `not_started` in `production_approved` or `promoted`; it must be active/passed in `monitoring` and passed in `completed`.

Staging records deployment and verification times, `valid_until`, and a controlled `checks_evidence_ref`. Chronology is staging deployment <= verification <= approval <= production deployment. The validity window must be positive and include approval and deployment; undeployed readiness uses current UTC time. Historical completed/deployed receipts are checked against their recorded deployment time and do not fail solely because time later passed. Future observations, reversed ordering, stale policy/parity bindings and approval after expiration block. Missing verification, validity or check evidence is incomplete. Projects set their own reviewed validity window; the template does not invent one.

`promoted` may still have production checks `not_run`; explicit failed/incomplete checks block normal progress. `monitoring` and `completed` require production tests, gates and smoke checks to have passed. Successful completion cannot hide a failed monitoring or recovery status. A restored previous artifact belongs to `rolled_back` and requires verified rollback evidence; it does not mean the attempted new behavior succeeded.

With a promotion supplied, `--require-production-ready` also requires `production_approved` or an applicable deployed receipt. A draft/staged/awaiting-approval record can be consistent without being ready. Without a promotion, the flag checks environment prerequisites only. State records do not implement an atomic deployment lock or independently prove a transition history.

## Failure, rollback, and break-glass

Only one production promotion may be active per project/environment pair. Conflicts block instead of racing.

Rollback to a previously verified artifact and containment actions use incident authority and are not normal promotion. New hotfix behavior may use an abbreviated staging window, but staging, incident identity, exact approval, rollback, monitoring, and post-incident review remain required. Recovery is not complete until restored state is verified; otherwise the record is `blocked_recovery`.

## Cost

Before provisioning approval, the selected provider/region must have a dated official pricing source, currency and billing units, expected/burst/worst-case monthly formulas, hard cap, alert owner, automatic degradation, retention controls, and kill switch. GAR never invents current prices or treats provider quotas as project caps.

Use `scripts/environment_check.py` for local read-only schema and semantic validation. A pass proves only the supplied contract and evidence references; it does not prove a live environment, deploy, application, network, or production system.
