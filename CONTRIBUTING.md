# Contributing to Generic Agent Runtime

Thanks for considering a contribution to GAR. This project governs its own
development using the same principles it ships to others: explicit scope,
evidence before claims, and no silent overwrites. Contributions are expected
to follow that spirit.

## Before you start

- Read the [Code of Conduct](CODE_OF_CONDUCT.md).
- For anything beyond a small fix (new behavior, a new skill, a change to
  `AGENTS.md` or a schema), please open an issue first using the
  [Feature request template](.github/ISSUE_TEMPLATE/feature_request.yml) to
  discuss the approach before investing time in an implementation.
- Found a security issue? Do **not** open a public issue — see
  [SECURITY.md](SECURITY.md) instead.

## Ground rules

- **Model and stack neutrality.** GAR must keep working the same way across
  Claude, Codex, Gemini, and other repository-aware agents. Avoid changes
  that hard-code behavior to a single vendor or model.
- **No silent overwrites.** Any tooling change that touches adoption,
  bootstrap, or file generation must preserve GAR's plan-before-write and
  non-destructive-by-default behavior.
- **Evidence before claims.** If a change affects validation, security, or
  release behavior, show the command output or test result that backs it up
  in your PR description, not just a description of the intent.

## Development setup

Requirements: Python 3.9 or newer. Runtime tooling uses only the Python
standard library, so no extra install step should be required.

```bash
git clone https://github.com/carlos-h-gomes/generic-agent-runtime.git
cd generic-agent-runtime
```

## Validating your changes

Before opening a PR, run:

```bash
bash scripts/validate.sh
bash scripts/validate.sh --full
```

Both should pass, or you should be able to explain in your PR why a specific
check is not applicable.

## Making changes

- Keep pull requests focused and scoped to one change.
- Update the relevant documentation (`docs/TECHNICAL-DOCUMENTATION.md`,
  `docs/USER-MANUAL.md`, `CHANGELOG.md`) whenever the change is material or
  user-visible — this mirrors the documentation-impact rule already in
  [`AGENTS.md`](AGENTS.md).
- Never commit secrets, credentials, or real project/customer data, including
  in test fixtures or examples.

## Submitting a pull request

1. Fork the repository and create a branch for your change.
2. Make your change and run the validation commands above.
3. Open a PR using the provided template and fill in the checklist honestly —
   including any check you skipped and why.
4. Link the related issue if one exists.

Maintainer-side release and packaging process is documented separately in
[docs/harness/MAINTAINER.md](docs/harness/MAINTAINER.md) and is not required
reading to submit a contribution.

## Questions

Open a [bug report](.github/ISSUE_TEMPLATE/bug_report.yml) or
[feature request](.github/ISSUE_TEMPLATE/feature_request.yml) issue if you're
unsure where something belongs.
