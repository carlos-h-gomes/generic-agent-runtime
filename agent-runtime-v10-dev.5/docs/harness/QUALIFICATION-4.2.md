# Harness 4.2 Qualification Record

Release date: 2026-07-17

Status: qualification in progress. Final command counts, archive SHA-256 and extraction evidence are recorded only after the deterministic package is built and verified.

## Required mechanical evidence

- strict source validation;
- Windows PID-probe and live-lock regressions;
- complete runtime functional suite;
- deterministic package plan and repeated-byte hash;
- archive path, metadata and `MANIFEST.sha256` verification;
- strict validation and functional tests from a fresh clean extraction;
- confirmation that active project tasks, bridge history and sensitive file classes are absent.

## Behavioral scope

The behavioral evaluation manifest is unchanged because 4.2 does not alter model routing or approval contracts. Organization-wide rollout still requires representative host/model qualification.

## Claim boundary

Harness 4.2 corrects the identified Harness-controlled Windows process-probe crash. It does not guarantee that the desktop application, operating system, graphics stack, extensions or third-party tools cannot crash for unrelated reasons.
