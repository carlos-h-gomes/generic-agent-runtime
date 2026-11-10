# Promotion Records

Store one schema-valid `<release-id>.promotion.json` per candidate only when a release workflow is authorized. A record binds artifact, non-secret configuration, migration, policy, staging evidence, gates, approval, production outcome, monitoring, and rollback. Never store secret values, raw production data, or unrestricted logs here.

Use promotion schema 2.0. Preserve earlier receipts as history; never relabel or fabricate evidence. `production_approved` requires exact policy/staging evidence bindings and prepared monitoring/recovery. Completion requires passed production checks. See `../../harness/ENVIRONMENT-PROMOTION-POLICY.md` for chronology, validity and readiness rules.
