-- Carga snapshot de dotación desde SAP usando DISTINCT ON para garantizar 1 row por empleado
INSERT INTO dwh.fact_dotacion_snapshot (
    mes_cierre_sk,
    empleado_sk,
    cargo_sk,
    empresa_sk,
    modalidad_sk,
    headcount,
    fte_real,
    horas_capacidad_mensual,
    sueldo_base_mensual,
    antiguedad_meses
)
SELECT 
    mes_cierre_sk,
    empleado_sk,
    cargo_sk,
    empresa_sk,
    modalidad_sk,
    headcount,
    fte_real,
    horas_capacidad_mensual,
    sueldo_base_mensual,
    antiguedad_meses
FROM (
    SELECT DISTINCT ON (COALESCE(de.empleado_sk, -1))
        TO_CHAR(CURRENT_DATE, 'YYYYMMDD')::INTEGER AS mes_cierre_sk,
        COALESCE(de.empleado_sk, -1) AS empleado_sk,
        COALESCE(dc.cargo_sk, -1) AS cargo_sk,
        COALESCE(demp.empresa_sk, -1) AS empresa_sk,
        COALESCE(dm.modalidad_sk, -1) AS modalidad_sk,
        1 AS headcount,
        1.0 AS fte_real,
        180 AS horas_capacidad_mensual,
        COALESCE(s.sueldo_base, 0) AS sueldo_base_mensual,
        (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM COALESCE(s.inicio, s.desde_area, CURRENT_DATE))) * 12 +
        (EXTRACT(MONTH FROM CURRENT_DATE) - EXTRACT(MONTH FROM COALESCE(s.inicio, s.desde_area, CURRENT_DATE))) AS antiguedad_meses
    FROM stg.stg_dotacion_sap s
    LEFT JOIN dwh.dim_empleado de 
        ON CAST(s.id_personal AS VARCHAR) = de.empleado_id_nk
        AND de.scd_es_actual = TRUE
    LEFT JOIN dwh.dim_cargo dc 
        ON TRIM(UPPER(s.posicion)) = dc.nombre_cargo
    LEFT JOIN dwh.dim_empresa demp 
        ON CAST(s.id_sociedad AS VARCHAR) = demp.codigo
    LEFT JOIN dwh.dim_modalidad_contrato dm 
        ON TRIM(UPPER(s.relacion_laboral)) = dm.tipo_vinculo_legal
        AND '45 HORAS' = dm.regimen_horario
    ORDER BY COALESCE(de.empleado_sk, -1), s.id_personal
) sub

ON CONFLICT (mes_cierre_sk, empleado_sk) 
DO UPDATE SET
    cargo_sk = EXCLUDED.cargo_sk,
    empresa_sk = EXCLUDED.empresa_sk,
    modalidad_sk = EXCLUDED.modalidad_sk,
    headcount = EXCLUDED.headcount,
    fte_real = EXCLUDED.fte_real,
    horas_capacidad_mensual = EXCLUDED.horas_capacidad_mensual,
    sueldo_base_mensual = EXCLUDED.sueldo_base_mensual,
    antiguedad_meses = EXCLUDED.antiguedad_meses;
