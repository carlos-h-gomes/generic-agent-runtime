---
name: software-architecture-uml
description: "Explicit specialist review for Level 2/3 architecture, contracts, data ownership, workflows, queues, or deployment boundaries."
---

# Software architecture gate

Return a `GateResult` conforming to `schemas/gate-result.schema.json`.

## Analyze

- actors, systems, modules, trust and data boundaries;
- responsibilities, dependency direction, ownership, and coupling;
- synchronous/asynchronous flows and transaction/concurrency boundaries;
- contract shape, versioning, backward compatibility, and migration;
- failure, timeout, retry/degradation, rollback, and recovery paths;
- security, performance, cost, and operational constraints supplied by other gates;
- at least one viable alternative and the reason it was rejected.

Inspect current code and documented decisions first. Do not design from generic best practice alone.

Brownfield admission preserves the verified architecture; migration requires a separate approved decision. For greenfield work, reuse an explicit user choice or present relevant options when a material choice is missing. Review the approved open profile's roots, modules, responsibilities, dependency direction, contracts, and verification adapters. Treat entry files as composition roots and block single-file monoliths while allowing thin startup, provider, router, middleware, and layout assembly. `python-react-hybrid` is an optional compatibility profile.

For integrations and automation, identify the system of record and authority before recommending any user-named component. Category or connector availability never grants authority; record component contracts, failure behavior, security, cost, rollback, and ownership in the open solution decision.

## Artifact

Create a concise Markdown decision for every triggered gate. Include outcome, context, affected boundaries, responsibilities, contracts, failure behavior, compatibility/migration, alternatives, risks, and implementation constraints. Add only the smallest useful view:

- C4 context/container for system boundaries;
- component for module relationships;
- sequence for multi-step or asynchronous flows;
- class/domain for ownership and invariants;
- state for lifecycle/retry transitions;
- deployment for runtime topology.

Text must remain understandable without rendering the diagram.

Block implementation when ownership, contract compatibility, failure behavior, or migration safety is unresolved. Do not own detailed data retry semantics, security severity, implementation, or release execution; coordinate those with their specialist gates.
