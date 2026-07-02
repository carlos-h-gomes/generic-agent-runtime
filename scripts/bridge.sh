#!/usr/bin/env bash
# bridge.sh — deterministic mechanics for the agent bridge (see .agents/skills/core/agent-bridge/SKILL.md)
# Pure bash + optional python3. No dependencies. Safe to run from repo root.
set -euo pipefail

BRIDGE_DIR="docs/ai/bridge"
LEDGER="$BRIDGE_DIR/ledger.jsonl"
ARCHIVE="$BRIDGE_DIR/ledger-archive.jsonl"
BOARD="$BRIDGE_DIR/board.md"
COMPACT_THRESHOLD=200

usage() {
  cat <<'EOF'
Usage:
  bridge.sh board                                  Print the current board (one page).
  bridge.sh tail [N]                               Print last N ledger events (default 15).
  bridge.sh log <agent> <event> <task> <note> [files_csv] [next]
                                                   Append one event. event: claim|release|start|progress|done|blocked|handoff|note
  bridge.sh claims                                 Print currently active file claims (claim minus release).
  bridge.sh compact                                Move oldest events to ledger-archive.jsonl when over threshold.
  bridge.sh init                                   Create bridge files if missing.
Notes are hard-capped at 140 chars. Details belong in the task file; the ledger carries pointers.
EOF
}

ensure_files() {
  mkdir -p "$BRIDGE_DIR"
  [ -f "$LEDGER" ] || : > "$LEDGER"
}

json_escape() { # minimal escaper for quotes and backslashes
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

cmd="${1:-}"
case "$cmd" in
  init)
    ensure_files
    echo "bridge ready: $LEDGER, $BOARD"
    ;;
  board)
    [ -f "$BOARD" ] && cat "$BOARD" || echo "No board at $BOARD (run: bridge.sh init)"
    ;;
  tail)
    ensure_files
    n="${2:-15}"
    tail -n "$n" "$LEDGER"
    ;;
  log)
    ensure_files
    agent="${2:?agent required}"; event="${3:?event required}"; task="${4:?task required}"; note="${5:?note required}"
    files_csv="${6:-}"; next="${7:-}"
    case "$event" in claim|release|start|progress|done|blocked|handoff|note) ;; *)
      echo "invalid event: $event" >&2; exit 1;; esac
    if [ "${#note}" -gt 140 ]; then echo "note > 140 chars — move detail to the task file" >&2; exit 1; fi
    if [ -n "$next" ] && [ "${#next}" -gt 140 ]; then echo "next > 140 chars — move detail to the task file" >&2; exit 1; fi
    ts="$(date -u +%Y-%m-%dT%H:%MZ)"
    files_json=""
    if [ -n "$files_csv" ]; then
      IFS=',' read -ra arr <<< "$files_csv"
      parts=""
      for f in "${arr[@]}"; do
        f_trimmed="$(echo "$f" | sed -e 's/^ *//' -e 's/ *$//')"
        parts="$parts\"$(json_escape "$f_trimmed")\","
      done
      files_json=",\"f\":[${parts%,}]"
    fi
    next_json=""
    [ -n "$next" ] && next_json=",\"nx\":\"$(json_escape "$next")\""
    printf '{"ts":"%s","a":"%s","e":"%s","t":"%s"%s,"n":"%s"%s}\n' \
      "$ts" "$(json_escape "$agent")" "$event" "$(json_escape "$task")" \
      "$files_json" "$(json_escape "$note")" "$next_json" >> "$LEDGER"
    echo "logged: $agent $event $task"
    ;;
  claims)
    ensure_files
    if command -v python3 >/dev/null 2>&1; then
      python3 - "$LEDGER" <<'PY'
import json, sys
active = {}  # (agent, path) -> ts/task
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    key_paths = ev.get("f") or []
    if ev.get("e") == "claim":
        for p in key_paths:
            active[(ev.get("a"), p)] = {"since": ev.get("ts"), "task": ev.get("t")}
    elif ev.get("e") in ("release", "done"):
        if key_paths:
            for p in key_paths:
                active.pop((ev.get("a"), p), None)
        else:  # release/done with no files releases all claims of that agent+task
            for k in [k for k, v in active.items() if k[0] == ev.get("a") and v["task"] == ev.get("t")]:
                active.pop(k, None)
if not active:
    print("no active claims")
else:
    for (agent, path), meta in sorted(active.items()):
        print(f"{path}\tclaimed by {agent}\tsince {meta['since']}\ttask {meta['task']}")
PY
    else
      echo "(python3 not found — raw claim/release events below; resolve manually)"
      grep -E '"e":"(claim|release|done)"' "$LEDGER" || echo "no claim events"
    fi
    ;;
  compact)
    ensure_files
    total="$(wc -l < "$LEDGER" | tr -d ' ')"
    if [ "$total" -le "$COMPACT_THRESHOLD" ]; then
      echo "ledger at $total lines (threshold $COMPACT_THRESHOLD) — no compaction needed"
      exit 0
    fi
    keep=100
    move=$(( total - keep ))
    head -n "$move" "$LEDGER" >> "$ARCHIVE"
    tail -n "$keep" "$LEDGER" > "$LEDGER.tmp" && mv "$LEDGER.tmp" "$LEDGER"
    echo "moved $move oldest events to $ARCHIVE; kept last $keep."
    echo "REMINDER: durable knowledge must live in task files / shared-context.md, not in the archive."
    ;;
  ""|help|-h|--help)
    usage
    ;;
  *)
    echo "unknown command: $cmd" >&2; usage; exit 1
    ;;
esac
