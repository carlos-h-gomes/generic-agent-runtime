---
name: project-profiling
description: "Profile an unfamiliar repository only when commands, boundaries, or project facts are materially unknown or stale."
---

# Project profiling

Profile only enough of the repository to work safely. Do not scan everything by default.

## Procedure

1. Find the repository root, applicable instruction chain, version-control state, and local capability constraints.
2. Read high-signal manifests and entrypoints: README, package/runtime manifests, lockfiles, CI, build files, deployment configuration, and main source directories.
3. Inspect existing `docs/ai/` summaries before source details. Follow pointers progressively.
4. Derive commands only from repository evidence. Run safe discovery flags or existing validation commands when authorized and practical; record exact command, outcome, and environment.
5. Identify stack, package manager, module and data boundaries, external integrations, important paths, generated artifacts, and material security/cost/operational risks.
6. Distinguish current fact, inference, and unknown. Add an evidence pointer for every non-obvious claim.

## Write policy

Inspection is read-only. Write or refresh project memory only when profiling/bootstrap was requested or repository writes are otherwise authorized.

When authorized, prefer these focused files:

- `project-profile.md`: current identity, stack, boundaries, and important paths;
- `commands.md`: commands that were actually verified, including platform assumptions;
- `conventions.md`: project-specific patterns that are not cheaply discoverable;
- `risks.md`: durable material risks;
- `shared-context.md`: current cross-session facts.

Do not copy README prose or file trees. Do not overwrite unresolved user or agent notes. Mark stale entries as superseded or replace them with verified current facts.

## Bootstrap boundary

If the repository lacks a usable memory layer, propose the smallest bootstrap. Do not create governance, validation scripts, or product changes automatically unless authorized. Profiling can precede a separately requested implementation, but it does not silently broaden the task.

## Output

Return the evidence-backed profile or changed memory paths, verified commands, unknowns, and whether the project is ready for triage/implementation.
