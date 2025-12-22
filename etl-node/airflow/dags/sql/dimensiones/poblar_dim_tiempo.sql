-- =============================================================================
-- POBLAR_DIM_TIEMPO.SQL - Generación de dimensión tiempo (2010 hasta +5 años)
-- =============================================================================
-- Estrategia: INSERT con ON CONFLICT DO NOTHING (no sobrescribe fechas existentes)
-- Esto permite ejecutar el script múltiples veces sin duplicar ni perder datos
-- =============================================================================

INSERT INTO dwh.dim_tiempo (
    tiempo_sk,
    fecha,
    anio,
    mes_nombre,
    mes_numero,
    trimestre,
    dia_semana,
    es_fin_de_semana,
    es_feriado,
    nombre_feriado,
    tipo_feriado,
    es_irrenunciable,
    semana_anio
)
SELECT
    -- SK: Formato YYYYMMDD (Ej: 20231201)
    TO_CHAR(datum, 'YYYYMMDD')::INTEGER AS tiempo_sk,

    -- Fecha real
    datum AS fecha,

    -- Año
    EXTRACT(YEAR FROM datum)::SMALLINT AS anio,

    -- Nombre del Mes (Case para asegurar español sin depender de config del server)
    CASE EXTRACT(MONTH FROM datum)
        WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
    END AS mes_nombre,

    -- Número de mes
    EXTRACT(MONTH FROM datum)::SMALLINT AS mes_numero,

    -- Trimestre (Q1, Q2, etc)
    'Q' || TO_CHAR(datum, 'Q') AS trimestre,

    -- Día de la semana (Case para español)
    CASE EXTRACT(ISODOW FROM datum)
        WHEN 1 THEN 'Lunes' WHEN 2 THEN 'Martes' WHEN 3 THEN 'Miércoles'
        WHEN 4 THEN 'Jueves' WHEN 5 THEN 'Viernes' WHEN 6 THEN 'Sábado'
        WHEN 7 THEN 'Domingo'
    END AS dia_semana,

    -- Es fin de semana (6=Sábado, 7=Domingo en ISO)
    CASE WHEN EXTRACT(ISODOW FROM datum) IN (6, 7) THEN TRUE ELSE FALSE END AS es_fin_de_semana,

    -- Es Feriado (Por defecto FALSE, se actualiza con update_feriados.sql)
    FALSE AS es_feriado,

    -- Nombre del feriado (NULL por defecto)
    NULL AS nombre_feriado,

    -- Tipo de feriado (NULL por defecto)
    NULL AS tipo_feriado,

    -- Es irrenunciable (FALSE por defecto)
    FALSE AS es_irrenunciable,

    -- Semana del año
    EXTRACT(WEEK FROM datum)::SMALLINT AS semana_anio

FROM generate_series(
    '2010-01-01'::DATE,
    (CURRENT_DATE + INTERVAL '5 years')::DATE,
    '1 day'::INTERVAL
) AS datum

-- Si la fecha ya existe, no hacer nada (preservar datos de feriados actualizados)
ON CONFLICT (tiempo_sk) DO NOTHING;

-- =============================================================================
-- REGISTRO ESPECIAL: "Fin de los tiempos" (9999-12-31)
-- =============================================================================
-- Usado para registros SCD Tipo 2 activos (sin fecha de fin de vigencia)
-- y para representar "fecha desconocida" o "sin límite"
-- =============================================================================
INSERT INTO dwh.dim_tiempo (
    tiempo_sk,
    fecha,
    anio,
    mes_nombre,
    mes_numero,
    trimestre,
    dia_semana,
    es_fin_de_semana,
    es_feriado,
    nombre_feriado,
    tipo_feriado,
    es_irrenunciable,
    semana_anio
) VALUES (
    99991231,
    '9999-12-31'::DATE,
    9999,
    'Diciembre',
    12,
    'Q4',
    'Viernes',
    FALSE,
    FALSE,
    NULL,
    NULL,
    FALSE,
    52
) ON CONFLICT (tiempo_sk) DO NOTHING;
