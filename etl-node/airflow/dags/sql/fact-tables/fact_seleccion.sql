-- PARA CADA (Solicitud) EN el_archivo_excel_staging:

--     // PASO 1: Identificar a los actores
--     // ------------------------------------------------
--     ID_PROCESO = Solicitud.id_proceso (Esta es la clave única)
--     CANDIDATO  = Buscar en DimEmpleado el RUT/Nombre de quien ganó (si hay alguien)

--     // PASO 2: El Cruce con Rotación (Quality of Hire)
--     // "Oye DWH, ¿este candidato que contratamos sigue aquí o se fue?"
--     // ------------------------------------------------
--     DATO_CONTINUIDAD = NULL
--     RAZON_FALLA      = NULL

--     SI (CANDIDATO existe):
--         // Miramos la OTRA tabla (FactRotacion)
--         ¿EXISTE una "Baja" o "Renuncia" para este CANDIDATO en FactRotacion?
        
--         SI (SI, encontramos una baja):
--             DATO_CONTINUIDAD = 0  (No tuvo continuidad, falló)
--             RAZON_FALLA      = Traer "Renuncia Voluntaria" de FactRotacion
        
--         SINO (NO, no hay bajas, sigue activo):
--             DATO_CONTINUIDAD = 1  (Éxito)
--             RAZON_FALLA      = NULL

--     // PASO 3: Definir el Estado del Proceso (La foto actual)
--     // ------------------------------------------------
--     ESTADO = ""
--     SI (Solicitud tiene fecha de cierre Y tiene continuidad definida):
--         ESTADO = "CERRADO" (Ya pasó la prueba o falló, fin de la historia)
    
--     SINO SI (Solicitud tiene fecha de cierre PERO no sabemos continuidad):
--         ESTADO = "EVALUANDO" (Lo contratamos hace poco, está en prueba)
    
--     SINO:
--         ESTADO = "BUSCANDO" (Aún entrevistando gente)

--     // PASO 4: La Operación UPSERT (Insertar o Actualizar)
--     // ------------------------------------------------
--     BUSCAR en FactSeleccion SI EXISTE EL ID_PROCESO:

--         CASO NO EXISTE (Es nuevo):
--             -> INSERTAR nueva fila con ESTADO, DATO_CONTINUIDAD, RAZON_FALLA...
        
--         CASO SI EXISTE (Ya estaba cargado ayer):
--             -> ACTUALIZAR la fila existente:
--                - ¿Cambió el estado de "Buscando" a "Evaluando"? -> Actualízalo.
--                - ¿Apareció una baja en Rotación? -> Actualiza DATO_CONTINUIDAD a 0.
--                - ¿Se corrigió la duración? -> Actualízalo.

INSERT INTO dwh.fact_seleccion (
    fecha_apertura_sk, 
    fecha_cierre_sk,
    cargo_solicitado_sk, 
    empleado_seleccionado_sk, 
    gerencia_solicitante_sk,
    id_solicitud_nk, 
    fuente_reclutamiento, 
    recruiter_responsable,
    estado_final_proceso,
    duracion_proceso_dias, 
    costo_proceso, 
    cantidad_candidatos, 
    cantidad_entrevistas,
    tiene_continuidad, 
    motivo_fallo_continuidad
)
SELECT 
    -- 1. Fechas
    TO_CHAR((s.fecha_cierre - (COALESCE(s.duracion_dias, 0) || ' days')::INTERVAL), 'YYYYMMDD')::INTEGER,
    TO_CHAR(s.fecha_cierre, 'YYYYMMDD')::INTEGER,

    -- 2. Dimensiones
    COALESCE(dc.cargo_sk, -1),
    COALESCE(de.empleado_sk, -1),
    COALESCE(dg.gerencia_sk, -1),

    -- 3. Degeneradas (Business Key)
    s.id_proceso::VARCHAR, -- ESTE ES EL NK (castear a VARCHAR)
    s.fuente_reclutamiento,
    'No Asignado', -- FIX: Recruiter Responsable (No viene en el staging) 
    
    -- Lógica de Estado
    CASE 
        WHEN s.tiene_continuidad IS NOT NULL THEN 'CERRADO'
        WHEN s.fecha_cierre IS NOT NULL AND s.tiene_continuidad IS NULL THEN 'EVALUANDO'
        ELSE 'BUSCANDO' 
    END,

    -- 4. Medidas
    s.duracion_dias,
    s.coste_proceso,
    s.nro_cvs_recibidos,
    (COALESCE(s.nro_personas_entrevistadas_telefono, 0) + COALESCE(s.nro_personas_entrevistadas_presencial, 0)),

    -- 5. Quality (tiene_continuidad ahora es BOOLEAN)
    CASE 
        WHEN s.tiene_continuidad = TRUE THEN 1
        WHEN s.tiene_continuidad = FALSE THEN 0
        ELSE NULL 
    END,
    
    -- Lookup Motivo Fallo
    CASE 
        WHEN s.tiene_continuidad = FALSE THEN fr_baja.razon_detallada
        ELSE NULL 
    END

FROM stg.stg_proceso_seleccion s
LEFT JOIN dwh.dim_cargo dc ON TRIM(UPPER(s.cargo)) = dc.nombre_cargo
LEFT JOIN dwh.dim_gerencia dg ON TRIM(UPPER(s.gerencia)) = dg.nombre_gerencia
LEFT JOIN dwh.dim_empleado de ON TRIM(UPPER(s.nombre)) = TRIM(UPPER(de.nombre_completo)) AND de.scd_es_actual = TRUE 
LEFT JOIN (
    SELECT fr.empleado_sk, dm.razon_detallada
    FROM dwh.fact_rotacion fr
    JOIN dwh.dim_medida_aplicada dm ON fr.medida_sk = dm.medida_sk
    WHERE dm.tipo_movimiento IN ('BAJA', 'DESPIDO', 'RENUNCIA')
      AND fr.fecha_fin_vigencia_sk IS NOT NULL
) fr_baja ON de.empleado_sk = fr_baja.empleado_sk

-- LA MAGIA DEL UPSERT
ON CONFLICT (id_solicitud_nk) 
DO UPDATE SET
    -- Actualizamos los campos que pueden cambiar con el tiempo
    fecha_cierre_sk = EXCLUDED.fecha_cierre_sk,
    empleado_seleccionado_sk = EXCLUDED.empleado_seleccionado_sk,
    estado_final_proceso = EXCLUDED.estado_final_proceso,
    duracion_proceso_dias = EXCLUDED.duracion_proceso_dias,
    cantidad_candidatos = EXCLUDED.cantidad_candidatos,
    cantidad_entrevistas = EXCLUDED.cantidad_entrevistas,
    tiene_continuidad = EXCLUDED.tiene_continuidad,
    motivo_fallo_continuidad = EXCLUDED.motivo_fallo_continuidad,
    fecha_carga = CURRENT_TIMESTAMP; -- Auditamos que se tocó la fila