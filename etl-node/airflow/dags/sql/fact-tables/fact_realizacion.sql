INSERT INTO dwh.fact_realizacion_capacitacion (
    fecha_inicio_sk, fecha_fin_sk,
    gerencia_organizadora_sk, curso_sk, proveedor_sk, lugar_realizacion_sk,
    costo_total_curso, duracion_horas_total, dias_extension, 
    total_asistentes, nps_score, satisfaccion_promedio, valoracion_formador
)
SELECT 
    TO_CHAR(s.fecha_inicio, 'YYYYMMDD')::INTEGER,
    TO_CHAR(s.fecha_fin, 'YYYYMMDD')::INTEGER,
    COALESCE(dg.gerencia_sk, -1),
    COALESCE(dc.curso_sk, -1),
    COALESCE(dp.proveedor_sk, -1),
    COALESCE(dl.lugar_sk, -1),
    
    s.coste,
    s.total_horas,
    (s.fecha_fin - s.fecha_inicio), -- Dias extension
    s.nro_asistentes,
    s.nps,
    s.indice_satisfaccion,
    s.valoracion_formador

FROM stg.stg_realizacion_capacitaciones s

-- Joins Dimensiones
LEFT JOIN dwh.dim_gerencia dg ON TRIM(UPPER(s.gerencia)) = dg.nombre_gerencia
LEFT JOIN dwh.dim_curso dc ON TRIM(UPPER(s.titulo)) = dc.nombre_curso
LEFT JOIN dwh.dim_proveedor dp ON TRIM(UPPER(s.formador_proveedor)) = dp.nombre_proveedor
LEFT JOIN dwh.dim_lugar_realizacion dl ON (CASE WHEN UPPER(s.lugar) LIKE '%ONLINE%' OR UPPER(s.lugar) LIKE '%VIRTUAL%' THEN 'AULA VIRTUAL' ELSE 'OFICINA CENTRAL / NO INFORMADO' END) = dl.lugar

-- UPSERT: Business Key (curso_sk, fecha_inicio_sk)
ON CONFLICT (curso_sk, fecha_inicio_sk) DO UPDATE SET
    fecha_fin_sk = EXCLUDED.fecha_fin_sk,
    gerencia_organizadora_sk = EXCLUDED.gerencia_organizadora_sk,
    proveedor_sk = EXCLUDED.proveedor_sk,
    lugar_realizacion_sk = EXCLUDED.lugar_realizacion_sk,
    costo_total_curso = EXCLUDED.costo_total_curso,
    duracion_horas_total = EXCLUDED.duracion_horas_total,
    dias_extension = EXCLUDED.dias_extension,
    total_asistentes = EXCLUDED.total_asistentes,
    nps_score = EXCLUDED.nps_score,
    satisfaccion_promedio = EXCLUDED.satisfaccion_promedio,
    valoracion_formador = EXCLUDED.valoracion_formador,
    fecha_carga = CURRENT_TIMESTAMP;