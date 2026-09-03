# Security Policy

## Scope

This project is a governance and validation harness. It reduces accidental
authority and makes missing evidence visible. It is not a sandbox, an EDR, a
vulnerability scanner, or proof that any application built with it is secure.
See `docs/harness/SECURITY-MODEL.md` for the trust boundaries and the residual
risks the project explicitly does not cover.

## Supported versions

Only the latest released version receives fixes.

| Version | Supported |
|---------|-----------|
| 8.1.x   | yes       |
| 7.0.x   | no        |
| < 7.0   | no        |

## Reporting a vulnerability

Please do not open a public issue for security problems.

Use GitHub private vulnerability reporting on this repository (Security tab,
"Report a vulnerability"). Include the affected version, the component,
reproduction steps and the impact you observed.

Expect an acknowledgement within 7 days. If a fix is warranted it lands in the
next release with a `CHANGELOG.md` entry.

## Out of scope

- Vulnerabilities in downstream applications generated or governed by the harness
- Vulnerabilities in the AI models, tool hosts or providers the harness coordinates
- Findings that require an operator to pass `--trust-project-code` against code
  they already control
