#!/bin/bash
# =============================================================================
# Script de Setup para Desarrollo Local - Linux/Mac
# =============================================================================
# Ejecutar desde la carpeta airflow/
# bash scripts/setup-dev.sh
# =============================================================================

set -e

echo "========================================"
echo " Setup de Entorno de Desarrollo Local"
echo "========================================"

# Verificar que 'uv' esté instalado
if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: Necesitas instalar 'uv' antes de continuar."
    echo "Instálalo siguiendo: https://docs.astral.sh/uv/"
    exit 1
fi

# Verificar que estamos en la carpeta correcta
if [ ! -f "./docker-compose.yaml" ]; then
    echo "ERROR: Ejecuta este script desde la carpeta 'airflow/'"
    exit 1
fi

# 1. Crear entorno virtual
echo ""
echo "[1/4] Creando entorno virtual Python..."
if [ -d ".venv" ]; then
    echo "  -> Entorno virtual ya existe, saltando..."
else
    uv venv .venv --python 3.13
    echo "  -> Entorno virtual creado en .venv/ (uv venv)"
fi

# 2. Activar e instalar dependencias
echo ""
echo "[2/4] Instalando dependencias para desarrollo..."
source .venv/bin/activate
uv pip install -r requirements-dev.txt -q
echo "  -> Dependencias instaladas correctamente"

# 3. Copiar .env si no existe
echo ""
echo "[3/4] Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  -> Archivo .env creado desde .env.example"
    echo "  -> IMPORTANTE: Revisa y ajusta los valores en .env"
else
    echo "  -> Archivo .env ya existe"
fi

# 4. Crear carpeta de logs si no existe
echo ""
echo "[4/4] Creando estructura de carpetas..."
mkdir -p logs test_data
echo "  -> Carpetas creadas"

echo ""
echo "========================================"
echo " Setup Completado!"
echo "========================================"
echo ""
echo "Próximos pasos:"
echo "  1. Abre VS Code en esta carpeta"
echo "  2. Selecciona el intérprete Python: .venv/bin/python"
echo "  3. Los errores de lint deberían desaparecer"
echo ""
echo "Para levantar Airflow en modo testing:"
echo "  docker-compose --profile testing up -d"
echo ""
echo "Para ver la UI de Airflow:"
echo "  http://localhost:8080 (admin/admin)"
echo ""
