INSERT INTO dwh.fact_participacion_capacitacion (
    mes_realizacion_sk,
    empleado_sk,
    curso_sk,
    realizacion_link_id,
    horas_capacitacion_recibidas,
    asistencia_count
)
SELECT DISTINCT ON (mes_sk, empleado_sk, curso_sk)
    mes_sk,
    empleado_sk,
    curso_sk,
    realizacion_link_id,
    total_horas_formacion,
    asistencia_count
FROM (
    SELECT 
        TO_CHAR(
            MAKE_DATE(
                EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER,
                CASE UPPER(TRIM(s.mes))
                    WHEN 'ENERO' THEN 1 WHEN 'FEBRERO' THEN 2 WHEN 'MARZO' THEN 3
                    WHEN 'ABRIL' THEN 4 WHEN 'MAYO' THEN 5 WHEN 'JUNIO' THEN 6
                    WHEN 'JULIO' THEN 7 WHEN 'AGOSTO' THEN 8 WHEN 'SEPTIEMBRE' THEN 9
                    WHEN 'OCTUBRE' THEN 10 WHEN 'NOVIEMBRE' THEN 11 WHEN 'DICIEMBRE' THEN 12
                    ELSE 1
                END,
                1
            ),
            'YYYYMMDD'
        )::INTEGER AS mes_sk,
        
        COALESCE(de.empleado_sk, -1) AS empleado_sk,
        COALESCE(dc.curso_sk, -1) AS curso_sk,
        fr.realizacion_id AS realizacion_link_id,
        s.total_horas_formacion,
        1 AS asistencia_count

    FROM stg.stg_capacitaciones_participantes s

    LEFT JOIN dwh.dim_empleado de 
        ON s.rut = de.rut 
        AND de.scd_es_actual = TRUE

    LEFT JOIN dwh.dim_curso dc 
        ON TRIM(UPPER(s.nombre_curso)) = dc.nombre_curso

    -- JOIN por curso solamente (no hay fecha en realizacion para filtrar)
    LEFT JOIN dwh.fact_realizacion_capacitacion fr
        ON fr.curso_sk = dc.curso_sk
) subq

ON CONFLICT (mes_realizacion_sk, empleado_sk, curso_sk) DO UPDATE SET
    horas_capacitacion_recibidas = EXCLUDED.horas_capacitacion_recibidas,
    realizacion_link_id = EXCLUDED.realizacion_link_id;