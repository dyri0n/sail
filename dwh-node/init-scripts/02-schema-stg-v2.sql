-- =============================================================================
-- 02-SCHEMA-STG-V2.SQL - Estructura del Schema Staging (Versión Refactorizada)
-- =============================================================================
-- Tablas temporales donde se cargan los datos crudos antes de transformar.
-- Se truncan después de cada ETL exitoso.
--
-- CAMBIOS vs V1:
--   - Renombrado stg_capacitaciones_resumen -> stg_realizacion_capacitaciones
--   - Renombrado stg_capacitaciones_participantes -> stg_participacion_capacitaciones
--   - Renombrado stg_asistencia_diaria_geovictoria -> stg_asistencia_diaria
--   - Actualizado stg_rotacion_empleados con nuevas columnas del Excel
-- =============================================================================

-- Crear schema staging con propietario stg_admin
CREATE SCHEMA IF NOT EXISTS stg AUTHORIZATION stg_admin;

-- Permisos para que dwh_admin pueda LEER del staging (necesario para los ETL)
GRANT USAGE ON SCHEMA stg TO dwh_admin;

-- Cambiar al usuario stg_admin para crear las tablas
SET ROLE stg_admin;
SET search_path TO stg;

-- =============================================================================
-- TABLAS DE STAGING
-- =============================================================================

-- -----------------------------------------------------------------------------
-- ROTACIÓN DE EMPLEADOS (data_rotacion.xlsx -> Hoja1)
-- -----------------------------------------------------------------------------
-- Nota: Se usa SERIAL como PK porque un empleado puede tener múltiples registros
CREATE TABLE stg_rotacion_empleados (
    id_registro SERIAL PRIMARY KEY,
    
    -- Identificadores
    id_empleado INTEGER NOT NULL,
    nombre VARCHAR(255),
    
    -- Empresa
    id_empresa INTEGER,
    empresa VARCHAR(255),
    tipo_empleo VARCHAR(255),
    
    -- Período principal
    desde1 DATE,
    hasta1 DATE,
    
    -- Organización
    area VARCHAR(255),
    funcion VARCHAR(255),                  -- NUEVO: Denominación de función
    cargo VARCHAR(255),
    jornada VARCHAR(100),
    duracion VARCHAR(100),                 -- NUEVO: Duración del contrato
    ant_puesto DATE,
    ceco VARCHAR(255),
    
    -- Datos personales
    fecha_nacimiento DATE,
    edad INTEGER CHECK (edad > 0),
    pais_nacimiento VARCHAR(100),
    lugar_nacimiento VARCHAR(100),
    nacionalidad VARCHAR(100),
    estado_civil VARCHAR(50),
    nro_hijos INTEGER CHECK (nro_hijos >= 0),
    sexo VARCHAR(20),
    
    -- Período secundario
    desde2 DATE,
    hasta2 DATE,
    clase_fecha VARCHAR(100),
    fecha DATE,
    clase_prestamo VARCHAR(100),
    movilidad_geografica VARCHAR(100),
    experiencia_profesional TEXT,
    puesto_ocupado VARCHAR(255),           -- NUEVO
    carnet_conducir VARCHAR(50),           -- NUEVO: Carnet de conducir B
    
    -- Período terciario
    desde3 DATE,
    hasta3 DATE,
    
    -- Medidas
    clase_medida VARCHAR(255),
    motivo_medida VARCHAR(255),
    alta DATE,
    baja DATE,
    
    -- Otros
    encargado_superior VARCHAR(255),
    fecha_modificacion DATE,               -- NUEVO: Modif.el
    denominacion_final VARCHAR(255)        -- NUEVO: Última columna Denominación
);

COMMENT ON TABLE stg_rotacion_empleados IS 
    'Staging: Datos de rotación y maestro de empleados desde SAP (data_rotacion.xlsx -> Hoja1)';

-- -----------------------------------------------------------------------------
-- REALIZACIÓN DE CAPACITACIONES (data_capacitaciones.xlsx -> Informe 202X)
-- -----------------------------------------------------------------------------
-- Resumen de capacitaciones realizadas en el año
CREATE TABLE stg_realizacion_capacitaciones (
    id_registro SERIAL PRIMARY KEY,
    nro_capacitacion INTEGER,
    mes VARCHAR(20) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    lugar VARCHAR(100),                    -- Presencial, Online, Virtual
    fecha_inicio DATE,
    fecha_fin DATE,
    objetivo_area VARCHAR(255),
    externo_interno VARCHAR(50),           -- Externo, Interno o Externo/Interno
    tipo_curso VARCHAR(100),
    gerencia VARCHAR(100),
    formador_proveedor VARCHAR(255),
    nro_asistentes INTEGER CHECK (nro_asistentes >= 0),
    horas_ppersona INTEGER CHECK (horas_ppersona >= 0),
    total_horas INTEGER CHECK (total_horas >= 0),
    coste NUMERIC(12, 2) CHECK (coste >= 0),
    valoracion_formador NUMERIC(3, 1) CHECK (
        valoracion_formador >= 0 AND valoracion_formador <= 5
    ),
    indice_satisfaccion NUMERIC(5, 2) CHECK (
        indice_satisfaccion >= 0 AND indice_satisfaccion <= 100
    ),
    nps INTEGER CHECK (nps >= -100 AND nps <= 100)
);

COMMENT ON TABLE stg_realizacion_capacitaciones IS 
    'Staging: Resumen de capacitaciones realizadas (data_capacitaciones.xlsx -> Informe 202X)';

-- -----------------------------------------------------------------------------
-- PARTICIPACIÓN EN CAPACITACIONES (data_capacitaciones.xlsx -> Participantes)
-- -----------------------------------------------------------------------------
-- Detalle de asistentes a cada capacitación
CREATE TABLE stg_participacion_capacitaciones (
    id_registro SERIAL PRIMARY KEY,
    id_asistencia INTEGER,
    mes VARCHAR(20),
    rut VARCHAR(12) NOT NULL,
    id_empleado INTEGER,
    nombre VARCHAR(255),
    apellidos VARCHAR(255),
    correo VARCHAR(255),
    nombre_curso VARCHAR(255) NOT NULL,
    total_horas_formacion INTEGER CHECK (total_horas_formacion >= 0)
);

COMMENT ON TABLE stg_participacion_capacitaciones IS 
    'Staging: Participantes de capacitaciones (data_capacitaciones.xlsx -> Participantes)';

-- -----------------------------------------------------------------------------
-- ASISTENCIA DIARIA (data_asistencias.xlsx -> Días)
-- -----------------------------------------------------------------------------
-- Registros de asistencia importados de GeoVictoria
CREATE TABLE stg_asistencia_diaria (
    row_id SERIAL,
    
    -- Datos categóricos
    grupo VARCHAR(100),                    -- Origen: Grupo
    
    -- Identificadores y Fechas (PK)
    asistio_en DATE NOT NULL,              -- Origen: Fecha
    
    -- Permisos y turnos
    tipo_permiso VARCHAR(100),             -- Origen: Permiso
    tipo_turno VARCHAR(150),               -- Origen: Turno
    
    -- Marcas de tiempo
    hora_ingreso TIME,                     -- Origen: Entró
    atraso INTERVAL,                       -- Origen: Atraso
    hora_salida TIME,                      -- Origen: Salió
    adelanto INTERVAL,                     -- Origen: Adelanto
    total_horas INTERVAL,                  -- Origen: Horas Totales
    
    -- ID Empleado (última columna en Excel)
    id_empleado INTEGER NOT NULL,          -- Origen: Cargo
    
    -- Llave primaria compuesta (incluye turno para permitir múltiples turnos por día)
    CONSTRAINT pk_stg_asistencia_diaria PRIMARY KEY (asistio_en, id_empleado, tipo_turno)
);

COMMENT ON TABLE stg_asistencia_diaria IS 
    'Staging: Asistencia diaria de GeoVictoria (data_asistencias.xlsx -> Días)';
COMMENT ON COLUMN stg_asistencia_diaria.id_empleado IS 
    'Identificador numérico del empleado (campo Cargo en el Excel)';
COMMENT ON COLUMN stg_asistencia_diaria.atraso IS 
    'Duración del atraso. NULL o 00:00:00 si no hubo';

-- -----------------------------------------------------------------------------
-- PERFILES DE TRABAJO (DFT) - Sin cambios
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- PROCESO DE SELECCIÓN - Sin cambios
-- -----------------------------------------------------------------------------
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
    coste_proceso NUMERIC(12, 2) CHECK (coste_proceso >= 0)
);

COMMENT ON TABLE stg_proceso_seleccion IS 'Staging: Procesos de selección y reclutamiento.';

-- =============================================================================
-- PERMISOS
-- =============================================================================
RESET ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA stg TO dwh_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA stg GRANT SELECT ON TABLES TO dwh_admin;
