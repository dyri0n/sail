"""
Tasks para carga de Excel a Staging (DAG 00).
"""

from pathlib import Path
from typing import Any

import pandas as pd
from airflow.exceptions import AirflowException
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sdk import task
from sqlalchemy import create_engine

from config.settings import Settings

settings = Settings()
STG_CONN_ID = settings.STG_CONN_ID
LANDING_ZONE_PATH = Path("/landing-zone")

EXCEL_FILES_MAPPING = {
    "data_sap.xlsx": {
        "table": "stg.stg_rotacion_empleados",
        "columns": {
            "Nº pers.": "id_empleado",
            "RUT": "rut",
            "Número de personal": "nombre",
            "Soc.": "id_empresa",
            "Nombre de la empresa": "empresa",
            "Denom.área personal": "tipo_empleo",
            "Desde": "desde1",
            "Hasta": "hasta1",
            "Denominación de unidad organiz": "area",
            "Denominación de posiciones": "cargo",
            "Relación laboral": "jornada",
            "Ant_puesto": "ant_puesto",
            "Denominación": "ceco",
            "Fe.nacim.": "fecha_nacimiento",
            "Edad del empleado": "edad",
            "País de nacimiento": "pais_nacimiento",
            "Lugar de nacimiento": "lugar_nacimiento",
            "Nacionalidad": "nacionalidad",
            "Clave para el estado civil": "estado_civil",
            "Nº de hijos": "nro_hijos",
            "Texto sexo": "sexo",
            "Desde.1": "desde2",
            "Hasta.1": "hasta2",
            "Clase de fecha": "clase_fecha",
            "Fecha": "fecha",
            "Clase de préstamo": "clase_prestamo",
            "Movilidad geográfica": "movilidad_geografica",
            "Experiencia Profesional": "experiencia_profesional",
            "Inicio": "desde3",
            "Hasta.2": "hasta3",
            "Denominación de la clase de me": "clase_medida",
            "Denominación del motivo de med": "motivo_medida",
            "Alta": "alta",
            "Baja": "baja",
            "Nombre del superior (GO)": "encargado_superior",
        },
        "date_columns": [
            "desde1",
            "hasta1",
            "ant_puesto",
            "fecha_nacimiento",
            "desde2",
            "hasta2",
            "fecha",
            "desde3",
            "hasta3",
            "alta",
            "baja",
        ],
        "required_columns": ["Nº pers.", "RUT"],
    },
    "data_capacitaciones.xlsx": {
        "table": "stg.stg_capacitaciones_resumen",
        "columns": {
            "Nº": "nro_capacitacion",
            "Mes": "mes",
            "Título capacitación": "titulo",
            "Lugar de impartición": "lugar",
            "Fecha inicio": "fecha_inicio",
            "Fecha fin": "fecha_fin",
            "Objetivo / Area temática": "objetivo_area",
            "Externo / Interno": "externo_interno",
            "Tipo de curso": "tipo_curso",
            "Gerencia": "gerencia",
            "Formador / Proveedor": "formador_proveedor",
            "Asistentes": "nro_asistentes",
            "Horas": "horas_ppersona",
            "Horas totales": "total_horas",
            "Coste total": "coste",
            "Valoración del formador": "valoracion_formador",
            "Índice de satisfacción": "indice_satisfaccion",
            "NPS": "nps",
        },
        "date_columns": ["fecha_inicio", "fecha_fin"],
        "required_columns": ["Mes", "Título capacitación"],
    },
    "data_asistencia_capacitaciones.xlsx": {
        "table": "stg.stg_capacitaciones_participantes",
        "columns": {
            "Nº": "id_asistencia",
            "MES": "mes",
            "Rut": "rut",
            "NºEMPLEADO": "id_empleado",
            "NOMBRE": "nombre",
            "APELLIDOS": "apellidos",
            "CORREO": "correo",
            "NOMBRE CURSO": "nombre_curso",
            "TOTAL HRS FORMACION": "total_horas_formacion",
        },
        "date_columns": [],
        "required_columns": ["Rut", "NOMBRE CURSO"],
    },
    "data_gestion_asistencia.xlsx": {
        "table": "stg.stg_asistencia_diaria_geovictoria",
        "columns": {
            "Cargo": "id_empleado",
            "Fecha": "asistio_en",
            "Grupo": "grupo",
            "Permiso": "tipo_permiso",
            "Turno": "tipo_turno",
            "Entró": "hora_ingreso",
            "Salió": "hora_salida",
            "Atraso": "atraso",
            "Adelanto": "adelanto",
            "Horas Totales": "total_horas",
        },
        "date_columns": ["asistio_en"],
        "time_columns": ["hora_ingreso", "hora_salida"],
        "interval_columns": ["atraso", "adelanto", "total_horas"],
        "required_columns": ["Cargo", "Fecha"],
    },
}

TRUNCATE_SQL = """
TRUNCATE TABLE stg.stg_rotacion_empleados CASCADE;
TRUNCATE TABLE stg.stg_capacitaciones_resumen CASCADE;
TRUNCATE TABLE stg.stg_capacitaciones_participantes CASCADE;
TRUNCATE TABLE stg.stg_asistencia_diaria_geovictoria CASCADE;
"""


def parse_time_to_interval(value: Any) -> str | None:
    if pd.isna(value) or value in ("", None):
        return None
    value_str = str(value).strip()
    if not value_str or value_str == "0:00":
        return "00:00:00"
    parts = value_str.split(":")
    if len(parts) == 2:
        hours, minutes = parts
        return f"{int(hours):02d}:{int(minutes):02d}:00"
    return value_str


def parse_time_column(value: Any) -> str | None:
    if pd.isna(value) or value in ("", None):
        return None
    value_str = str(value).strip()
    if not value_str:
        return None
    from datetime import datetime

    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")
    parts = value_str.split(":")
    if len(parts) >= 2:
        hours, minutes = parts[0], parts[1]
        return f"{int(hours):02d}:{int(minutes):02d}:00"
    return None


def create_staging_tasks(task_prefix: str = "stg"):
    """
    Crea y retorna todas las tasks de staging.

    Returns:
        dict con: verificar, truncar, cargar_sap, cargar_capacitaciones,
                  cargar_asistencia_cap, cargar_asistencia, resumen
    """

    @task(task_id=f"{task_prefix}_verificar_formato")
    def verificar_formato(**context) -> dict:
        validation_results = {}
        errors = []
        files_found = {}

        print(f"Buscando archivos en: {LANDING_ZONE_PATH}")
        try:
            contents = list(LANDING_ZONE_PATH.iterdir())
            print(f"Contenido: {[f.name for f in contents]}")
        except Exception as e:
            raise AirflowException(f"Error accediendo a {LANDING_ZONE_PATH}: {e}") from e

        for filename, config in EXCEL_FILES_MAPPING.items():
            file_path = LANDING_ZONE_PATH / filename
            if not file_path.exists():
                errors.append(f"Archivo no encontrado: '{filename}'")
                validation_results[filename] = {"found": False}
                continue
            print(f"✓ Archivo encontrado: {filename}")
            try:
                df_sample = pd.read_excel(file_path, nrows=1)
                actual_columns = set(df_sample.columns)
                required_columns = set(config["required_columns"])
                missing_cols = required_columns - actual_columns
                if missing_cols:
                    errors.append(f"Archivo '{filename}' - Columnas faltantes: {missing_cols}")
                    validation_results[filename] = {
                        "found": True,
                        "valid": False,
                        "missing_columns": list(missing_cols),
                    }
                else:
                    validation_results[filename] = {
                        "found": True,
                        "valid": True,
                        "columns": list(actual_columns),
                    }
                    files_found[filename] = str(file_path)
                    print(f"  ✓ Columnas validadas")
            except Exception as e:
                errors.append(f"Error leyendo '{filename}': {e}")
                validation_results[filename] = {"found": True, "valid": False, "error": str(e)}

        if errors:
            raise AirflowException("Errores:\n" + "\n".join(f"  - {e}" for e in errors))
        return {
            "landing_zone": str(LANDING_ZONE_PATH),
            "files": files_found,
            "validation": validation_results,
        }

    truncar = SQLExecuteQueryOperator(
        task_id=f"{task_prefix}_truncar_tablas",
        conn_id=STG_CONN_ID,
        sql=TRUNCATE_SQL,
    )

    @task(task_id=f"{task_prefix}_cargar_sap")
    def cargar_data_sap(file_info: dict, **context):
        filename = "data_sap.xlsx"
        config = EXCEL_FILES_MAPPING[filename]
        df = pd.read_excel(LANDING_ZONE_PATH / filename)
        print(f"Leyendo '{filename}': {len(df)} registros")
        df = df.rename(columns=config["columns"])
        valid_cols = [c for c in config["columns"].values() if c in df.columns]
        df = df[valid_cols]
        for col in config["date_columns"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        if "edad" in df.columns:
            df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
        if "nro_hijos" in df.columns:
            df["nro_hijos"] = pd.to_numeric(df["nro_hijos"], errors="coerce").fillna(0).astype(int)
        engine = create_engine(settings.get_stg_uri())
        df.to_sql(
            "stg_rotacion_empleados",
            engine,
            schema="stg",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )
        print(f"✓ Cargados {len(df)} registros en stg.stg_rotacion_empleados")
        return {"table": config["table"], "records": len(df)}

    @task(task_id=f"{task_prefix}_cargar_capacitaciones")
    def cargar_data_capacitaciones(file_info: dict, **context):
        filename = "data_capacitaciones.xlsx"
        config = EXCEL_FILES_MAPPING[filename]
        df = pd.read_excel(LANDING_ZONE_PATH / filename)
        print(f"Leyendo '{filename}': {len(df)} registros")
        df = df.rename(columns=config["columns"])
        valid_cols = [c for c in config["columns"].values() if c in df.columns]
        df = df[valid_cols]
        for col in config["date_columns"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        numeric_cols = [
            "nro_asistentes",
            "horas_ppersona",
            "total_horas",
            "coste",
            "valoracion_formador",
            "indice_satisfaccion",
            "nps",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        engine = create_engine(settings.get_stg_uri())
        df.to_sql(
            "stg_capacitaciones_resumen",
            engine,
            schema="stg",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )
        print(f"✓ Cargados {len(df)} registros en stg.stg_capacitaciones_resumen")
        return {"table": config["table"], "records": len(df)}

    @task(task_id=f"{task_prefix}_cargar_asistencia_cap")
    def cargar_data_asistencia_capacitaciones(file_info: dict, **context):
        filename = "data_asistencia_capacitaciones.xlsx"
        config = EXCEL_FILES_MAPPING[filename]
        df = pd.read_excel(LANDING_ZONE_PATH / filename)
        print(f"Leyendo '{filename}': {len(df)} registros")
        df = df.rename(columns=config["columns"])
        valid_cols = [c for c in config["columns"].values() if c in df.columns]
        df = df[valid_cols]
        if "total_horas_formacion" in df.columns:
            df["total_horas_formacion"] = pd.to_numeric(
                df["total_horas_formacion"], errors="coerce"
            )
        if "id_empleado" in df.columns:
            df["id_empleado"] = pd.to_numeric(df["id_empleado"], errors="coerce")
        engine = create_engine(settings.get_stg_uri())
        df.to_sql(
            "stg_capacitaciones_participantes",
            engine,
            schema="stg",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )
        print(f"✓ Cargados {len(df)} registros en stg.stg_capacitaciones_participantes")
        return {"table": config["table"], "records": len(df)}

    @task(task_id=f"{task_prefix}_cargar_asistencia")
    def cargar_data_gestion_asistencia(file_info: dict, **context):
        filename = "data_gestion_asistencia.xlsx"
        config = EXCEL_FILES_MAPPING[filename]
        df = pd.read_excel(LANDING_ZONE_PATH / filename)
        print(f"Leyendo '{filename}': {len(df)} registros")
        df = df.rename(columns=config["columns"])
        valid_cols = [c for c in config["columns"].values() if c in df.columns]
        df = df[valid_cols]
        if "asistio_en" in df.columns:
            df["asistio_en"] = pd.to_datetime(df["asistio_en"], errors="coerce").dt.date
        for col in config.get("time_columns", []):
            if col in df.columns:
                df[col] = df[col].apply(parse_time_column)
        for col in config.get("interval_columns", []):
            if col in df.columns:
                df[col] = df[col].apply(parse_time_to_interval)
        if "id_empleado" in df.columns:
            df["id_empleado"] = pd.to_numeric(df["id_empleado"], errors="coerce")
        df = df.dropna(subset=["id_empleado", "asistio_en"])
        engine = create_engine(settings.get_stg_uri())
        df.to_sql(
            "stg_asistencia_diaria_geovictoria",
            engine,
            schema="stg",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )
        print(f"✓ Cargados {len(df)} registros en stg.stg_asistencia_diaria_geovictoria")
        return {"table": config["table"], "records": len(df)}

    @task(task_id=f"{task_prefix}_resumen")
    def resumen_carga(resultados: list[dict], **context):
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
        
        # Hacer push explícito del conteo con un key específico
        context['task_instance'].xcom_push(key='row_count', value=total_registros)
        
        return total_registros  # Esto también se guarda como 'return_value'
    return {
        "verificar": verificar_formato,
        "truncar": truncar,
        "cargar_sap": cargar_data_sap,
        "cargar_capacitaciones": cargar_data_capacitaciones,
        "cargar_asistencia_cap": cargar_data_asistencia_capacitaciones,
        "cargar_asistencia": cargar_data_gestion_asistencia,
        "resumen": resumen_carga,
    }
