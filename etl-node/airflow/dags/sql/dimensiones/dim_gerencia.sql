TRUNCATE TABLE dwh.dim_gerencia RESTART IDENTITY CASCADE;

INSERT INTO
    dwh.dim_gerencia (nombre_gerencia)
SELECT DISTINCT
    TRIM(UPPER(gerencia))
FROM stg.stg_resumen_anual_capacitaciones
WHERE
    gerencia IS NOT NULL
UNION
SELECT DISTINCT
    TRIM(UPPER(gerencia))
FROM stg.stg_proceso_seleccion
WHERE
    gerencia IS NOT NULL;