-- ====================================================================
-- PASO 1: CALCULAR LA DELTA Y CLASIFICAR LA ACCIÓN
-- ====================================================================
CREATE TEMPORARY TABLE tmp_empleado_logic AS
SELECT
    -- Datos de Staging
    s.id_empleado AS id_nk,
    s.rut,
    s.nombre,
    s.sexo, s.fecha_nacimiento, s.nacionalidad, s.estado_civil,
    NULL::VARCHAR as formacion, -- (Mapear si existe en staging)

    -- Calculamos si en el origen viene activo
    CASE WHEN s.baja IS NULL OR s.baja > CURRENT_DATE THEN TRUE ELSE FALSE END AS stg_es_activo,

    -- Necesitamos 'tipo_empleo' SOLO para la lógica del IF (Eventual), no se guarda en Dim
    s.tipo_empleo,

    -- Datos Actuales en DWH
    d.empleado_sk AS sk_existente,
    d.scd_fecha_inicio_vigencia AS fecha_inicio_actual,
    d.estado_laboral_activo AS dwh_es_activo,

    -- HASH DIFF (Solo atributos personales)
    MD5(ROW(s.nombre, s.sexo, s.fecha_nacimiento, s.nacionalidad, s.estado_civil)::text) AS hash_stg,
    MD5(ROW(d.nombre_completo, d.sexo, d.fecha_nacimiento, d.nacionalidad, d.estado_civil)::text) AS hash_dwh,

    -- LÓGICA DE DECISIÓN (Aquí traducimos tu pseudocódigo a etiquetas)
    CASE
        -- CASO A: Nuevo
        WHEN d.empleado_sk IS NULL THEN 'NUEVO'

        -- CASO E (Optimizado): Reingreso Rápido de Eventual (< 30 días)
        WHEN (d.estado_laboral_activo = FALSE AND (s.baja IS NULL OR s.baja > CURRENT_DATE)) -- Es Reingreso
             AND s.tipo_empleo = 'Eventual'
             AND (CURRENT_DATE - d.scd_fecha_inicio_vigencia < 30)
             THEN 'REACTIVAR_SCD1'

        -- CASO E (Estándar): Reingreso Normal (Genera historia)
        WHEN (d.estado_laboral_activo = FALSE AND (s.baja IS NULL OR s.baja > CURRENT_DATE))
             THEN 'REINGRESO_SCD2'

        -- CASO D: Baja (Estaba activo, ahora inactivo)
        WHEN (d.estado_laboral_activo = TRUE AND NOT (s.baja IS NULL OR s.baja > CURRENT_DATE))
             THEN 'BAJA_SCD2'

        -- CASO C: Cambio de Atributos Personales
        WHEN MD5(ROW(s.nombre, s.sexo, s.fecha_nacimiento, s.nacionalidad, s.estado_civil)::text)
             <> MD5(ROW(d.nombre_completo, d.sexo, d.fecha_nacimiento, d.nacionalidad, d.estado_civil)::text)
             THEN 'CAMBIO_SCD2'

        ELSE 'SIN_CAMBIOS'
    END AS accion_requerida

FROM stg.stg_rotacion_empleados s
LEFT JOIN dwh.dim_empleado d
    ON s.id_empleado::VARCHAR = d.empleado_id_nk  -- Match por ID Negocio (SAP) - Cast a VARCHAR
    AND d.scd_es_actual = TRUE;          -- Solo contra la versión vigente

-- ====================================================================
-- PASO 2: EJECUTAR UPDATES (CERRAR VIGENCIAS O REACTIVAR)
-- ====================================================================

-- 2.1: REACTIVACIÓN RÁPIDA (Tu Caso E Optimizado)
-- Solo actualizamos el flag a True y borramos la fecha fin (como si nunca se hubiera ido)
UPDATE dwh.dim_empleado d
SET
    estado_laboral_activo = TRUE,
    scd_fecha_fin_vigencia = '9999-12-31'::DATE
FROM tmp_empleado_logic tmp
WHERE d.empleado_sk = tmp.sk_existente
  AND tmp.accion_requerida = 'REACTIVAR_SCD1';

-- 2.2: CERRAR VERSION ANTERIOR (Casos C, D y E Estándar)
-- Ponemos fecha fin = Ayer y scd_actual = False
UPDATE dwh.dim_empleado d
SET
    scd_es_actual = FALSE,
    scd_fecha_fin_vigencia = CURRENT_DATE - INTERVAL '1 day'
FROM tmp_empleado_logic tmp
WHERE d.empleado_sk = tmp.sk_existente
  AND tmp.accion_requerida IN ('REINGRESO_SCD2', 'BAJA_SCD2', 'CAMBIO_SCD2');

-- ====================================================================
-- PASO 3: INSERTAR NUEVAS FILAS
-- ====================================================================

INSERT INTO dwh.dim_empleado (
    empleado_id_nk, 
    rut, 
    nombre_completo,
    sexo, 
    fecha_nacimiento, 
    nacionalidad, 
    estado_civil, 
    formacion,
    estado_laboral_activo,
    scd_fecha_inicio_vigencia, 
    scd_fecha_fin_vigencia, 
    scd_es_actual
)
SELECT
    tmp.id_nk, 
    tmp.rut, 
    tmp.nombre,
    tmp.sexo, 
    tmp.fecha_nacimiento, 
    tmp.nacionalidad, 
    tmp.estado_civil, 
    tmp.formacion,

    -- Definir Estado Activo para la nueva fila
    CASE
        WHEN tmp.accion_requerida = 'BAJA_SCD2' THEN FALSE -- Caso D
        ELSE TRUE -- Casos Nuevo, Reingreso, Cambio Atributos (se asume activo)
    END,

    -- Fecha Inicio de vigencia (siempre es la fecha de carga)
    CURRENT_DATE,

    '9999-12-31', -- Fecha Fin Futura
    TRUE          -- Es Actual
FROM tmp_empleado_logic tmp
WHERE tmp.accion_requerida IN ('NUEVO', 'REINGRESO_SCD2', 'BAJA_SCD2', 'CAMBIO_SCD2');

-- Limpieza
DROP TABLE tmp_empleado_logic;
