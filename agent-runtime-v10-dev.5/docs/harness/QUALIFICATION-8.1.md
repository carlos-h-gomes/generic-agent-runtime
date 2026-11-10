# Generic Agent Runtime 8.1 qualification

Status: qualified 8.1.0 release source on 2026-08-31. This document records local release evidence; it does not authorize deployment or production mutation.

## Scope

Version 8.1 adds reversible workspace hygiene to the frozen v8.0 RC baseline. The feature inventories and plans before mutation, uses owner-bound `_archives` bundles, verifies hashes and index records, reverses failed moves, and restores only to collision-free original paths. It does not implement purge, retention deletion, Git rewriting, remote storage, or automatic archival during adoption.

The pre-publication review also adds a concrete downstream product security and privacy baseline. It covers common omissions in fast AI-assisted development across identity, sessions, authorization, request/resource budgets, sensitive business-flow abuse, browser and API controls, SSRF, uploads/parsers, webhooks, supply chain, containment, recovery, and LGPD. The baseline governs questions and evidence; it does not implement downstream controls or certify compliance.

Baseline archive SHA-256: `8B0A798F35AFFB7FF9D046158818A99EC9959B75867F64BF08C7D8CE2820EEF2`.

## Source evidence

- Focused workspace-hygiene suite: 14 passed, including real Windows direct and nested junction rejection; one ordinary symlink test skipped because the local account cannot create symlinks.
- Complete runtime suite: 65 passed, two expected skips, exit 0. The added regression asserts concrete security/LGPD baseline coverage.
- Strict runtime check: 240 passed, one optional external `jsonschema` meta-schema validator skipped, zero failures.
- Full PowerShell profile: lint, functional, architecture, documentation, runtime, package plan, security, and UI checks passed.
- Synthetic CLI lifecycle: inventory, plan, apply, verify, and restore all exited 0; the restored fixture SHA-256 matched its original and the historical index remained present.

The host cannot create an ordinary symbolic link without administrator privilege, so that variant remains an expected skip. The equivalent Windows reparse boundary was exercised with real junctions at the workspace root, as a direct candidate, and nested below a selected directory; every case was rejected before a plan or move and the outside marker remained unchanged. The built-in schema validator passed; the optional external `jsonschema` package was unavailable and is not represented as a pass.

## Release identity and portability

The deterministic archive digest, entry count, path/link/resource inspection, internal `MANIFEST.sha256` verification, and clean-extraction runtime result are recorded in the external governed task evidence after packaging. Keeping the archive's own digest outside its payload avoids a circular self-hash claim.

## Boundaries

This qualification covers the Harness distribution and synthetic local fixtures only. It does not establish that any downstream application, host, VPS, network, model, tool, deployment, or production environment is secure. Applying workspace hygiene to current user material remains a separate exact authorization.
