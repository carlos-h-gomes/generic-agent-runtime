# Migration from Harness 7.0 to 8.0

Status: candidate guidance pending full v8 qualification.

V8 preserves v7 task, GateResult, bridge, adoption, security, legacy architecture-policy, project-template, and automation-decision contracts for reading. It adds open architecture, solution, reuse, and model-capability contracts.

## Required migration decisions

1. Verify the v7 rollback archive SHA-256 `89c0f481006ff85e787bb2f939c46b11c1b7c3be207fe05b39d05437cc51df3b` through a trusted channel.
2. Use Harness adoption plan/apply/verify; do not overwrite project-owned memory.
3. Keep an existing Python/React policy valid until the owner chooses to convert it. The template remains available.
4. For a new or changed application profile, record the observed or user-approved v2 architecture profile. Do not migrate code implicitly.
5. Read existing `code | n8n | hybrid` decisions as v7 history. Create a v2 open solution decision only when the workload changes or is reapproved; preserve audit history.
6. Add reuse decisions only for material new work, not retroactively for every module.
7. Enable GPT-5.6 Sol or Daybreak Blue profiles only after project choice, access detection, current-source review, budgets, and representative evals.
8. Keep answer, inspection, diagnosis, review, and production-readiness assessment read-only unless persistence is separately authorized. Reuse existing governance artifacts; validate every required formal task, decision, and GateResult against its canonical schema before citing it as evidence.

Rollback restores the verified v7 distribution and project-owned backups created by adoption. Rolling back the Harness does not automatically reverse application, data, integration, or model-routing changes; those require project-specific rollback evidence.
