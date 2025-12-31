#!/usr/bin/env bash
# Start backend using uvicorn in background and save PID to scripts/backend.pid
# Usage: ./start-backend.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$BACKEND_ROOT/app"
PYTHON="$BACKEND_DIR/.venv/bin/python"
PIDFILE="$SCRIPT_DIR/backend.pid"
LOGFILE="$BACKEND_ROOT/logs/backend.log"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Backend appears to be running (pid $(cat "$PIDFILE")). Aborting start."
  echo "Logs: $LOGFILE"
  exit 0
fi

if [ ! -x "$PYTHON" ]; then
  echo "Virtualenv python not found. Run ./setup-backend.sh first." >&2
  exit 1
fi

(cd "$BACKEND_DIR" && nohup "$PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOGFILE" 2>&1 & echo $! > "$PIDFILE")
PID=$(cat "$PIDFILE")
echo "Started backend (pid: $PID). Logs: $LOGFILE"
