INSERT INTO dwh.dim_permiso (codigo_permiso_nk, descripcion, categoria_analitica)
SELECT DISTINCT
    TRIM(tipo_permiso),
    TRIM(tipo_permiso),
    -- Categorización básica (puedes expandir esto luego)
    CASE 
        WHEN LOWER(tipo_permiso) LIKE '%vacaciones%' THEN 'VACACIONES'
        WHEN LOWER(tipo_permiso) LIKE '%licencia%' THEN 'LICENCIA MEDICA'
        WHEN LOWER(tipo_permiso) LIKE '%falla%' OR LOWER(tipo_permiso) LIKE '%inasistente%' THEN 'AUSENCIA'
        WHEN LOWER(tipo_permiso) IN ('ninguno', '') THEN 'PRESENCIA'
        ELSE 'OTROS PERMISOS'
    END
FROM stg.stg_asistencia_diaria
WHERE tipo_permiso IS NOT NULL
ON CONFLICT (codigo_permiso_nk) DO NOTHING;