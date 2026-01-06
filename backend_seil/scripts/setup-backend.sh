#!/usr/bin/env bash
# =============================================================================
# Setup backend venv and install requirements (usa "uv")
# Ejecutar desde: backend_seil/scripts
# Usage: ./setup-backend.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$BACKEND_ROOT/app"
VENV_DIR="$BACKEND_DIR/.venv"
REQ="$BACKEND_DIR/requirements.txt"

echo "========================================"
echo " Setup backend environment (uv)"
echo "========================================"

# Validations
if [ ! -f "$REQ" ]; then
  echo "ERROR: requirements.txt not found in $BACKEND_DIR" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 'uv' is not installed or not in PATH. Install it: https://docs.astral.sh/uv/" >&2
  exit 1
fi

# 1) Create venv if missing
echo "\n[1/3] Creating virtualenv (uv venv) if it doesn't exist..."
if [ -d "$VENV_DIR" ]; then
  echo "  -> Virtualenv exists at $VENV_DIR, skipping..."
else
  (cd "$BACKEND_DIR" && uv venv .venv --python 3.11)
  echo "  -> Virtualenv created at $VENV_DIR"
fi

# 2) Install deps
echo "\n[2/3] Installing dependencies (uv pip)..."
# Use uv pip to ensure we use the venv's pip
(cd "$BACKEND_DIR" && uv pip install -r requirements.txt -q)
echo "  -> Dependencies installed"

# 3) Create logs dir
echo "\n[3/3] Creating useful folders if missing..."
LOGS_DIR="$BACKEND_ROOT/logs"
if [ ! -d "$LOGS_DIR" ]; then
  mkdir -p "$LOGS_DIR"
  echo "  -> Created logs dir: $LOGS_DIR"
else
  echo "  -> Logs dir already exists: $LOGS_DIR"
fi

cat <<EOF

========================================
 Setup backend completed!
========================================
Next steps:
  1. Activate the venv: source $VENV_DIR/bin/activate
  2. Start the app: ./start-backend.sh (from this folder)
  3. Start the DB: ./start-db.sh (uses docker compose: backend_seil/docker/postgres)
EOF