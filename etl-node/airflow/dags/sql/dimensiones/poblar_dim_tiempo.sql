-- 1. Limpiamos la tabla para regenerarla completamente (Full Refresh)
TRUNCATE TABLE dim_tiempo;

-- 2. Insertamos generando la serie de fechas
INSERT INTO dim_tiempo (
    tiempo_sk,
    fecha,
    anio,
    mes_nombre,
    mes_numero,
    trimestre,
    dia_semana,
    es_fin_de_semana,
    es_feriado,
    semana_anio
)
SELECT
    -- SK: Formato YYYYMMDD (Ej: 20231201)
    TO_CHAR(datum, 'YYYYMMDD')::INTEGER AS tiempo_sk,

    -- Fecha real
    datum AS fecha,

    -- Año
    EXTRACT(YEAR FROM datum) AS anio,

    -- Nombre del Mes (Case para asegurar español sin depender de config del server)
    CASE EXTRACT(MONTH FROM datum)
        WHEN 1 THEN 'Enero' WHEN 2 THEN 'Febrero' WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril' WHEN 5 THEN 'Mayo' WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre' WHEN 11 THEN 'Noviembre' WHEN 12 THEN 'Diciembre'
    END AS mes_nombre,

    -- Número de mes
    EXTRACT(MONTH FROM datum) AS mes_numero,

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

    -- Es Feriado (Por defecto FALSE, actualizar luego con lógica de negocio específica)
    FALSE AS es_feriado,

    -- Semana del año
    EXTRACT(WEEK FROM datum) AS semana_anio

FROM (
    -- AQUÍ ESTÁ LA MAGIA: Generar serie desde 2010-01-01 hasta (Hoy + 3 Años)
    SELECT '2010-01-01'::DATE + SEQUENCE.DAY AS datum
    FROM GENERATE_SERIES(
        0,
        (DATE_PART('year', CURRENT_DATE) + 3 - 2010) * 365 + 1500 -- Un estimado holgado o calculo exacto de días
    ) AS SEQUENCE(DAY)
) DQ
WHERE datum <= (CURRENT_DATE + INTERVAL '3 years');
