-- scripts/init_dwh.sql

-- 1. Configuración inicial (Ejecutado como 'postgres')
CREATE USER dwh_admin WITH PASSWORD 'sail-rrhh-p4';
CREATE SCHEMA dwh_rrhh AUTHORIZATION dwh_admin;

-- 2. Permisos básicos
GRANT ALL ON SCHEMA dwh_rrhh TO dwh_admin;

-- Cambiamos la "identidad" de la sesión actual.
-- Ahora todo lo que se cree abajo será propiedad nativa de dwh_admin.
SET ROLE dwh_admin;

-- Definimos el path (opcional si usas nombres completos, pero cómodo)
SET search_path TO dwh_rrhh;

-- =============================================================
-- 1. DIMENSIONES (Tablas Maestras)
-- =============================================================

CREATE TABLE dim_tiempo (
    tiempo_sk INTEGER PRIMARY KEY, -- Formato AAAAMMDD
    fecha DATE NOT NULL,
    anio SMALLINT,
    mes_nombre VARCHAR(20),
    mes_numero SMALLINT,
    trimestre VARCHAR(2),
    dia_semana VARCHAR(20),
    es_fin_de_semana BOOLEAN,
    es_feriado BOOLEAN,
    nombre_feriado VARCHAR(100),
    tipo_feriado VARCHAR(50), -- 'Civil' o 'Religioso'
    es_irrenunciable BOOLEAN DEFAULT FALSE,
    semana_anio SMALLINT
);
COMMENT ON TABLE dim_tiempo IS 'Dimensión estática para todas las facts.';
COMMENT ON COLUMN dim_tiempo.tiempo_sk IS 'Clave subrogada fecha (AAAAMMDD)';

CREATE TABLE dim_empleado (
    empleado_sk SERIAL PRIMARY KEY,
    empleado_id_nk VARCHAR(50), -- ID SAP
    rut VARCHAR(20),
    nombre_completo VARCHAR(255),
    sexo VARCHAR(20),

    fecha_nacimiento DATE,
    nacionalidad VARCHAR(50),
    estado_civil VARCHAR(50),
    formacion VARCHAR(100),

    estado_laboral_activo BOOLEAN DEFAULT TRUE,

    scd_fecha_inicio_vigencia DATE,
    scd_fecha_fin_vigencia DATE,
    scd_es_actual BOOLEAN
);
COMMENT ON COLUMN dim_empleado.empleado_sk IS 'SCD Tipo 2: Cambia si cambia cargo, ceco, etc.';
COMMENT ON COLUMN dim_empleado.estado_laboral_activo IS 'Indica si está trabajando ahora o no el empleado';
COMMENT ON COLUMN dim_empleado.empleado_id_nk IS 'ID SAP u Original del sistema fuente';

-- 1. Dimensión Cargo
-- Llave de Negocio: nombre_cargo
CREATE TABLE dim_cargo (
    cargo_sk SERIAL PRIMARY KEY,
    nombre_cargo VARCHAR(255) NOT NULL,
    familia_puesto VARCHAR(100),
    area_funcional VARCHAR(100),

    CONSTRAINT uk_dim_cargo_nombre UNIQUE (nombre_cargo)
);

-- 2. Dimensión Empresa
-- Llave de Negocio: codigo (Ej: '837', '841')
CREATE TABLE dim_empresa (
    empresa_sk SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),

    CONSTRAINT uk_dim_empresa_codigo UNIQUE (codigo)
);

-- 3. Dimensión Gerencia
-- Llave de Negocio: nombre_gerencia
CREATE TABLE dim_gerencia (
    gerencia_sk SERIAL PRIMARY KEY,
    nombre_gerencia VARCHAR(100) NOT NULL,

    CONSTRAINT uk_dim_gerencia_nombre UNIQUE (nombre_gerencia)
);

-- 4. Dimensión Centro Costo
-- Llave de Negocio: nombre_ceco (o codigo si tuvieras separado, aqui usamos nombre)
CREATE TABLE dim_centro_costo (
    ceco_sk SERIAL PRIMARY KEY,
    nombre_ceco VARCHAR(100) NOT NULL,

    CONSTRAINT uk_dim_ceco_nombre UNIQUE (nombre_ceco)
);

-- 5. Dimensión Modalidad Contrato
-- Llave de Negocio: COMPUESTA (tipo_vinculo + regimen)
-- Ejemplo: 'INDEFINIDO' + 'FULL-TIME' es distinto a 'INDEFINIDO' + 'PART-TIME'
CREATE TABLE dim_modalidad_contrato (
    modalidad_sk SERIAL PRIMARY KEY,
    tipo_vinculo_legal VARCHAR(50) NOT NULL,
    regimen_horario VARCHAR(50) NOT NULL,
    fte_estandar DECIMAL(5,2),
    horas_cap_mensual_estandar INTEGER,

    CONSTRAINT uk_dim_modalidad_combo UNIQUE (tipo_vinculo_legal, regimen_horario)
);
COMMENT ON TABLE dim_modalidad_contrato IS 'Junk Dimension que combina Tipo de Empleo y Jornada.';
COMMENT ON COLUMN dim_modalidad_contrato.tipo_vinculo_legal IS 'Ej: Empleado, Temporal, Jubilado';
COMMENT ON COLUMN dim_modalidad_contrato.regimen_horario IS 'Ej: Full-Time, Part-Time, Art 22';
COMMENT ON COLUMN dim_modalidad_contrato.fte_estandar IS '1.0 para Full, 0.5 para Part-Time';

CREATE TABLE dim_turno (
    turno_sk SERIAL PRIMARY KEY,
    nombre_turno VARCHAR(100),
    hora_inicio_teorica TIME,
    hora_fin_teorica TIME,
    descanso_min INTEGER,
    horas_jornada DECIMAL(5,2)
);

CREATE TABLE dim_permiso (
    permiso_sk SERIAL PRIMARY KEY,
    codigo_permiso_nk VARCHAR(50),
    descripcion VARCHAR(255),
    categoria_analitica VARCHAR(100)
);
COMMENT ON TABLE dim_permiso IS 'Clasifica el estado del empleado ese día (Vacaciones vs Fallas).';

CREATE TABLE dim_medida_aplicada (
    medida_sk SERIAL PRIMARY KEY,
    tipo_movimiento VARCHAR(50),
    razon_detallada VARCHAR(255),
    es_voluntario BOOLEAN
);
COMMENT ON COLUMN dim_medida_aplicada.tipo_movimiento IS 'Alta, Baja, Cambio Puesto';

CREATE TABLE dim_curso (
    curso_sk SERIAL PRIMARY KEY,
    nombre_curso VARCHAR(255),
    categoria_tematica VARCHAR(100),
    modalidad VARCHAR(50)
);

CREATE TABLE dim_proveedor (
    proveedor_sk SERIAL PRIMARY KEY,
    nombre_proveedor VARCHAR(255),
    tipo_proveedor VARCHAR(50)
);

CREATE TABLE dim_lugar_realizacion (
    lugar_sk SERIAL PRIMARY KEY,
    lugar VARCHAR(255),
    region VARCHAR(100),
    pais VARCHAR(100)
);

-- =============================================================
-- 2. FACTS (Tablas de Hechos)
-- =============================================================

-- ÁREA: SELECCIÓN
CREATE TABLE fact_seleccion (
    seleccion_id SERIAL PRIMARY KEY,
    -- Foreign Keys
    cargo_solicitado_sk INTEGER REFERENCES dim_cargo(cargo_sk),
    fecha_apertura_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    fecha_cierre_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    empleado_seleccionado_sk INTEGER REFERENCES dim_empleado(empleado_sk),
    gerencia_solicitante_sk INTEGER REFERENCES dim_gerencia(gerencia_sk),
    -- Degeneradas
    id_solicitud_nk VARCHAR(50),
    fuente_reclutamiento VARCHAR(100),
    recruiter_responsable VARCHAR(100),
    estado_final_proceso VARCHAR(50),
    -- Métricas
    duracion_proceso_dias INTEGER,
    costo_proceso DECIMAL(15,2),
    cantidad_candidatos INTEGER,
    cantidad_entrevistas INTEGER,
    -- Quality of Hire
    tiene_continuidad INTEGER,
    motivo_fallo_continuidad VARCHAR(255)
);
COMMENT ON TABLE fact_seleccion IS 'Snapshot Acumulativo. Una fila por vacante.';
COMMENT ON COLUMN fact_seleccion.tiene_continuidad IS '1 si superó 4 meses, 0 si se fue antes';

-- ÁREA: ASISTENCIA
CREATE TABLE fact_asistencia (
    asistencia_id SERIAL PRIMARY KEY,
    -- Foreign Keys
    fecha_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    permiso_sk INTEGER REFERENCES dim_permiso(permiso_sk),
    empleado_sk INTEGER REFERENCES dim_empleado(empleado_sk),
    turno_planificado_sk INTEGER REFERENCES dim_turno(turno_sk),
    -- Datos Reales
    hora_entrada_real TIMESTAMP,
    hora_salida_real TIMESTAMP,
    -- Métricas
    horas_trabajadas DECIMAL(10,2),
    minutos_atraso INTEGER,
    minutos_adelanto_salida INTEGER,
    tolerancia_aplicada_min INTEGER,
    -- Flags
    permiso_aplicado VARCHAR(100),
    es_atraso INTEGER,
    es_salida_anticipada INTEGER,
    es_ausencia INTEGER
);
COMMENT ON TABLE fact_asistencia IS 'Transaccional diaria. Análisis de puntualidad y ausentismo.';
COMMENT ON COLUMN fact_asistencia.es_atraso IS '1 si Minutos_Atraso > Tolerancia';

-- ÁREA: ROTACIÓN
CREATE TABLE fact_rotacion (
    rotacion_id SERIAL PRIMARY KEY,
    -- Foreign Keys
    modalidad_sk INTEGER REFERENCES dim_modalidad_contrato(modalidad_sk),
    empleado_sk INTEGER REFERENCES dim_empleado(empleado_sk),
    ceco_sk INTEGER REFERENCES dim_centro_costo(ceco_sk),
    medida_sk INTEGER REFERENCES dim_medida_aplicada(medida_sk),
    cargo_sk INTEGER REFERENCES dim_cargo(cargo_sk),
    empresa_sk INTEGER REFERENCES dim_empresa(empresa_sk),
    fecha_inicio_vigencia_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    fecha_fin_vigencia_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    -- Métricas
    sueldo_base_intervalo DECIMAL(15,2),
    variacion_headcount INTEGER
);
COMMENT ON TABLE fact_rotacion IS 'Tabla de intervalos. Historia de cambios contractuales.';
COMMENT ON COLUMN fact_rotacion.variacion_headcount IS '+1 (Alta), -1 (Baja), 0 (Cambio)';

-- ÁREA: DOTACIÓN (SNAPSHOT)
CREATE TABLE fact_dotacion_snapshot (
    -- Esta tabla suele tener un volumen alto, se puede usar particionamiento por mes
    -- Foreign Keys
    modalidad_sk INTEGER REFERENCES dim_modalidad_contrato(modalidad_sk),
    empresa_sk INTEGER REFERENCES dim_empresa(empresa_sk),
    cargo_sk INTEGER REFERENCES dim_cargo(cargo_sk),
    empleado_sk INTEGER REFERENCES dim_empleado(empleado_sk),
    mes_cierre_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    -- Métricas
    headcount INTEGER DEFAULT 1,
    fte_real DECIMAL(5,2),
    horas_capacidad_mensual INTEGER,
    sueldo_base_mensual DECIMAL(15,2),
    antiguedad_meses INTEGER,
    -- Clave Primaria Compuesta (opcional pero recomendada para snapshots)
    PRIMARY KEY (mes_cierre_sk, empleado_sk)
);
COMMENT ON TABLE fact_dotacion_snapshot IS 'Snapshot Periódico Mensual. Foto fija.';

-- ÁREA: CAPACITACIÓN (OFERTA)
CREATE TABLE fact_realizacion_capacitacion (
    realizacion_id SERIAL PRIMARY KEY,
    -- Foreign Keys
    fecha_inicio_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    fecha_fin_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    gerencia_organizadora_sk INTEGER REFERENCES dim_gerencia(gerencia_sk),
    curso_sk INTEGER REFERENCES dim_curso(curso_sk),
    proveedor_sk INTEGER REFERENCES dim_proveedor(proveedor_sk),
    lugar_realizacion_sk INTEGER REFERENCES dim_lugar_realizacion(lugar_sk),
    -- Métricas
    costo_total_curso DECIMAL(15,2),
    duracion_horas_total INTEGER,
    dias_extension INTEGER,
    total_asistentes INTEGER,
    nps_score INTEGER,
    satisfaccion_promedio DECIMAL(5,2),
    valoracion_formador DECIMAL(5,2)
);
COMMENT ON TABLE fact_realizacion_capacitacion IS 'Gestión de la oferta. Una fila por edición del curso.';

-- ÁREA: CAPACITACIÓN (DEMANDA)
CREATE TABLE fact_participacion_capacitacion (
    participacion_id SERIAL PRIMARY KEY,
    -- Foreign Keys
    mes_realizacion_sk INTEGER REFERENCES dim_tiempo(tiempo_sk),
    empleado_sk INTEGER REFERENCES dim_empleado(empleado_sk),
    curso_sk INTEGER REFERENCES dim_curso(curso_sk),
    -- Link para Drill-Across
    realizacion_link_id INTEGER REFERENCES fact_realizacion_capacitacion(realizacion_id),
    -- Métricas
    horas_capacitacion_recibidas DECIMAL(10,2),
    asistencia_count INTEGER DEFAULT 1
);
COMMENT ON TABLE fact_participacion_capacitacion IS 'Historial de aprendizaje del empleado.';
COMMENT ON COLUMN fact_participacion_capacitacion.realizacion_link_id IS 'Para drill-across a costos en FactRealizacion';
