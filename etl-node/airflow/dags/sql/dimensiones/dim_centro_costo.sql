INSERT INTO dwh.dim_centro_costo (nombre_ceco)
SELECT DISTINCT
    ceco
FROM stg.stg_rotacion_empleados
WHERE ceco IS NOT NULL

ON CONFLICT (nombre_ceco)
DO UPDATE SET
    nombre_ceco = EXCLUDED.nombre_ceco;
