INSERT INTO
    dwh.dim_medida_aplicada (
        tipo_movimiento,
        razon_detallada,
        es_voluntario
    )
SELECT DISTINCT
    TRIM(UPPER(clase_medida)),
    TRIM(UPPER(motivo_medida)),
    CASE
        WHEN UPPER(motivo_medida) LIKE '%RENUNCIA%' THEN TRUE
        WHEN UPPER(motivo_medida) LIKE '%MUTUO ACUERDO%' THEN TRUE
        ELSE FALSE
    END
FROM staging.stg_rotacion_empleados
WHERE
    clase_medida IS NOT NULL ON CONFLICT (
        tipo_movimiento,
        razon_detallada
    ) DO NOTHING;