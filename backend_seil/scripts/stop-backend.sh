#!/usr/bin/env bash
# Stop backend started by start-backend.sh
# Usage: ./stop-backend.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$SCRIPT_DIR/backend.pid"

if [ ! -f "$PIDFILE" ]; then
  echo "No pid file found. Nothing to stop."
  exit 0
fi

PID=$(cat "$PIDFILE" | head -n1)
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Stopped process $PID"
else
  echo "Process $PID not running"
fi
rm -f "$PIDFILE"
