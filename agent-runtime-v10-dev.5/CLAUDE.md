# CLAUDE.md - Generic Agent Runtime adapter

@AGENTS.md

`AGENTS.md` is the source of truth. This adapter adds only Claude-specific behavior:

- Use native subagents for bounded independent work; keep the parent as integrator and default writer.
- Treat `docs/ai/` as project memory and `.agents/skills/` as on-demand procedures.
- On Windows, use `scripts/run.ps1`; on POSIX, use the shell entrypoints documented in `docs/harness/INSTALL.md`.
- Do not duplicate the kernel here. If this file and `AGENTS.md` appear to conflict, follow `AGENTS.md` and report the adapter drift.
