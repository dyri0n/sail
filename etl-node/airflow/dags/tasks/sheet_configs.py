"""
Configuraciones de hojas Excel para carga a Staging.

Define todas las hojas Excel que se cargan al schema staging,
con sus mapeos de columnas y tipos de datos.

Cada ExcelSheet representa una hoja individual de un archivo Excel
y su tabla destino en staging.
"""

from tasks.excel_loader import ColumnType, ExcelSheet, col, parse_fecha_asistencia

# =============================================================================
# CONSTANTES
# =============================================================================
# Nombres de archivos Excel en landing zone
ARCHIVO_CAPACITACIONES = "data_capacitaciones.xlsx"
ARCHIVO_ASISTENCIAS = "data_asistencias.xlsx"
ARCHIVO_ROTACION = "data_rotaciones.xlsx"

# =============================================================================
# HOJAS: CAPACITACIONES
# =============================================================================

# Hoja: Informe 202X (wildcard para el año) -> stg_realizacion_capacitaciones
# NOTA: Las primeras 4 filas son decorativas (título, etc.), el header real está en la fila 5
CAPACITACIONES_REALIZACION = ExcelSheet(
    archivo=ARCHIVO_CAPACITACIONES,
    hoja="Informe 202*",  # Wildcard: busca "Informe 2024", "Informe 2025", etc.
    tabla="stg.stg_realizacion_capacitaciones",
    skiprows=4,  # Saltar las primeras 4 filas decorativas
    header_row=0,  # Después de skiprows, la primera fila es el header
    columnas=[
        col("N°", "nro_capacitacion", ColumnType.INTEGER),
        col("Mes", "mes", ColumnType.STRING, required=True),
        col("Título capacitación", "titulo", ColumnType.STRING, required=True),
        col("Lugar de impartición", "lugar"),
        col("Fecha inicio", "fecha_inicio", ColumnType.DATE),
        col("Fecha fin", "fecha_fin", ColumnType.DATE),
        col("Objetivo / Area temática", "objetivo_area"),
        col("Externo / Interno", "externo_interno"),
        col("Tipo de curso", "tipo_curso"),
        col("Gerencia", "gerencia"),
        col("Formador / Proveedor", "formador_proveedor"),
        col("Asistentes", "nro_asistentes", ColumnType.INTEGER),
        col("Horas", "horas_ppersona", ColumnType.INTEGER),
        col("Horas totales", "total_horas", ColumnType.INTEGER),
        col("Coste total", "coste", ColumnType.NUMERIC),
        col("Valoracion del formador", "valoracion_formador", ColumnType.NUMERIC),
        col("Indice de satisfacciOn", "indice_satisfaccion", ColumnType.NUMERIC),
        col("NPS", "nps", ColumnType.INTEGER),
    ],
    drop_na_subset=["mes", "titulo"],  # Filtrar filas vacías (sin mes ni título)
)

# Hoja: Participantes -> stg_participacion_capacitaciones
CAPACITACIONES_PARTICIPANTES = ExcelSheet(
    archivo=ARCHIVO_CAPACITACIONES,
    hoja="Participantes",
    tabla="stg.stg_participacion_capacitaciones",
    columnas=[
        col("N°", "id_asistencia", ColumnType.INTEGER),
        col("MES", "mes"),
        col("Rut", "rut", ColumnType.STRING, required=True),
        col("NºEMPLEADO", "id_empleado", ColumnType.INTEGER),
        col("NOMBRE", "nombre"),
        col("APELLIDOS", "apellidos"),
        col("CORREO", "correo"),
        col("NOMBRE CURSO", "nombre_curso", ColumnType.STRING, required=True),
        col("TOTAL HRS FORMACION", "total_horas_formacion", ColumnType.INTEGER),
    ],
    drop_na_subset=["rut", "nombre_curso"],  # Filtrar filas vacías
)

# =============================================================================
# HOJAS: ASISTENCIAS (GeoVictoria)
# =============================================================================

# Hoja: Días -> stg_asistencia_diaria
# NOTA: El archivo tiene headers técnicos ocultos. La fila 0 visible tiene los nombres reales.
# Usamos header=None y renombramos las columnas por posición.
ASISTENCIA_DIARIA = ExcelSheet(
    archivo=ARCHIVO_ASISTENCIAS,
    hoja="Días",
    tabla="stg.stg_asistencia_diaria",
    header_row=0,  # Primera fila visible tiene: Grupo, Fecha, Permiso, Turno, Entró, Atraso, Salió, Adelanto, Horas Totales, Cargo
    columnas=[
        col("Grupo", "grupo"),
        col(
            "Fecha", "asistio_en", ColumnType.STRING, required=True
        ),  # Se parsea con transformación personalizada
        col("Permiso", "tipo_permiso"),
        col("Turno", "tipo_turno"),
        col("Entró", "hora_ingreso", ColumnType.TIME),
        col("Atraso", "atraso", ColumnType.INTERVAL),
        col("Salió", "hora_salida", ColumnType.TIME),
        col("Adelanto", "adelanto", ColumnType.INTERVAL),
        col("Horas Totales", "total_horas", ColumnType.INTERVAL),
        col("Cargo", "id_empleado", ColumnType.INTEGER, required=True),
    ],
    transformaciones={
        "asistio_en": parse_fecha_asistencia,  # Parsea "Lun 29-04-2024" -> date
    },
    drop_na_subset=["id_empleado", "asistio_en"],
)

# =============================================================================
# HOJAS: ROTACIÓN (SAP)
# =============================================================================

# Hoja: Hoja1 (por defecto) -> stg_rotacion_empleados
# Columnas reales del Excel (pandas agrega .1, .2 a columnas duplicadas)
ROTACION_EMPLEADOS = ExcelSheet(
    archivo=ARCHIVO_ROTACION,
    hoja="Hoja1",
    tabla="stg.stg_rotacion_empleados",
    header_row=0,
    columnas=[
        # Identificadores
        col("Nº pers.", "id_empleado", ColumnType.INTEGER, required=True),
        col("Número de personal", "nombre"),
        # Empresa
        col("Soc.", "id_empresa", ColumnType.INTEGER),
        col("Nombre de la empresa", "empresa"),
        col("Denom.área personal", "tipo_empleo"),
        # Período principal
        col("Desde", "desde1", ColumnType.DATE),
        col("Hasta", "hasta1", ColumnType.DATE),
        # Organización
        col("Denominación de unidad organiz", "area"),
        col("Denominación de función", "funcion"),
        col("Denominación de posiciones", "cargo"),
        col("Relación laboral", "jornada"),
        col("Duración", "duracion"),
        col("Ant_puesto", "ant_puesto", ColumnType.DATE),
        col("Denominación", "ceco"),
        # Datos personales
        col("Fe.nacim.", "fecha_nacimiento", ColumnType.DATE),
        col("Edad del empleado", "edad", ColumnType.INTEGER),
        col("País de nacimiento", "pais_nacimiento"),
        col("Lugar de nacimiento", "lugar_nacimiento"),
        col("Nacionalidad", "nacionalidad"),
        col("Clave para el estado civil", "estado_civil"),
        col("Nº de hijos", "nro_hijos", ColumnType.INTEGER),
        col("Texto sexo", "sexo"),
        # Período secundario (pandas agrega .1 a columnas duplicadas)
        col("Desde.1", "desde2", ColumnType.DATE),
        col("Hasta.1", "hasta2", ColumnType.DATE),
        col("Clase de fecha", "clase_fecha"),
        col("Fecha", "fecha", ColumnType.DATE),
        col("Clase de préstamo", "clase_prestamo"),
        col("Movilidad geográfica", "movilidad_geografica"),
        col("Experiencia Profesional", "experiencia_profesional"),
        col("Puesto ocupado", "puesto_ocupado"),
        col("Carnet de conducir B", "carnet_conducir"),
        # Período terciario
        col("Inicio", "desde3", ColumnType.DATE),
        col("Hasta.2", "hasta3", ColumnType.DATE),
        # Medidas
        col("Denominación de la clase de me", "clase_medida"),
        col("Denominación del motivo de med", "motivo_medida"),
        col("Alta", "alta", ColumnType.DATE),
        col("Baja", "baja", ColumnType.DATE),
        # Superior y otros
        col("Nombre del superior (GO)", "encargado_superior"),
        col("Modif.el", "fecha_modificacion", ColumnType.DATE),
        col("Denominación.1", "denominacion_final"),
    ],
    drop_na_subset=["id_empleado"],  # Filtrar filas sin ID de empleado
)

# =============================================================================
# HOJAS: SAP (Dotación Snapshot)
# =============================================================================
ARCHIVO_SAP = "data_sap.xlsx"

DOTACION_SAP = ExcelSheet(
    archivo=ARCHIVO_SAP,
    hoja="Sheet1", # Default name usually, or "Hoja1"
    tabla="stg.stg_dotacion_sap",
    header_row=0,
    columnas=[
        col("Nº pers.", "id_personal", ColumnType.INTEGER),
        col("RUT", "rut"),
        col("Número de personal", "numero_personal", ColumnType.INTEGER),
        col("Soc.", "id_sociedad"),
        col("Nombre de la empresa", "nombre_empresa"),
        col("Denom.área personal", "area_personal"),
        col("Desde", "desde_area", ColumnType.DATE),
        col("Hasta", "hasta_area", ColumnType.DATE),
        col("Denominación de unidad organiz", "unidad_organizativa"),
        col("Denominación de posiciones", "posicion"),
        col("Sueldo Base", "sueldo_base", ColumnType.INTEGER),
        
        col("Relación laboral", "relacion_laboral"),
        col("Ant_puesto", "ant_puesto", ColumnType.NUMERIC),
        col("Denominación", "denominacion"),
        col("Fe.nacim.", "fecha_nacimiento", ColumnType.DATE),
        col("Edad del empleado", "edad", ColumnType.INTEGER),
        col("País de nacimiento", "pais_nacimiento"),
        col("Lugar de nacimiento", "lugar_nacimiento"),
        col("Nacionalidad", "nacionalidad"),
        col("Clave para el estado civil", "estado_civil"),
        col("Nº de hijos", "nro_hijos", ColumnType.INTEGER),
        col("Texto sexo", "sexo"),

        col("Desde.1", "desde_1", ColumnType.DATE),
        col("Hasta.1", "hasta_1", ColumnType.DATE),
        col("Clase de fecha", "clase_fecha"),
        col("Fecha", "fecha", ColumnType.DATE),
        col("Clase de préstamo", "clase_prestamo"),
        col("Movilidad geográfica", "movilidad_geografica"),
        col("Experiencia Profesional", "experiencia_profesional", ColumnType.INTEGER),
        col("Inicio", "inicio", ColumnType.DATE),
        col("Hasta.2", "hasta_2", ColumnType.DATE),
        col("Denominación de la clase de me", "clase_medida"),
        col("Denominación del motivo de med", "motivo_medida"),
        col("Alta", "alta", ColumnType.DATE),
        col("Baja", "baja", ColumnType.DATE),
        col("Nombre del superior (GO)", "nombre_superior"),
    ]
)

# =============================================================================
# REGISTROS DE HOJAS POR ARCHIVO
# =============================================================================

# Todas las hojas agrupadas por archivo
HOJAS_POR_ARCHIVO: dict[str, list[ExcelSheet]] = {
    ARCHIVO_CAPACITACIONES: [
        CAPACITACIONES_REALIZACION,
        CAPACITACIONES_PARTICIPANTES,
    ],
    ARCHIVO_ASISTENCIAS: [
        ASISTENCIA_DIARIA,
    ],
    ARCHIVO_ROTACION: [
        ROTACION_EMPLEADOS,
    ],
    ARCHIVO_SAP: [
        DOTACION_SAP,
    ],
}

# Lista plana de todas las hojas
TODAS_LAS_HOJAS: list[ExcelSheet] = [
    CAPACITACIONES_REALIZACION,
    CAPACITACIONES_PARTICIPANTES,
    ASISTENCIA_DIARIA,
    ROTACION_EMPLEADOS,
    DOTACION_SAP,
]

# Diccionario para acceso rápido por ID (archivo[hoja])
HOJAS_POR_ID: dict[str, ExcelSheet] = {sheet.id: sheet for sheet in TODAS_LAS_HOJAS}


# =============================================================================
# FUNCIONES HELPER
# =============================================================================
def obtener_hoja(archivo: str, hoja: str) -> ExcelSheet | None:
    """Obtiene una configuración de hoja por archivo y nombre de hoja."""
    sheet_id = f"{archivo}[{hoja}]"
    return HOJAS_POR_ID.get(sheet_id)


def obtener_hojas_archivo(archivo: str) -> list[ExcelSheet]:
    """Obtiene todas las hojas configuradas para un archivo."""
    return HOJAS_POR_ARCHIVO.get(archivo, [])


def obtener_tablas_destino() -> list[str]:
    """Retorna lista de todas las tablas destino."""
    return [sheet.tabla for sheet in TODAS_LAS_HOJAS]
