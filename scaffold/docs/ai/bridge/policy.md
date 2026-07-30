# Bridge Policy

- The bridge is advisory coordination, not authentication or authorization.
- Use native host coordination first; use this bridge across tools/sessions or for durable handoff.
- Use unique run and actor IDs. One writer owns each file.
- Claim shared paths before editing and never cross another live overlapping claim.
- Events contain pointers and notes up to 140 characters, never secrets, payloads, customer data, prompts, or full logs.
- Prefer isolated worktrees or filesystem controls when participants are not mutually trusted.
