-- =================================================================
-- CONFIGURACIÓN: MOTIVOS CONSIDERADOS VOLUNTARIOS
-- Editar este array según las reglas de negocio de RRHH
-- =================================================================
DO $$
DECLARE
    -- Lista de motivos que implican voluntariedad del empleado
    MOTIVOS_VOLUNTARIOS CONSTANT TEXT[] := ARRAY[
        'ART.159-1-MUTUO ACUERDO PARTES',
        'ART.159-2-RENUNCIA VOLUNTARIA',
        'BAJA VOLUNTARIA',
        'RENUNCIA'
        -- Agregar más motivos según necesidad:
        -- 'JUBILACIÓN PARCIAL',
        -- 'MUTUO ACUERDO'
    ];
BEGIN
    INSERT INTO dwh.dim_medida_aplicada (
        tipo_movimiento,
        razon_detallada,
        es_voluntario
    )
    SELECT DISTINCT
        TRIM(UPPER(clase_medida)),
        TRIM(UPPER(motivo_medida)),
        -- Regla de Voluntariedad: TRUE si el motivo está en la lista configurable
        CASE 
            WHEN TRIM(UPPER(motivo_medida)) = ANY(MOTIVOS_VOLUNTARIOS) THEN TRUE
            ELSE FALSE
        END
    FROM stg.stg_rotacion_empleados
    WHERE clase_medida IS NOT NULL
    ON CONFLICT (tipo_movimiento, razon_detallada) 
    DO UPDATE SET 
        es_voluntario = EXCLUDED.es_voluntario;
END $$;