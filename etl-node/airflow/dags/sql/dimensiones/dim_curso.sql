INSERT INTO dwh.dim_curso (nombre_curso, categoria_tematica, modalidad)
SELECT DISTINCT 
    TRIM(UPPER(titulo)),
    TRIM(UPPER(objetivo_area)),
    TRIM(UPPER(tipo_curso))
FROM stg.stg_capacitaciones_resumen
WHERE titulo IS NOT NULL
ON CONFLICT (nombre_curso, categoria_tematica, modalidad) DO NOTHING;