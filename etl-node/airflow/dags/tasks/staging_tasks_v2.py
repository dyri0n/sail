"""
Tasks para carga de Excel a Staging (DAG 00).

Versión refactorizada que utiliza el sistema de ExcelSheet
para parametrizar la carga de hojas individuales.
"""

from pathlib import Path

import pandas as pd
from airflow.exceptions import AirflowException
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk import task
from sqlalchemy import create_engine

from config.settings import Settings
from tasks.excel_loader import ExcelLoader, ExcelSheet
from tasks.sheet_configs import (
    ASISTENCIA_DIARIA,
    CAPACITACIONES_PARTICIPANTES,
    CAPACITACIONES_REALIZACION,
    ROTACION_EMPLEADOS,
    TODAS_LAS_HOJAS,
)

settings = Settings()
STG_CONN_ID = settings.STG_CONN_ID
LANDING_ZONE_PATH = Path("/landing-zone")

# SQL para truncar todas las tablas de staging antes de cargar
TRUNCATE_SQL = """
TRUNCATE TABLE stg.stg_rotacion_empleados CASCADE;
TRUNCATE TABLE stg.stg_realizacion_capacitaciones CASCADE;
TRUNCATE TABLE stg.stg_participacion_capacitaciones CASCADE;
TRUNCATE TABLE stg.stg_asistencia_diaria CASCADE;
"""


def create_staging_tasks(task_prefix: str = "stg"):
    """
    Crea y retorna todas las tasks de staging.

    Returns:
        dict con las tasks:
            - verificar: Valida formato de todos los archivos Excel
            - truncar: Trunca tablas de staging (SQLOperator)
            - cargar_capacitaciones_realizacion: Carga hoja Informe 202X
            - cargar_capacitaciones_participantes: Carga hoja Participantes
            - cargar_asistencia: Carga hoja Días
            - cargar_rotacion: Carga hoja Hoja1
            - resumen: Muestra resumen de carga
    """

    # Instancia del loader (reutilizable)
    loader = ExcelLoader(LANDING_ZONE_PATH)

    # =========================================================================
    # TASK: VERIFICAR FORMATO
    # =========================================================================
    @task(task_id=f"{task_prefix}_verificar_formato")
    def verificar_formato(**context) -> dict:
        """
        Valida que todos los archivos y hojas Excel existan
        y contengan las columnas requeridas.
        """
        validation_results = {}
        errors = []
        hojas_validadas = {}

        print(f"Buscando archivos en: {LANDING_ZONE_PATH}")
        try:
            contents = list(LANDING_ZONE_PATH.iterdir())
            print(f"Contenido: {[f.name for f in contents]}")
        except Exception as e:
            raise AirflowException(f"Error accediendo a {LANDING_ZONE_PATH}: {e}") from e

        # Validar cada hoja configurada
        for sheet in TODAS_LAS_HOJAS:
            print(f"\nValidando: {sheet.id}")
            result = loader.validar(sheet)
            validation_results[sheet.id] = result

            if not result["found"]:
                errors.append(f"Archivo no encontrado: '{sheet.archivo}'")
            elif not result["valid"]:
                error_msg = result.get("error", "Error desconocido")
                errors.append(f"{sheet.id}: {error_msg}")
            else:
                print(f"  ✓ Validación exitosa")
                hojas_validadas[sheet.id] = {
                    "path": result["path"],
                    "hoja_resuelta": result.get("hoja_resuelta", sheet.hoja),
                }

        if errors:
            raise AirflowException(
                "Errores de validación:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        return {
            "landing_zone": str(LANDING_ZONE_PATH),
            "hojas_validadas": hojas_validadas,
            "validation": validation_results,
        }

    # =========================================================================
    # TASK: TRUNCAR TABLAS
    # =========================================================================
    truncar = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_truncar_tablas",
        conn_id=STG_CONN_ID,
        sql=TRUNCATE_SQL,
    )

    # =========================================================================
    # FUNCIÓN GENÉRICA DE CARGA
    # =========================================================================
    def _cargar_hoja_a_db(sheet: ExcelSheet, info_validacion: dict) -> dict:
        """
        Función genérica para cargar una hoja Excel a su tabla destino.

        Args:
            sheet: Configuración de la hoja
            info_validacion: Resultado de verificar_formato para esta hoja

        Returns:
            Dict con tabla y cantidad de registros cargados
        """
        # Obtener nombre de hoja resuelta (por si era wildcard)
        hoja_info = info_validacion.get("hojas_validadas", {}).get(sheet.id, {})
        hoja_resuelta = hoja_info.get("hoja_resuelta")

        # Cargar y transformar datos
        df = loader.cargar(sheet, hoja_resuelta=hoja_resuelta)

        # Insertar en base de datos
        engine = create_engine(settings.get_stg_uri())
        df.to_sql(
            sheet.tabla_nombre,
            engine,
            schema=sheet.schema,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )

        print(f"✓ Cargados {len(df)} registros en {sheet.tabla}")
        return {"table": sheet.tabla, "records": len(df)}

    # =========================================================================
    # TASKS DE CARGA ESPECÍFICAS
    # =========================================================================
    @task(task_id=f"{task_prefix}_cargar_capacitaciones_realizacion")
    def cargar_capacitaciones_realizacion(file_info: dict, **context):
        """Carga hoja 'Informe 202X' -> stg_realizacion_capacitaciones"""
        return _cargar_hoja_a_db(CAPACITACIONES_REALIZACION, file_info)

    @task(task_id=f"{task_prefix}_cargar_capacitaciones_participantes")
    def cargar_capacitaciones_participantes(file_info: dict, **context):
        """Carga hoja 'Participantes' -> stg_participacion_capacitaciones"""
        return _cargar_hoja_a_db(CAPACITACIONES_PARTICIPANTES, file_info)

    @task(task_id=f"{task_prefix}_cargar_asistencia")
    def cargar_asistencia(file_info: dict, **context):
        """Carga hoja 'Días' -> stg_asistencia_diaria"""
        return _cargar_hoja_a_db(ASISTENCIA_DIARIA, file_info)

    @task(task_id=f"{task_prefix}_cargar_rotacion")
    def cargar_rotacion(file_info: dict, **context):
        """Carga hoja 'Hoja1' -> stg_rotacion_empleados"""
        return _cargar_hoja_a_db(ROTACION_EMPLEADOS, file_info)

    # =========================================================================
    # TASK: RESUMEN
    # =========================================================================
    @task(task_id=f"{task_prefix}_resumen")
    def resumen_carga(resultados: list[dict], **context):
        """Muestra resumen de todos los datos cargados."""
        print("\n" + "=" * 60)
        print("RESUMEN DE CARGA A STAGING")
        print("=" * 60)
        total_registros = 0
        for resultado in resultados:
            if resultado:
                print(f"  • {resultado['table']}: {resultado['records']} registros")
                total_registros += resultado["records"]
        print("-" * 60)
        print(f"  TOTAL: {total_registros} registros")
        print("=" * 60 + "\n")
        return {"total_registros": total_registros}

    # =========================================================================
    # RETORNAR DICT CON TODAS LAS TASKS
    # =========================================================================
    return {
        "verificar": verificar_formato,
        "truncar": truncar,
        "cargar_capacitaciones_realizacion": cargar_capacitaciones_realizacion,
        "cargar_capacitaciones_participantes": cargar_capacitaciones_participantes,
        "cargar_asistencia": cargar_asistencia,
        "cargar_rotacion": cargar_rotacion,
        "resumen": resumen_carga,
    }
