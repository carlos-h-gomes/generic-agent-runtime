# Safe Installation

Harness files intentionally share names with project governance, scripts, schemas, and memory. Do not extract this archive directly over an active repository.

1. Extract `agent-runtime-v4.2.zip` into a new staging directory.
2. Verify `MANIFEST.sha256` and run `python scripts/runtime_check.py` in staging.
3. Inventory collisions against the target repository, including `AGENTS.md`, adapters, `.agents/`, `scripts/`, `schemas/`, `prompt-templates/`, and `docs/ai/`.
4. Merge deliberately. Preserve nearer project-specific instructions, verified commands, constitution, decisions, risks, active tasks, live bridge ledger, and unrelated scripts.
5. Run the target repository's existing validation plus the merged Harness validation.
6. Initialize the bridge only after preserving or reconciling any existing bridge history.

The archive relocates Harness release notes to `docs/harness/` so it does not overwrite a project's root README or changelog. Root governance/script collisions remain intentional and require review.
