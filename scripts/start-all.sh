#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SCRIPT MAESTRO - LEVANTAR TODA LA INFRAESTRUCTURA
# =============================================================================
# Ejecutar desde la raíz del proyecto: ./scripts/start-all.sh
# =============================================================================

# -----------------------------------------------------------------------------
# CONFIGURACIÓN: Elige el modo de Staging
# -----------------------------------------------------------------------------
# Opciones: "STG-PROD" (sin datos) o "STG-TEST" (con datos de prueba)
STG_MODE="STG-TEST"
# STG_MODE="STG-PROD"

echo "========================================"
echo " Levantando Infraestructura Completa"
echo "========================================"
echo "Modo Staging: $STG_MODE"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# -----------------------------------------------------------------------------
# 1. DWH Node (Data Warehouse)
# -----------------------------------------------------------------------------
echo "[1/3] Levantando Data Warehouse (puerto 6000)..."
cd "$ROOT_DIR/dwh-node"
./scripts/compose-up.sh

# -----------------------------------------------------------------------------
# 2. STG Node (Staging Database)
# -----------------------------------------------------------------------------
echo ""
echo "[2/3] Levantando Staging Database..."
cd "$ROOT_DIR/stg-node"

if [ "$STG_MODE" = "STG-TEST" ]; then
    echo "  -> Modo: Testing con datos de prueba (puerto 6002)"
    ./scripts/compose-up-test.sh
else
    echo "  -> Modo: Producción sin datos (puerto 6001)"
    ./scripts/compose-up-prod.sh
fi

# -----------------------------------------------------------------------------
# 3. ETL Node (Airflow)
# -----------------------------------------------------------------------------
echo ""
echo "[3/3] Levantando Airflow (puerto 8080)..."
cd "$ROOT_DIR/etl-node/airflow"
./scripts/compose-up.sh

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
echo ""
echo "========================================"
echo " Infraestructura Levantada!"
echo "========================================"
cat <<EOF

Servicios disponibles:
  - Data Warehouse:  localhost:6000 (usuario: dwh_admin)
  - Staging $STG_MODE:  localhost:$([ "$STG_MODE" = "STG-TEST" ] && echo "6002" || echo "6001") (usuario: stg_admin)
  - Airflow UI:      http://localhost:8080 (admin/admin)

Próximos pasos:
  1. Verifica que .env esté configurado correctamente en etl-node/airflow/
  2. Espera ~60s para que Airflow inicialice completamente
  3. Accede a http://localhost:8080 para ver los DAGs

EOF

cd "$ROOT_DIR"
