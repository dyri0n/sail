#!/usr/bin/env bash
# Stop postgres DB stack
# Usage: ./stop-db.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker/postgres/docker-compose.yml"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found in PATH" >&2
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "docker compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

echo "Stopping Postgres stack with: docker compose -f $COMPOSE_FILE down"
docker compose -f "$COMPOSE_FILE" down -v

echo "Postgres stack stopped."
