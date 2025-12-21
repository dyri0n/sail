INSERT INTO dwh.dim_cargo (nombre_cargo, familia_puesto, area_funcional)
SELECT DISTINCT
    TRIM(UPPER(cargo)),
    NULL, -- familia_puesto
    TRIM(UPPER(area))
FROM stg.stg_rotacion_empleados
WHERE cargo IS NOT NULL

ON CONFLICT (nombre_cargo)
DO UPDATE SET
    -- Si el cargo ya existía, actualizamos su área por si se movió
    area_funcional = EXCLUDED.area_funcional,
    -- Opcional: Actualizar fecha de modificación si tuvieras una columna 'updated_at'
    familia_puesto = EXCLUDED.familia_puesto;
