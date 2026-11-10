---
name: minimalism
description: "Review a proposed change for unnecessary concepts, dependencies, branches, and operational surface without weakening safeguards."
---

# Minimalism

Minimalism sizes the solution, not the safeguards.

## Decision order

For each proposed element, ask:

1. Does it need to exist to satisfy an acceptance criterion or required control?
2. Can the platform or standard library solve it clearly?
3. Can an existing dependency or project pattern solve it without distortion?
4. What is the smallest coherent new implementation?

Do not optimize for a one-liner. Readability, explicit failure handling, and test seams are part of coherence.

## Scope review

Measure the change by:

- new concepts and abstractions;
- new dependencies and configuration;
- branches, states, and compatibility paths;
- data migrations and external contracts;
- permissions, jobs, observability, and operational surface;
- maintenance burden for the next agent.

Delete speculative flexibility, duplicate helpers, unused flags, premature abstraction, and unrelated refactoring. Prefer a local direct implementation until demonstrated repetition or a real boundary justifies abstraction.

For governance artifacts, prefer this order: reuse the authoritative artifact, return an inline review, update one existing review home when authorized, then create the smallest schema-valid formal set only when continuity or a required gate needs it. Read-only review does not authorize task, decision, gate, or `docs/ai` creation. Risk changes the depth of reasoning, not the write boundary or the number of files. Never create per-gate files as a substitute for a concise production-readiness conclusion.

## Safety floor

Never reduce input validation, authorization, privacy, accessibility, test coverage required by the task, rollback/data-loss handling, rate/cost limits, monitoring required for release, or durable context required for safe handoff.

Return a short delete/avoid list and the minimal design chosen. If the minimal safe solution cannot meet acceptance criteria, say so rather than hiding the gap.
