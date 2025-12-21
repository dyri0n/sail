-- Limpiamos para recarga completa (o usa DELETE WHERE fecha >= periodo si es incremental)
TRUNCATE TABLE dwh.fact_rotacion RESTART IDENTITY;

INSERT INTO dwh.fact_rotacion (
    fecha_inicio_vigencia_sk, fecha_fin_vigencia_sk,
    modalidad_sk, empleado_sk, empresa_sk, ceco_sk, cargo_sk, medida_sk,
    sueldo_base_intervalo, variacion_headcount
)
SELECT 
    -- 1. Fechas a SK (YYYYMMDD)
    TO_CHAR(s.desde3, 'YYYYMMDD')::INTEGER,
    TO_CHAR(COALESCE(s.hasta3, '9999-12-31'::DATE), 'YYYYMMDD')::INTEGER,

-- 2. Lookups a Dimensiones (Usamos LEFT JOIN para no perder datos si falta dim)
COALESCE(dm.modalidad_sk, -1), -- -1 suele usarse como 'Desconocido'

-- Lookup Empleado (SCD2): Buscamos el SK vigente en la fecha del evento
-- Cruzamos por Business Key (Rut o ID) y verificamos fecha
COALESCE(de.empleado_sk, -1),
COALESCE(demp.empresa_sk, -1),
COALESCE(dcc.ceco_sk, -1),
COALESCE(dc.cargo_sk, -1),
COALESCE(dma.medida_sk, -1),

-- 3. Métricas
0, -- Sueldo Base (No vi campo sueldo en tu staging, pon 0 o mapea columna correcta)

-- Lógica Variación Headcount
CASE
    WHEN UPPER(s.clase_medida) IN (
        'ALTA',
        'CONTRATACION',
        'REINGRESO'
    ) THEN 1
    WHEN UPPER(s.clase_medida) IN (
        'BAJA',
        'DESPIDO',
        'RENUNCIA',
        'TERMINO'
    ) THEN -1
    ELSE 0 -- Cambios de puesto, ascensos, etc.
END
FROM stg.stg_rotacion_empleados s

-- JOINs para recuperar los SKs (Surrogate Keys)
LEFT JOIN dwh.dim_modalidad_contrato dm ON TRIM(UPPER(s.tipo_empleo)) = dm.tipo_vinculo_legal
AND TRIM(UPPER(s.jornada)) = dm.regimen_horario
LEFT JOIN dwh.dim_empleado de ON s.rut = de.rut
AND s.desde3 BETWEEN de.scd_fecha_inicio_vigencia AND de.scd_fecha_fin_vigencia
LEFT JOIN dwh.dim_empresa demp ON CAST(s.id_empresa AS VARCHAR) = demp.codigo
LEFT JOIN dwh.dim_centro_costo dcc ON s.ceco = dcc.nombre_ceco
LEFT JOIN dwh.dim_cargo dc ON TRIM(UPPER(s.cargo)) = dc.nombre_cargo
LEFT JOIN dwh.dim_medida_aplicada dma ON TRIM(UPPER(s.clase_medida)) = dma.tipo_movimiento
AND TRIM(UPPER(s.motivo_medida)) = dma.razon_detallada;