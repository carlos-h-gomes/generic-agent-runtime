# GEMINI.md — Generic Agent Runtime adapter

@AGENTS.md

`AGENTS.md` is the source of truth. Keep Gemini-specific configuration thin:

- Load project memory and skills only when the task router selects them.
- Use bounded native subagents only when the host exposes them and the orchestration suitability test passes.
- Do not duplicate or weaken the kernel here; report adapter drift.
