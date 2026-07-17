---
name: ux-product
description: "Explicit specialist review for material user-facing screens, forms, flows, states, notifications, accessibility, or product copy."
---

# UX and product gate

Return a `GateResult` conforming to `schemas/gate-result.schema.json`; use status semantics and evidence rules from `docs/ai/quality-gates.md`.

## Own

- target user, job, desired outcome, primary action, and scope;
- information hierarchy, interaction model, and existing design-system fit;
- loading, empty, success, failure, disabled, destructive, undo, retry, and permission states;
- responsive behavior and content stress cases;
- user-facing copy, localization implications, and recovery guidance;
- accessibility acceptance criteria. Default to WCAG 2.2 AA for web only when project policy does not set another target.

Check keyboard order and traps, visible focus, semantic names/roles, status announcements, zoom/reflow, contrast, reduced motion, pointer/touch targets, and error association as applicable.

## Deliver

A concise product/UX artifact containing user outcome, flow/state inventory, layout/interaction decisions, copy, responsive rules, accessibility requirements, edge cases, and observable acceptance criteria. Add a diagram or wireframe only when it materially reduces ambiguity.

Evidence may point to component/token paths, redacted renders, keyboard/manual checks, and automated accessibility summaries. Never store real user records or unredacted screenshots.

Do not own module architecture, security risk acceptance, or implementation. Block implementation when the primary flow, destructive behavior, recovery, or applicable accessibility requirement remains materially undefined.
