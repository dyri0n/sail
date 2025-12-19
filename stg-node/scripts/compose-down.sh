#!/usr/bin/env bash
set -euo pipefail

# Uso: ./scripts/compose-down.sh [--prod|--test|--all]
# Baja contenedores staging

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker no está en PATH" >&2
  exit 1
fi

case "${1:-all}" in
  --prod)
    docker compose --profile prod down
    ;;
  --test)
    docker compose --profile testing down
    ;;
  --all|*)
    docker compose --profile prod --profile testing down
    ;;
esac
