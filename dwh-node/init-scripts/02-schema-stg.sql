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
CREATE TABLE stg_rotacion_empleados (
    id_personal INTEGER PRIMARY KEY,
    numero_personal_texto VARCHAR(100),
    id_sociedad INTEGER,
    nombre_completo VARCHAR(255),
    nombre_empresa VARCHAR(255),
    area_personal VARCHAR(255),
    fecha_desde_area_personal DATE,
    fecha_hasta_area_personal DATE,
    unidad_organizativa VARCHAR(255),
    posicion VARCHAR(255),
    relacion_laboral VARCHAR(100),
    fecha_antiguedad_puesto DATE,
    denominacion_cargo_duplicada VARCHAR(255),
    fecha_nacimiento DATE,
    edad INTEGER CHECK (edad > 0),
    pais_nacimiento VARCHAR(100),
    lugar_nacimiento VARCHAR(100),
    nacionalidad VARCHAR(100),
    estado_civil VARCHAR(50),
    numero_hijos INTEGER CHECK (numero_hijos >= 0),
    sexo VARCHAR(20),
    fecha_desde_cargo DATE,
    fecha_hasta_cargo DATE,
    clase_fecha VARCHAR(100),
    fecha_generica DATE,
    clase_prestamo VARCHAR(100),
    movilidad_geografica VARCHAR(100),
    experiencia_profesional TEXT,
    fecha_inicio_exp DATE,
    modificacion_exp VARCHAR(100),
    fecha_hasta_exp DATE,
    denominacion_clase_me VARCHAR(255),
    denominacion_motivo_med VARCHAR(255),
    fecha_alta DATE,
    fecha_baja DATE,
    nombre_superior VARCHAR(255)
);

COMMENT ON TABLE stg_rotacion_empleados IS 'Staging: Datos de rotación y maestro de empleados desde SAP.';

-- Resumen anual de capacitaciones
CREATE TABLE stg_capacitaciones_resumen (
    id_capacitacion SERIAL PRIMARY KEY,
    mes VARCHAR(20) NOT NULL,
    titulo_capacitacion VARCHAR(255) NOT NULL,
    modalidad VARCHAR(100),
    fecha_inicio DATE,
    fecha_fin DATE,
    area_tematica VARCHAR(100),
    tipo_formador VARCHAR(100),
    gerencia VARCHAR(50),
    formador_proveedor VARCHAR(255),
    asistentes INTEGER CHECK (asistentes > 0),
    horas INTEGER CHECK (horas > 0),
    horas_totales INTEGER,
    coste_total_euros NUMERIC(10, 2) CHECK (coste_total_euros >= 0),
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
    id_control_interno INTEGER PRIMARY KEY,
    fecha_cierre_proceso DATE,
    situacion TEXT,
    motivo VARCHAR(255),
    detalle_motivo TEXT,
    publicado_portal_interno BOOLEAN,
    fecha_envio_responsable DATE,
    fecha_entrevista_responsable DATE,
    duracion_entrevista_gerente NUMERIC(10, 2),
    duracion_dias_total INTEGER CHECK (duracion_dias_total >= 0),
    fuente_reclutamiento VARCHAR(255),
    detalle_fuente TEXT,
    observaciones TEXT,
    coste_proceso NUMERIC(12, 2) CHECK (coste_proceso >= 0),
    n_cv_recibidos INTEGER CHECK (n_cv_recibidos >= 0),
    n_personas_entrevistadas_telefono INTEGER CHECK (n_personas_entrevistadas_telefono >= 0),
    n_personas_entrevistadas_presencial INTEGER CHECK (n_personas_entrevistadas_presencial >= 0),
    n_personas_finalistas INTEGER CHECK (n_personas_finalistas >= 0),
    puesto VARCHAR(255),
    centro_area VARCHAR(255),
    detalle_puesto VARCHAR(255),
    gerencia VARCHAR(100),
    linea_negocio VARCHAR(100),
    grupo VARCHAR(10),
    persona VARCHAR(255),
    sexo VARCHAR(20),
    edad INTEGER CHECK (edad > 0),
    formacion VARCHAR(255),
    anos_experiencia INTEGER CHECK (anos_experiencia >= 0),
    sector_procedencia VARCHAR(255),
    activo BOOLEAN,
    continuidad_mas_4_meses BOOLEAN,
    origen VARCHAR(100),
    total_ambiguo INTEGER
);

COMMENT ON TABLE stg_proceso_seleccion IS 'Staging: Procesos de selección y reclutamiento.';

-- Permisos de lectura para dwh_admin sobre todas las tablas de staging
RESET ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA stg TO dwh_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA stg GRANT SELECT ON TABLES TO dwh_admin;
