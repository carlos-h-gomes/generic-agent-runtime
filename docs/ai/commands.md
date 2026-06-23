# Commands

Status: template. Fill during Project Profiling.

Only document commands verified from repository files such as package files, Makefiles, CI config, Docker files, README, or existing scripts.

## Package manager

- Detected package manager:
- Install command:
- Dev command:
- Build command:

## Validation commands

```bash
# Test

# Lint

# Typecheck

# Build

# Security check (SAST + secrets)

# Dependency / supply-chain scan (SCA, e.g. trivy fs / pip-audit / npm audit)

# Docker/infra check

# Cost/usage check
```

## RTK-aware validation (optional)

If this project uses an output-compressing CLI proxy (rtk), record the wrapped forms of the verified commands here, e.g.:

```bash
# rtk test ./scripts/test.sh
# rtk pytest        # or rtk cargo test / rtk go test
# rtk lint          # or rtk ruff check / rtk tsc
# rtk git status / rtk git diff
```

Notes: the proxy is optional and degrades gracefully to the plain commands; its auto-rewrite hook only covers Bash tool calls (built-in Read/Grep/Glob bypass it); on failure it tees the full output to a file — diagnose from that, not the compact summary.

## Safe commands

Commands agents may run without approval:

```bash
# Example:
# npm test
# npm run lint
# docker compose config
```

## Approval-required commands

Commands that need explicit human approval:

```bash
# production deploy
# destructive migration
# data deletion
# bulk message sending
# paid high-volume execution
# secrets rotation
```

## Command notes

- Do not invent commands.
- Prefer the smallest relevant validation subset.
- Record command failures honestly.
- Never claim validation passed unless it actually ran successfully.
