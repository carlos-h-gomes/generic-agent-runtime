# UI Quality Contract

Material web interfaces use `docs/ai/ui-review.json` as a release contract. A prose claim such as “looks good” is not evidence.

The contract identifies target users, critical journeys, design-system tokens/components, the full interaction-state matrix, narrow and wide viewports, content stress, WCAG 2.2 AA evidence, reviewed visual baselines, and reviewer identity.

Required states are default, loading, empty, success, validation error, system error, disabled, permission, destructive, recovery, degraded/offline, and content stress. A state may be `not_applicable` only with a product-specific reason.

Recommended implementation loop:

1. Define tokens and reusable primitives before page styling.
2. Build states in an isolated component environment when practical.
3. Test critical journeys at keyboard-only and zoom/reflow conditions.
4. Run automated accessibility checks, then manual focus, semantics, contrast, error, and motion review.
5. Capture deterministic visual baselines at a narrow viewport (390 px or less) and a wide viewport (1280 px or more).
6. Review visual diffs; never auto-approve changed baselines in the same unreviewed step.
7. Set the contract to `approved` only after every evidence pointer resolves inside the project.

Automated accessibility checks find only a subset of issues. The machine gate supplements, but does not replace, product and human accessibility review.
