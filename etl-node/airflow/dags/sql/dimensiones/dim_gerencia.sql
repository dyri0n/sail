INSERT INTO
    dwh.dim_gerencia (nombre_gerencia)
SELECT DISTINCT
    TRIM(UPPER(gerencia))
FROM stg.stg_realizacion_capacitaciones
WHERE
    gerencia IS NOT NULL
UNION
SELECT DISTINCT
    TRIM(UPPER(gerencia))
FROM stg.stg_proceso_seleccion
WHERE
    gerencia IS NOT NULL
ON CONFLICT (nombre_gerencia) DO UPDATE SET
    nombre_gerencia = EXCLUDED.nombre_gerencia;