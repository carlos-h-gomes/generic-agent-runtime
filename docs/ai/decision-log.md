# Decision Log

Append durable decisions; mark supersession explicitly. Do not store chat transcripts or hidden reasoning.

## 2026-08-04 — Separate governance adoption from application architecture and bound n8n to edge orchestration

Status: active
Supersedes: implicit v6 admission behavior that assumed the target Python/React profile for any detected application

### Context

Harness v6 handled a new Python/React project well but did not provide a safe, explicit contract for adopting an existing stack or upgrading a prior Harness. Automation routing also lacked a normative boundary between code and n8n.

### Decision

Treat governance adoption, application bootstrap, architecture migration, and deployment as separate authorized operations. Classify adoption as greenfield, brownfield, or upgrade; classify files as Harness-owned, project-owned, shared, or generated; use plan/apply/verify with digest-bound approvals and rollback evidence. Code owns authoritative business behavior. n8n may orchestrate bounded edge workflows, and hybrid workflows call versioned code APIs when both planes are needed.

### Alternatives and reasons

- Always generate the default Python/React structure: rejected because it mutates brownfield architecture without consent.
- Merge files heuristically during installation: rejected because ambiguous ownership makes silent data loss possible.
- Allow pure n8n whenever a workflow is visually convenient: rejected because convenience does not satisfy authority, consistency, security, recovery, or cost constraints.

### Consequences and residual risks

Adoption becomes more explicit and occasionally requires reconciliation approval. Existing stacks are preserved by default. A local Harness qualification does not validate a downstream repository or n8n deployment; those environments still require their own security, cost, observability, backup, and model-host evidence.

### Follow-ups

Run the behavioral suite on each intended model/host and require project-specific adoption and automation decisions before rollout.
