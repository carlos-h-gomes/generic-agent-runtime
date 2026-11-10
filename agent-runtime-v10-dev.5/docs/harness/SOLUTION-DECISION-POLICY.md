# Open Solution Decision Policy

Status: normative for v8. `AUTOMATION-EXECUTION-POLICY.md` remains a v7 compatibility reference.

Use `schemas/solution-decision.schema.json` for material integrations, automation, and multi-component placement. The contract accepts user-named technologies and does not restrict choices to code, n8n, or hybrid.

Each component declares category, technology, responsibilities, authority, system of record, owner, and interfaces. The decision also covers validation and compatibility, timeouts and retries, idempotency and replay, partial failure and reconciliation, least privilege and egress, sensitive-data minimization, versioned artifacts, environment separation, correlation, retention, rollback, kill switch, billing units, volume, caps, and approval.

Categories are descriptive, not authority. A connector does not prove security or production suitability. n8n may be selected and receive vendor-specific review, but it is an optional profile over the universal contract.

`scripts/solution_decision.py` rejects approved decisions with unresolved authority, missing system of record, incomplete universal security controls, missing environment separation, unbounded or unknown material cost, or open approval.
