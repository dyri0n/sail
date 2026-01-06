INSERT INTO dwh.dim_turno (
    nombre_turno, 
    hora_inicio_teorica, 
    hora_fin_teorica, 
    descanso_min, 
    horas_jornada
)
SELECT DISTINCT
    TRIM(tipo_turno) as nombre_turno,
    
    -- Extracción Hora Inicio (Grupo 1 del Regex)
    (REGEXP_MATCHES(tipo_turno, '^(\d{2}:\d{2})\s?-\s?(\d{2}:\d{2})\((\d+)\s?.+\)'))[1]::TIME,
    
    -- Extracción Hora Fin (Grupo 2)
    (REGEXP_MATCHES(tipo_turno, '^(\d{2}:\d{2})\s?-\s?(\d{2}:\d{2})\((\d+)\s?.+\)'))[2]::TIME,
    
    -- Extracción Minutos Descanso (Grupo 3)
    (REGEXP_MATCHES(tipo_turno, '^(\d{2}:\d{2})\s?-\s?(\d{2}:\d{2})\((\d+)\s?.+\)'))[3]::INTEGER,
    
    -- Cálculo de Jornada Neta: (Fin - Inicio) - Descanso
    EXTRACT(EPOCH FROM (
        (REGEXP_MATCHES(tipo_turno, '^(\d{2}:\d{2})\s?-\s?(\d{2}:\d{2})\((\d+)\s?.+\)'))[2]::TIME - 
        (REGEXP_MATCHES(tipo_turno, '^(\d{2}:\d{2})\s?-\s?(\d{2}:\d{2})\((\d+)\s?.+\)'))[1]::TIME
    )) / 3600 
    - 
    ((REGEXP_MATCHES(tipo_turno, '^(\d{2}:\d{2})\s?-\s?(\d{2}:\d{2})\((\d+)\s?.+\)'))[3]::INTEGER / 60.0)

FROM stg.stg_asistencia_diaria
WHERE tipo_turno SIMILAR TO '\d{2}:\d{2}\s?-\s?\d{2}:\d{2}\(\d+\s?.+\)' -- Solo procesamos los que cumplen el formato

ON CONFLICT (nombre_turno) DO UPDATE SET
    hora_inicio_teorica = EXCLUDED.hora_inicio_teorica,
    hora_fin_teorica = EXCLUDED.hora_fin_teorica,
    descanso_min = EXCLUDED.descanso_min,
    horas_jornada = EXCLUDED.horas_jornada;

-- Insertamos los "Otros" (Descanso, No Planificado) sin horas
INSERT INTO dwh.dim_turno (nombre_turno)
SELECT DISTINCT TRIM(tipo_turno)
FROM stg.stg_asistencia_diaria
WHERE tipo_turno NOT SIMILAR TO '\d{2}:\d{2}\s?-\s?\d{2}:\d{2}\(\d+\s?.+\)'
ON CONFLICT (nombre_turno) DO NOTHING;