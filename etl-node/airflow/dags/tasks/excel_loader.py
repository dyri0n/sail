"""
Módulo para carga y validación de hojas Excel.

Provee tipos y funciones para trabajar con hojas de Excel de forma
parametrizada y reutilizable. El grano mínimo es una hoja individual.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from airflow.exceptions import AirflowException


# =============================================================================
# ENUMS PARA TIPOS DE COLUMNA
# =============================================================================
class ColumnType(Enum):
    """Tipos de datos para columnas."""

    STRING = "string"
    INTEGER = "integer"
    NUMERIC = "numeric"
    DATE = "date"
    TIME = "time"
    INTERVAL = "interval"


# =============================================================================
# DATACLASS PARA DEFINICIÓN DE COLUMNA
# =============================================================================
@dataclass
class Column:
    """
    Define una columna del Excel y su mapeo a la base de datos.

    Attributes:
        excel_name: Nombre de la columna en el Excel (origen)
        db_name: Nombre de la columna en la BD (destino)
        col_type: Tipo de dato para transformación
        required: Si la columna es obligatoria para validación
    """

    excel_name: str
    db_name: str
    col_type: ColumnType = ColumnType.STRING
    required: bool = False

    def __post_init__(self):
        if not self.excel_name or not self.db_name:
            raise ValueError("excel_name y db_name son obligatorios")


# =============================================================================
# DATACLASS PARA DEFINICIÓN DE HOJA EXCEL
# =============================================================================
@dataclass
class ExcelSheet:
    """
    Define una hoja de Excel y su configuración de carga.

    Esta es la unidad mínima de trabajo. Cada hoja se mapea a una tabla
    de staging específica.

    Attributes:
        archivo: Nombre del archivo Excel (ej: "data_capacitaciones.xlsx")
        hoja: Nombre de la hoja o patrón wildcard (ej: "Informe 202*")
        tabla: Tabla destino en formato schema.tabla (ej: "stg.stg_capacitaciones")
        columnas: Lista ordenada de columnas (preserva el orden)
        transformaciones: Dict de funciones de transformación por columna DB
        drop_na_subset: Columnas DB que no pueden ser nulas (se eliminan filas)
    """

    archivo: str
    hoja: str
    tabla: str
    columnas: list[Column] = field(default_factory=list)
    header_row: int = 0  # Fila donde está el encabezado (0-indexed, después de skiprows)
    skiprows: int = 0  # Filas a saltar antes de leer (para archivos con decoración arriba)
    transformaciones: dict[str, Callable[[pd.Series], pd.Series]] = field(default_factory=dict)
    drop_na_subset: list[str] = field(default_factory=list)

    # Propiedades calculadas
    @property
    def schema(self) -> str:
        """Extrae el schema de la tabla (ej: 'stg' de 'stg.stg_tabla')."""
        return self.tabla.split(".")[0] if "." in self.tabla else "public"

    @property
    def tabla_nombre(self) -> str:
        """Extrae el nombre de la tabla sin schema."""
        return self.tabla.split(".")[-1]

    @property
    def columnas_excel(self) -> list[str]:
        """Lista de nombres de columnas del Excel (preserva orden)."""
        return [col.excel_name for col in self.columnas]

    @property
    def columnas_db(self) -> list[str]:
        """Lista de nombres de columnas de la BD (preserva orden)."""
        return [col.db_name for col in self.columnas]

    @property
    def columnas_requeridas(self) -> list[str]:
        """Lista de columnas Excel marcadas como requeridas."""
        return [col.excel_name for col in self.columnas if col.required]

    @property
    def mapeo_columnas(self) -> dict[str, str]:
        """Diccionario de mapeo Excel -> DB (preserva orden en Python 3.7+)."""
        return {col.excel_name: col.db_name for col in self.columnas}

    @property
    def columnas_fecha(self) -> list[str]:
        """Lista de columnas DB de tipo DATE."""
        return [col.db_name for col in self.columnas if col.col_type == ColumnType.DATE]

    @property
    def columnas_tiempo(self) -> list[str]:
        """Lista de columnas DB de tipo TIME."""
        return [col.db_name for col in self.columnas if col.col_type == ColumnType.TIME]

    @property
    def columnas_intervalo(self) -> list[str]:
        """Lista de columnas DB de tipo INTERVAL."""
        return [col.db_name for col in self.columnas if col.col_type == ColumnType.INTERVAL]

    @property
    def columnas_entero(self) -> list[str]:
        """Lista de columnas DB de tipo INTEGER."""
        return [col.db_name for col in self.columnas if col.col_type == ColumnType.INTEGER]

    @property
    def columnas_numerico(self) -> list[str]:
        """Lista de columnas DB de tipo NUMERIC."""
        return [col.db_name for col in self.columnas if col.col_type == ColumnType.NUMERIC]

    @property
    def id(self) -> str:
        """Identificador único de la hoja: archivo[hoja]."""
        return f"{self.archivo}[{self.hoja}]"

    def __str__(self) -> str:
        return f"ExcelSheet({self.archivo}[{self.hoja}] -> {self.tabla})"

    def __repr__(self) -> str:
        return self.__str__()


# =============================================================================
# FUNCIONES DE UTILIDAD PARA PARSEO
# =============================================================================
def parse_time_to_interval(value: Any) -> str | None:
    """Convierte valor de tiempo a formato INTERVAL de PostgreSQL."""
    if pd.isna(value) or value in ("", None):
        return None
    value_str = str(value).strip()
    # Manejar valores placeholder
    if not value_str or value_str in ("0:00", "--", "-", "---"):
        return "00:00:00"
    parts = value_str.split(":")
    if len(parts) == 2:
        hours, minutes = parts
        # Validar que sean dígitos antes de convertir
        if not hours.replace("-", "").isdigit() or not minutes.replace("-", "").isdigit():
            return "00:00:00"  # Valor no parseable, retornar 0
        return f"{int(hours):02d}:{int(minutes):02d}:00"
    return value_str


def parse_time_column(value: Any) -> str | None:
    """Convierte valor a formato TIME de PostgreSQL."""
    if pd.isna(value) or value in ("", None):
        return None
    value_str = str(value).strip()
    # Manejar valores placeholder como '--' o '-'
    if not value_str or value_str in ("--", "-", "---"):
        return None
    from datetime import datetime

    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")
    parts = value_str.split(":")
    if len(parts) >= 2:
        hours, minutes = parts[0], parts[1]
        # Validar que sean dígitos antes de convertir
        if not hours.isdigit() or not minutes.replace("-", "").isdigit():
            return None  # Valor no parseable como tiempo
        return f"{int(hours):02d}:{int(minutes):02d}:00"
    return None


def parse_fecha_asistencia(value: Any):
    """
    Parsea el formato especial de fecha de asistencia: "Lun 29-04-2024" o "Lun 29-04-2024 (F)".

    El formato es: DIA_SEMANA DD-MM-YYYY [MARCADOR]
    Donde:
    - DIA_SEMANA: Lun, Mar, Mié, Jue, Vie, Sáb, Dom
    - DD-MM-YYYY: Fecha en formato día-mes-año
    - MARCADOR: Opcional, como "(F)" para feriados

    Retorna: datetime.date o None si no se puede parsear
    """
    from datetime import datetime

    if pd.isna(value) or value in ("", None):
        return None

    value_str = str(value).strip()
    if not value_str:
        return None

    # Remover marcadores como "(F)" al final
    # El patrón extrae la fecha DD-MM-YYYY
    import re

    match = re.search(r"(\d{2}-\d{2}-\d{4})", value_str)
    if match:
        fecha_str = match.group(1)
        try:
            return datetime.strptime(fecha_str, "%d-%m-%Y").date()
        except ValueError:
            return None

    return None


# =============================================================================
# CLASE PRINCIPAL: EXCEL LOADER
# =============================================================================
class ExcelLoader:
    """
    Cargador de hojas Excel con validación y transformación.

    Uso:
        loader = ExcelLoader(landing_zone_path)
        df = loader.cargar(sheet_config)
        loader.validar(sheet_config)
    """

    def __init__(self, landing_zone: Path | str):
        self.landing_zone = Path(landing_zone)

    def _resolver_nombre_hoja(self, file_path: Path, patron_hoja: str) -> tuple[str, str]:
        """
        Resuelve el nombre real de la hoja si es un patrón wildcard.

        Args:
            file_path: Ruta al archivo Excel
            patron_hoja: Nombre exacto o patrón (ej: "Informe 202*")

        Returns:
            Tuple (nombre_hoja_encontrada, patron_usado)

        Raises:
            AirflowException: Si no se encuentra ninguna hoja que coincida
        """
        # Si no tiene wildcard, devolver tal cual
        if "*" not in patron_hoja and "?" not in patron_hoja:
            return patron_hoja, patron_hoja

        # Obtener lista de hojas del archivo
        xl = pd.ExcelFile(file_path)
        hojas_disponibles = xl.sheet_names

        # Buscar primera hoja que coincida con el patrón
        for hoja in hojas_disponibles:
            if fnmatch.fnmatch(hoja, patron_hoja):
                print(f"  → Patrón '{patron_hoja}' coincide con hoja '{hoja}'")
                return hoja, patron_hoja

        raise AirflowException(
            f"No se encontró ninguna hoja que coincida con el patrón '{patron_hoja}' "
            f"en '{file_path.name}'. Hojas disponibles: {hojas_disponibles}"
        )

    def validar(self, sheet: ExcelSheet) -> dict:
        """
        Valida que el archivo y hoja existan y contengan las columnas requeridas.

        Args:
            sheet: Configuración de la hoja a validar

        Returns:
            Dict con información de validación:
                - found: bool
                - valid: bool
                - hoja_resuelta: str (nombre real de la hoja)
                - missing_columns: list (si hay columnas faltantes)
                - columns: list (columnas encontradas)

        Raises:
            AirflowException: Si hay errores críticos de validación
        """
        file_path = self.landing_zone / sheet.archivo
        result = {"sheet_id": sheet.id, "found": False, "valid": False}

        # Verificar archivo
        if not file_path.exists():
            result["error"] = f"Archivo no encontrado: '{sheet.archivo}'"
            return result

        result["found"] = True
        result["path"] = str(file_path)

        try:
            # Resolver nombre de hoja (soporta wildcards)
            hoja_real, patron = self._resolver_nombre_hoja(file_path, sheet.hoja)
            result["hoja_resuelta"] = hoja_real
            result["patron_hoja"] = patron

            # Leer solo headers para validación (respetando skiprows y header_row)
            df_sample = pd.read_excel(
                file_path,
                sheet_name=hoja_real,
                skiprows=sheet.skiprows,
                header=sheet.header_row,
                nrows=0,
            )
            actual_columns = set(df_sample.columns)
            required_columns = set(sheet.columnas_requeridas)

            # Verificar columnas requeridas
            missing_cols = required_columns - actual_columns
            if missing_cols:
                result["valid"] = False
                result["missing_columns"] = list(missing_cols)
                result["error"] = f"Columnas faltantes: {missing_cols}"
            else:
                result["valid"] = True
                result["columns"] = list(actual_columns)

        except Exception as e:
            result["valid"] = False
            result["error"] = str(e)

        return result

    def cargar(
        self,
        sheet: ExcelSheet,
        hoja_resuelta: str | None = None,
    ) -> pd.DataFrame:
        """
        Carga y transforma una hoja Excel según su configuración.

        Args:
            sheet: Configuración de la hoja
            hoja_resuelta: Nombre real de la hoja (si ya fue resuelto)

        Returns:
            DataFrame con las columnas renombradas y transformadas
        """
        file_path = self.landing_zone / sheet.archivo

        # Resolver hoja si no se provee
        if hoja_resuelta is None:
            hoja_resuelta, _ = self._resolver_nombre_hoja(file_path, sheet.hoja)

        # Leer Excel (respetando skiprows y header_row)
        df = pd.read_excel(
            file_path,
            sheet_name=hoja_resuelta,
            skiprows=sheet.skiprows,
            header=sheet.header_row,
        )
        print(f"Leyendo '{sheet.archivo}[{hoja_resuelta}]': {len(df)} registros")

        # Renombrar columnas según mapeo
        df = df.rename(columns=sheet.mapeo_columnas)

        # Filtrar solo columnas válidas (las que existen en el mapeo)
        valid_cols = [c for c in sheet.columnas_db if c in df.columns]
        df = df[valid_cols]

        # Aplicar transformaciones por tipo de columna
        df = self._aplicar_transformaciones_tipo(df, sheet)

        # Aplicar transformaciones personalizadas
        for col_db, transform_fn in sheet.transformaciones.items():
            if col_db in df.columns:
                df[col_db] = df[col_db].apply(transform_fn)

        # Eliminar filas con nulos en columnas críticas
        if sheet.drop_na_subset:
            subset_existente = [c for c in sheet.drop_na_subset if c in df.columns]
            if subset_existente:
                # Reemplazar strings vacíos por NaN antes de dropna
                for col_name in subset_existente:
                    df[col_name] = df[col_name].replace(["", " ", "  "], pd.NA)
                filas_antes = len(df)
                df = df.dropna(subset=subset_existente)
                filas_despues = len(df)
                if filas_antes != filas_despues:
                    print(
                        f"  → Eliminadas {filas_antes - filas_despues} filas con valores nulos en {subset_existente}"
                    )

        return df

    def _aplicar_transformaciones_tipo(self, df: pd.DataFrame, sheet: ExcelSheet) -> pd.DataFrame:
        """Aplica transformaciones automáticas según el tipo de columna."""
        # Fechas
        for col in sheet.columnas_fecha:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

        # Tiempos
        for col in sheet.columnas_tiempo:
            if col in df.columns:
                df[col] = df[col].apply(parse_time_column)

        # Intervalos
        for col in sheet.columnas_intervalo:
            if col in df.columns:
                df[col] = df[col].apply(parse_time_to_interval)

        # Enteros
        for col in sheet.columnas_entero:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Numéricos (decimal)
        for col in sheet.columnas_numerico:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df


# =============================================================================
# FUNCIÓN HELPER PARA CREAR COLUMNAS RÁPIDAMENTE
# =============================================================================
def col(
    excel: str,
    db: str,
    tipo: ColumnType = ColumnType.STRING,
    required: bool = False,
) -> Column:
    """
    Helper para crear columnas de forma concisa.

    Uso:
        columnas = [
            col("Fecha inicio", "fecha_inicio", ColumnType.DATE, required=True),
            col("Nombre", "nombre"),
        ]
    """
    return Column(excel_name=excel, db_name=db, col_type=tipo, required=required)
