#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
PYTHON="$(harness_python)"
exec "$PYTHON" "$SCRIPT_DIR/bridge.py" "$@"
