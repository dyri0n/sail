INSERT INTO dwh.dim_proveedor (nombre_proveedor, tipo_proveedor)
SELECT DISTINCT 
    TRIM(UPPER(formador_proveedor)),
    TRIM(UPPER(externo_interno))
FROM stg.stg_realizacion_capacitaciones
WHERE formador_proveedor IS NOT NULL
ON CONFLICT (nombre_proveedor) DO NOTHING;