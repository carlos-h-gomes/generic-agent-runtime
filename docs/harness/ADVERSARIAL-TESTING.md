# Controlled Adversarial Testing

`scripts/adversarial_lab.py` performs bounded HTTP contract checks. It is deliberately not a general-purpose exploit runner.

## Modes

- `plan`: validates schema, origin, paths, methods, headers, and budgets; sends no traffic.
- `execute`: permits safe methods on a loopback-only origin without a scope file.
- External/non-loopback execution and every `POST` require an unexpired `authorized-target` contract with an exact canonical origin.

The runner limits methods, requests, response bytes, timeouts, headers, redirects, DNS stability, and path prefixes. It never prints response bodies. Destructive actions, credential headers, arbitrary payload engines, port scanning, evasion, persistence, and denial-of-service behavior are outside its contract.

## Workflow

1. Use synthetic fixtures in a disposable local environment.
2. Validate with `python scripts/adversarial_lab.py plan --plan security/examples/loopback-plan.json`.
3. For staging, copy the authorization example outside source control and fill a narrow scope, owner, approval reference, and short validity window.
4. Start with safe methods and a small request budget.
5. Stop on unexpected state change, authentication impact, instability, scope ambiguity, or changed DNS.
6. Store only redacted summaries and hashes as evidence.

Authorization represents permission recorded by the operator; the Harness cannot independently verify legal ownership.
