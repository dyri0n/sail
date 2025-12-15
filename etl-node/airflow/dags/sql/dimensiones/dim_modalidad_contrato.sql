INSERT INTO dwh.dim_modalidad_contrato (tipo_vinculo, regimen_horario, fte_estandar)
SELECT DISTINCT
    TRIM(UPPER(tipo_empleo)),
    TRIM(UPPER(jornada)),
    CASE
        WHEN UPPER(jornada) LIKE '%FULL%' OR UPPER(jornada) LIKE '%ART%22%' THEN 1.0
        WHEN UPPER(jornada) LIKE '%PART%' OR UPPER(jornada) LIKE '%MEDIO%' THEN 0.5
        ELSE 1.0
    END
FROM staging.stg_rotacion_empleados
WHERE tipo_empleo IS NOT NULL

ON CONFLICT (tipo_vinculo, regimen_horario)
DO UPDATE SET
    fte_estandar = EXCLUDED.fte_estandar;
