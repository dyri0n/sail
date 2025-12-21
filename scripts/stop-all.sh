#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SCRIPT MAESTRO - DETENER TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: ./scripts/stop-all.sh
# =============================================================================

echo "========================================"
echo " Deteniendo Infraestructura Completa"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# -----------------------------------------------------------------------------
# 1. Airflow (detener primero para liberar conexiones)
# -----------------------------------------------------------------------------
echo "[1/2] Deteniendo Airflow..."
cd "$ROOT_DIR/etl-node/airflow"
./scripts/compose-down.sh

# -----------------------------------------------------------------------------
# 2. Data Warehouse
# -----------------------------------------------------------------------------
echo ""
echo "[2/2] Deteniendo Data Warehouse..."
cd "$ROOT_DIR/dwh-node"
./scripts/compose-down.sh

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
echo ""
echo "========================================"
echo " Infraestructura Detenida!"
echo "========================================"
echo ""

cd "$ROOT_DIR"
