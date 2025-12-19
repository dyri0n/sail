TRUNCATE TABLE dwh.fact_dotacion_snapshot;

INSERT INTO
    dwh.fact_dotacion_snapshot (
        mes_cierre_sk,
        empleado_sk,
        cargo_sk,
        empresa_sk,
        modalidad_sk,
        headcount,
        fte_real,
        horas_capacidad_mensual,
        sueldo_base_mensual,
        antiguedad_meses
    )
SELECT t.tiempo_sk AS mes_cierre_sk, f.empleado_sk, f.cargo_sk, f.empresa_sk, f.modalidad_sk,

-- Headcount: Si está activo al cierre de mes (Headcount = 1)
1 AS headcount,

-- Heredamos el FTE estándar de la dimensión modalidad (o 1.0 si nulo)
COALESCE(dm.fte_estandar, 1.0) AS fte_real,

-- Horas capacidad (ej: 180 horas al mes * FTE)
ROUND(
    180 * COALESCE(dm.fte_estandar, 1.0)
) AS horas_capacidad,
f.sueldo_base_intervalo,

-- Cálculo Antigüedad (Meses entre inicio real y fecha de corte)
-- Necesitaríamos la fecha real de ingreso (desde1 en staging),
-- aquí uso fecha_inicio_vigencia como proxy si no está disponible el ingreso original
(EXTRACT(YEAR FROM t.fecha) - EXTRACT(YEAR FROM TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD'))) * 12 +
    (EXTRACT(MONTH FROM t.fecha) - EXTRACT(MONTH FROM TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD'))) AS antiguedad

FROM dwh.fact_rotacion f
JOIN dwh.dim_tiempo t 
    -- EL TRUCO DEL SNAPSHOT:
    -- Buscamos fechas que sean fin de mes
    -- Y donde el intervalo de rotación cubra esa fecha
    ON t.fecha >= TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD')
    AND t.fecha <= TO_DATE(f.fecha_fin_vigencia_sk::text, 'YYYYMMDD')
    -- Filtramos solo los últimos días del mes (Asumo lógica de día siguiente es 1 o cambio de mes)
    AND EXTRACT(MONTH FROM t.fecha) != EXTRACT(MONTH FROM (t.fecha + INTERVAL '1 day'))

JOIN dwh.dim_modalidad_contrato dm ON f.modalidad_sk = dm.modalidad_sk
JOIN dwh.dim_medida_aplicada dma ON f.medida_sk = dma.medida_sk

WHERE 
    -- Excluir bajas definitivas del stock activo
    UPPER(dma.tipo_movimiento) NOT IN ('BAJA', 'DESPIDO', 'RENUNCIA');