-- =============================================================================
-- 02-SCHEMA-STG.SQL - Estructura del Schema Staging
-- =============================================================================
-- Tablas temporales donde se cargan los datos crudos antes de transformar.
-- Se truncan después de cada ETL exitoso.
-- =============================================================================

-- Crear schema staging con propietario stg_admin
CREATE SCHEMA stg AUTHORIZATION stg_admin;

-- Permisos para que dwh_admin pueda LEER del staging (necesario para los ETL)
GRANT USAGE ON SCHEMA stg TO dwh_admin;

-- Cambiar al usuario stg_admin para crear las tablas
SET ROLE stg_admin;
SET search_path TO stg;

-- =============================================================================
-- TABLAS DE STAGING
-- =============================================================================

-- Tabla de staging para la rotación de empleados
-- Nota: Se usa SERIAL como PK porque un empleado puede tener múltiples registros (historial de movimientos)
CREATE TABLE stg_rotacion_empleados (
    id_registro SERIAL PRIMARY KEY,
    id_empleado INTEGER NOT NULL,
    rut VARCHAR(12),
    nombre VARCHAR(255), 
    id_empresa INTEGER,
    empresa VARCHAR(255),
    tipo_empleo VARCHAR(255),
    desde1 DATE,
    hasta1 DATE,
    area VARCHAR(255),
    cargo VARCHAR(255),
    jornada VARCHAR(100),
    ant_puesto DATE,
    ceco VARCHAR(255),
    fecha_nacimiento DATE,
    edad INTEGER CHECK (edad > 0),
    pais_nacimiento VARCHAR(100),
    lugar_nacimiento VARCHAR(100),
    nacionalidad VARCHAR(100),
    estado_civil VARCHAR(50),
    nro_hijos INTEGER CHECK (nro_hijos >= 0),
    sexo VARCHAR(20),
    desde2 DATE,
    hasta2 DATE,
    clase_fecha VARCHAR(100),
    fecha DATE,
    clase_prestamo VARCHAR(100),
    movilidad_geografica VARCHAR(100),
    experiencia_profesional TEXT,
    desde3 DATE,
    hasta3 DATE,
    clase_medida VARCHAR(255),
    motivo_medida VARCHAR(255),
    alta DATE,
    baja DATE,
    encargado_superior VARCHAR(255)
);

COMMENT ON TABLE stg_rotacion_empleados IS 'Staging: Datos de rotación y maestro de empleados desde SAP.';

-- Resumen anual de capacitaciones
CREATE TABLE stg_capacitaciones_resumen (
    nro_capacitacion SERIAL PRIMARY KEY,
    mes VARCHAR(20) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    lugar VARCHAR(50), -- Presencial, Online, Virtual
    fecha_inicio DATE,
    fecha_fin DATE,
    objetivo_area VARCHAR(100),
    externo_interno VARCHAR(50), -- Externo, Interno o Externo/Interno
    tipo_curso VARCHAR(50), -- Similar a lugar
    gerencia VARCHAR(50),
    formador_proveedor VARCHAR(255),
    nro_asistentes INTEGER CHECK (nro_asistentes > 0),
    horas_ppersona INTEGER CHECK (horas_ppersona > 0),
    total_horas INTEGER,
    coste NUMERIC(10, 2) CHECK (coste >= 0),
    valoracion_formador NUMERIC(3, 1) CHECK (
        valoracion_formador >= 1
        AND valoracion_formador <= 5
    ),
    indice_satisfaccion NUMERIC(5, 2) CHECK (
        indice_satisfaccion >= 0
        AND indice_satisfaccion <= 100
    ),
    nps INTEGER CHECK (
        nps >= -100
        AND nps <= 100
    )
);

COMMENT ON TABLE stg_capacitaciones_resumen IS 'Staging: Resumen mensual de capacitaciones realizadas.';

-- Participantes de las capacitaciones
CREATE TABLE stg_capacitaciones_participantes (
    id_asistencia SERIAL PRIMARY KEY,
    mes VARCHAR(20),
    rut VARCHAR(12) NOT NULL,
    id_empleado INTEGER,
    nombre VARCHAR(255),
    apellidos VARCHAR(255),
    correo VARCHAR(255),
    nombre_curso VARCHAR(255) NOT NULL,
    total_horas_formacion INTEGER
);

COMMENT ON TABLE stg_capacitaciones_participantes IS 'Staging: Detalle de participantes por capacitación.';

-- Perfiles de Trabajo (DFT)
CREATE TABLE stg_perfiles_trabajo (
    id SERIAL PRIMARY KEY,
    puesto TEXT,
    categoria TEXT,
    nombre_empleado TEXT,
    fecha DATE,
    linea_ascendente TEXT,
    linea_descendente TEXT,
    principal_mision TEXT,
    responsabilidades TEXT,
    informa_y_reporta TEXT,
    tareas_semanales TEXT,
    tareas_mensuales TEXT,
    tareas_trimestrales TEXT,
    tareas_semestrales TEXT,
    tareas_anuales TEXT,
    otras_tareas TEXT,
    competencias TEXT,
    habilidades_generales TEXT,
    habilidades_cognitivos TEXT,
    habilidades_fisicos TEXT,
    habilidades_sensoriales TEXT,
    condiciones_trabajo TEXT,
    apartado_legal TEXT
);

COMMENT ON TABLE stg_perfiles_trabajo IS 'Staging: Descripciones de puestos de trabajo (DFT).';

-- Proceso de selección de personal
CREATE TABLE stg_proceso_seleccion (
    id_proceso INTEGER PRIMARY KEY,
    fecha_cierre DATE,
    cargo VARCHAR(255),
    ceco VARCHAR(255),
    detalle_puesto VARCHAR(255),
    detalle_situacion TEXT,
    gerencia VARCHAR(100),
    linea_negocio VARCHAR(100),
    grupo VARCHAR(10),
    motivo VARCHAR(255),
    detalles_motivo TEXT,
    duracion_dias INTEGER CHECK (duracion_dias >= 0),
    fuente_reclutamiento VARCHAR(255),
    nombre VARCHAR(255),
    sexo VARCHAR(20),
    edad INTEGER CHECK (edad > 0),
    formacion VARCHAR(255),
    agnos_experiencia INTEGER CHECK (agnos_experiencia >= 0),
    sector_procedencia VARCHAR(255),
    tiene_continuidad BOOLEAN,
    nro_cvs_recibidos INTEGER CHECK (nro_cvs_recibidos >= 0),
    nro_personas_entrevistadas_telefono INTEGER CHECK (nro_personas_entrevistadas_telefono >= 0),
    nro_personas_entrevistadas_presencial INTEGER CHECK (nro_personas_entrevistadas_presencial >= 0),
    nro_personas_finalistas INTEGER CHECK (nro_personas_finalistas >= 0),
    -- publicado_portal_interno BOOLEAN,
    -- fecha_envio_responsable DATE,
    -- fecha_entrevista_responsable DATE,
    -- duracion_entrevista_gerente NUMERIC(10, 2),
    -- detalle_fuente TEXT,
    -- observaciones TEXT,
    coste_proceso NUMERIC(12, 2) CHECK (coste_proceso >= 0)
    -- activo BOOLEAN,
    -- origen VARCHAR(100),
    -- total_ambiguo INTEGER
);

COMMENT ON TABLE stg_proceso_seleccion IS 'Staging: Procesos de selección y reclutamiento.';

CREATE TABLE stg_asistencia_diaria_geovictoria (
    -- Columna técnica para secuencia de carga (Solicitud: Serial)
    row_id SERIAL,

    -- Identificadores y Fechas (PK)
    id_empleado INTEGER NOT NULL,          -- Origen: Cargo (Numérico)
    asistio_en DATE NOT NULL,              -- Origen: Fecha (Día corto + DD-MM-YYYY)

    -- Datos Categóricos
    grupo VARCHAR(100),                    -- Origen: Grupo (Texto en mayúsculas)
    tipo_permiso VARCHAR(100),             -- Origen: Permiso (Texto)
    tipo_turno VARCHAR(150),               -- Origen: Turno (Texto descriptivo HH:MM - HH:MM)

    -- Marcas de Tiempo (Horas del día)
    hora_ingreso TIME,                     -- Origen: Entró (HH:MM)
    hora_salida TIME,                      -- Origen: Salió (HH:MM)

    -- Duraciones (Cálculos de tiempo)
    atraso INTERVAL,                       -- Origen: Atraso (H:MM)
    adelanto INTERVAL,                     -- Origen: Adelanto (H:MM)
    total_horas INTERVAL,                  -- Origen: Horas Totales (H:MM)

    -- Definición de la llave primaria compuesta
    CONSTRAINT pk_stg_asistencia PRIMARY KEY (asistio_en, id_empleado)
);

-- Comentarios en las columnas para documentación (Opcional pero recomendado)
COMMENT ON TABLE stg_asistencia_diaria_geovictoria IS 'Tabla de staging para asistencia diaria importada de GeoVictoria';
COMMENT ON COLUMN stg_asistencia_diaria_geovictoria.id_empleado IS 'Identificador numérico del empleado (Legajo/ID)';
COMMENT ON COLUMN stg_asistencia_diaria_geovictoria.atraso IS 'Duración del atraso. 00:00 si no hubo';

-- Permisos de lectura para dwh_admin sobre todas las tablas de staging
RESET ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA stg TO dwh_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA stg GRANT SELECT ON TABLES TO dwh_admin;
