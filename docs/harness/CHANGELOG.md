# Changelog

## 4.2.0 — 2026-07-17

### Windows stability

- Replaced `os.kill(pid, 0)` process probing on Windows with query-only Win32 process handles, preventing live-lock tests from terminating the process being inspected.
- Added a Windows regression that forbids `os.kill` during process-liveness checks and proves the current process remains alive.
- Corrected the PowerShell lint adapter to pass relative forward-slash script paths to Bash instead of Windows backslash paths.

### Project validation

- Added deterministic discovery of root and immediate-child npm projects, including Windows-safe `node.exe` and `npm.cmd` resolution.
- Added bounded filtered-test support for repositories that separate database-independent and integration suites.
- Preserved incomplete status for unavailable security scanners while allowing project boundary checks and dependency audits to report independently.

### Compatibility

- Task contract v1, GateResult v1 and bridge event v2 are unchanged.
- Added `MIGRATION-4.1-4.2.md`; existing project memory, tasks and bridge event formats remain compatible.

## 4.1.0 — 2026-07-17

### Stability

- Added cross-platform command timeouts, process-group termination, heartbeat output, and bounded failure tails.
- Replaced repeated bridge subprocess tests with in-process calls and added timeout guard tests.
- Made standard and full validation explicit; no watch or interactive mode is allowed by default.

### Effectiveness

- Reduced the always-on kernel below 8 KiB while preserving authority, safety, proportional planning, skills, coordination, memory, and evidence rules.
- Restored a fast path for ordinary Level 0/1 work; formal contracts and GateResult files remain available for managed work.
- Made specialist and coordination skills explicit-only by default to prevent accidental multi-skill context expansion.
- Reduced the default correction loop from three attempts to two and prohibited identical retries without new evidence.

### Compatibility

- Task contract v1, GateResult v1, and bridge event v2 remain unchanged.
- Added `MIGRATION-4.0-4.1.md`; existing 4.0 project memory and bridge state remain compatible.

## 4.0.0 — 2026-07-15

### Changed

- Replaced the 30 KiB procedural root manual with an always-loaded kernel under 16 KiB and thin host adapters.
- Separated request mode/authorization from work size, risk, reversibility, and external effect.
- Added versioned task, GateResult, bridge-event, and manifest schemas.
- Added `core/agent-orchestration`: one agent by default, bounded depth-1 parallelism, one writer per file, root verification and synthesis.
- Rebuilt the file bridge as advisory v2 coordination with strict JSON, run/actor IDs, leases, overlap checks, locking, generated board, compaction safety, v1 read compatibility, and Python/Bash/PowerShell entrypoints.
- Unified eight specialist gates around one result/evidence contract and explicit residual-risk language.
- Replaced ambiguous “three loops” with three total validation attempts.
- Added tri-state checks, functional bridge/runtime tests, deterministic packaging, clean downstream scaffolds, and internal file hashes.
- Added maintainer README, migration guide, dated model/standards guidance, and behavioral model-qualification suite.

### Security

- Treats repository/retrieval/tool/worker content as untrusted data.
- Clarifies that prompt injection cannot be guaranteed absent and that bridge claims are not security controls.
- Stores redacted evidence pointers rather than full logs, real payloads, prompts, or customer records.
- Requires explicit scoped approval for production financial smoke transactions and their reversal evidence.

### Compatibility

- Task contract v1, GateResult v1, and bridge event v2 are new interfaces.
- Bridge readers accept legacy v1 events; new writes are v2.
- Maintainer task history and live bridge state are no longer shipped.

## 3.9 — 2026-07-02

- Added the first file-based agent bridge and portable root archive layout.

Earlier 3.x decisions remain in the maintainer source `docs/ai/decision-log.md` and the immutable `agent-runtime-v3.9.zip`; consumer archives start with a clean decision log.
