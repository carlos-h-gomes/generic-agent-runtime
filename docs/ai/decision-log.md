# Decision Log

Append durable decisions; mark supersession explicitly. Do not store chat transcripts or hidden reasoning.

## 2026-08-24 — Open architecture and solution choice; require reuse-first analysis

Status: active
Supersedes: the universal portions of the 2026-08-04 decision that made Python/React the greenfield default and restricted automation outcomes to code, n8n, or hybrid. The v7 contracts remain compatibility profiles.

### Context

The v7 policies safely preserved brownfield stacks, but greenfield generation still embedded the maintainer's current Python/React and n8n preferences. They also lacked a durable decision showing whether existing modules, contracts, tests, and dependencies had been considered before new code was proposed.

### Decision

Use open architecture and solution contracts. Reuse a material choice already supplied by the user; otherwise recommend relevant alternatives with concise reasons and wait for the user's choice. Preserve brownfield architecture unless migration is separately authorized. Before material implementation, inventory compatible assets and record whether each is reused, extended, adapted, replaced, or newly created. Enforce thin composition roots and declared dependency direction without prescribing a universal directory tree. Keep GPT-5.6 Sol and Daybreak Blue as optional capability profiles whose use depends on verified access, task fit, and unchanged authorization boundaries.

### Alternatives and reasons

- Default every greenfield project to Python/React: rejected because Harness implementation choices are not user requirements.
- Replace the code/n8n/hybrid enum with another fixed vendor list: rejected because the list would encode a new local preference and age quickly.
- Demand maximum decomposition: rejected because speculative layers make simple projects harder to understand.
- Treat model availability as authority: rejected because access and capability do not grant target, tool, data, or production permission.

### Consequences and residual risks

The Harness becomes more adaptable and reduces needless code, but architecture review must evaluate project-specific profiles rather than compare every repository with one tree. Static anti-monolith checks remain heuristic and require human review. Tool and model capability claims can become stale or unavailable and must be reverified.

### Follow-ups

Execute the version-8 behavioral suite on every intended model/host before release claims, including unavailable-model fallback and user-choice scenarios.

## 2026-08-04 — Separate governance adoption from application architecture and bound n8n to edge orchestration

Status: partially superseded by the 2026-08-24 open-choice decision; adoption separation and n8n-specific safety controls remain active
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
