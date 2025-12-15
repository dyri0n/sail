INSERT INTO dwh.dim_centro_costo (codigo_ceco, nombre_ceco)
SELECT DISTINCT
    ceco,
    ceco
FROM staging.stg_rotacion_empleados
WHERE ceco IS NOT NULL

ON CONFLICT (codigo_ceco)
DO UPDATE SET
    nombre_ceco = EXCLUDED.nombre_ceco;
