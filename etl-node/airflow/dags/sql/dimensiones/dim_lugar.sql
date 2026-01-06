-- (Inferencia simple porque falta columna detallada en Staging)
INSERT INTO dwh.dim_lugar_realizacion (lugar, region, pais)
SELECT DISTINCT
    CASE 
        WHEN UPPER(lugar) LIKE '%ONLINE%' OR UPPER(lugar) LIKE '%VIRTUAL%' THEN 'AULA VIRTUAL'
        ELSE COALESCE(TRIM(UPPER(lugar)), 'OFICINA CENTRAL / NO INFORMADO')
    END,
    'ARICA Y PARINACOTA', -- FIX: Valor fijo (no viene en staging)
    'CHILE'
FROM stg.stg_realizacion_capacitaciones
ON CONFLICT (lugar) DO NOTHING;