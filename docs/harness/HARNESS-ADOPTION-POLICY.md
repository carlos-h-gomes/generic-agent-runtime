# Harness adoption and reconciliation policy

Version: 2.0
Applies to: Harness 8 installation, adoption, and upgrade

## Non-negotiable separation

These are four different operations with independent authorization:

1. Install or upgrade Harness governance.
2. Bootstrap a new application profile.
3. Migrate an existing application architecture.
4. Deploy or change a runtime environment.

Adopting the Harness never authorizes the other three. The first target interaction is a read-only inventory and plan.

## Classification axes

Classify independently:

- adoption mode: `greenfield`, `brownfield`, or `upgrade`;
- Harness posture: absent, current, prior supported, or modified/unknown;
- application posture: empty, architecture profile recorded, observed existing stack, or unknown;
- architecture disposition: initialize target, preserve, profile required, or migration required.

Missing `backend/` or `frontend/` is not evidence that an existing application is absent. Inspect manifests, source roots, deployment files, and current project memory.

## Scenario behavior

### Greenfield

- Install governance and clean project-memory templates.
- Reuse any language, framework, topology, and tool choice already made by the user.
- If a material choice is missing, present relevant options with recommendations and tradeoffs, then wait for the user's decision before generating application code.
- The bundled Python API plus React TypeScript/Vite template is optional. Its directories are created only by the separate `bootstrap_project.py plan/apply` flow after that profile is selected and application bootstrap is explicitly authorized.

### Brownfield without Harness

- Preserve the verified language, framework, topology, commands, code, documentation, and deployment model.
- Install only non-conflicting governance content.
- Do not create `backend/`, `frontend/`, application entrypoints, or dependency manifests.
- Do not copy the default `docs/ai/architecture-policy.json`; project profiling must record an observed policy before architecture validation can pass.
- Any desired architecture migration becomes a separate Level 2/3 task with characterization, compatibility, staged movement, and rollback.

### Upgrade from an older Harness

- Verify the installed version and use every migration guide required between versions.
- Harness-owned files may be replaced only from a manifest-verified source, with explicit replacement approval and a rollback copy.
- Preserve project-owned memory, tasks, decisions, risks, commands, incident records, bridge history, product documentation, and application code.
- A differing shared file requires deliberate reconciliation; the tool does not choose a side.
- Upgrading the Harness never changes the application architecture.

## Ownership classes

`adoption-policy.json` is the machine inventory of ownership:

- `harness`: portable schemas, skills, scripts, prompts, templates, security fixtures, Harness documentation, and release policy indexes;
- `project`: truth index, project memory, active tasks, bridge state, product documentation, and architecture map;
- `shared`: root instructions, model adapters, and project security policy that require reconciliation when different;
- `generated`: `.harness/adoption-state.json`, created from the reviewed plan.

For a first-time brownfield adoption, an existing path that resembles a Harness-owned path is still a conflict. Ownership cannot be claimed from a filename alone.

## Plan, apply, and verify

Run from a separately verified, cleanly extracted portable distribution:

```text
python scripts/adopt_harness.py plan --target <project-root> --out <plan.json>
python scripts/adopt_harness.py apply --target <project-root> --plan <plan.json>
python scripts/adopt_harness.py verify --target <project-root>
```

`plan` performs no target writes. `--out` writes only the requested plan artifact outside target governance unless the operator deliberately chooses a target path. Review the complete operations list and conflicts. After manually reconciling a shared file, rerun plan with `--accept-shared <path>`; the plan preserves that exact target hash and any later change invalidates apply.

`apply` verifies the source manifest, plan digest, source fingerprint, target fingerprint, exact destination states, path containment, and linked/reparse ancestors before any write. Conflicts block. Harness-owned replacements additionally require `--approve-replace`; replaced files receive a rollback copy under `.harness/rollback/<plan-digest>/`.

`verify` performs no writes and checks installed Harness identity, generated adoption state, expected Harness-owned content, and preserved project-owned paths. Validation does not execute downstream project code.

Apply is bounded and attempts rollback after an unexpected local write failure. A failed rollback is a blocker requiring manual recovery from the recorded rollback directory; do not repeat apply without reconciling state.

## Completion

Adoption is complete only when no conflict remains, the installed identity matches the reviewed source, project-owned content is preserved, the adoption state is current, applicable migrations are recorded, and Harness structural validation passes. Brownfield application architecture may remain `profile_required`; that is an honest incomplete architecture gate, not an installation failure.
