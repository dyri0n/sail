# 🚨 RESUMEN EJECUTIVO - DIAGNÓSTICO STG vs DWH

**Fecha:** 7 de enero de 2026  
**Análisis por:** Script automatizado `diagnostico_stg_vs_dwh.py`

---

## PROBLEMA PRINCIPAL

### ❌ **dim_empleado está INCOMPLETO (50% de empleados faltantes)**

```
Total empleados en STG:         505 empleados únicos
Total empleados en dim_empleado: 255 empleados
FALTANTES:                       250 empleados (49.5%)
```

**Causa raíz:** `dim_empleado` se carga **ÚNICAMENTE** desde `stg_rotacion_empleados`, ignorando empleados que aparecen en:

- `stg_asistencia_diaria` (318 empleados, 230 NO están en rotación)
- `stg_participacion_capacitaciones` (262 empleados, 194 NO están en rotación)

---

## IMPACTO CRÍTICO

### 📊 Datos Perdidos

| Área                             | STG    | DWH   | Pérdida | %Pérdida   |
| -------------------------------- | ------ | ----- | ------- | ---------- |
| **Participaciones capacitación** | 892    | 231   | 661     | **74.1%**  |
| **Horas formación**              | 4,024  | 1,207 | 2,817   | **70.0%**  |
| **Asistencias válidas**          | 80,141 | 0\*   | 80,141  | **100%\*** |

\*Todas las asistencias tienen `empleado_sk = -1` (inválido)

### 👥 Empleados Afectados

```
Participación capacitaciones:
  - Solo 68 de 262 empleados tienen datos (74% perdidos)
  - 194 empleados sin match en dim_empleado

Asistencias:
  - Solo 88 de 318 empleados tienen match (72% sin match)
  - 230 empleados sin match en dim_empleado
  - 57,964 asistencias sin empleado válido
```

---

## 🎯 SOLUCIÓN

### Opción Recomendada: Completar dim_empleado

**Paso 1:** Cargar empleados faltantes en `dim_empleado`

```sql
INSERT INTO dwh.dim_empleado (empleado_id_nk, ...)
SELECT DISTINCT
    id_empleado::text,
    -- campos disponibles de asistencia/participación
FROM (
    SELECT DISTINCT id_empleado FROM stg.stg_asistencia_diaria
    UNION
    SELECT DISTINCT id_empleado FROM stg.stg_participacion_capacitaciones
) empleados
WHERE NOT EXISTS (
    SELECT 1 FROM dwh.dim_empleado
    WHERE empleado_id_nk = empleados.id_empleado::text
);
```

**Paso 2:** Recargar facts afectadas

- TRUNCATE `fact_asistencia`
- TRUNCATE `fact_participacion_capacitacion`
- Re-ejecutar DAGs de ETL

**Paso 3:** Validar

- Ejecutar `uv run python diagnostico_stg_vs_dwh.py`
- Verificar que ratio DWH/STG > 95%

---

## 📈 IMPACTO DE LA CORRECCIÓN

### Antes (Actual)

- ❌ 74% de capacitaciones perdidas
- ❌ 100% de asistencias inválidas
- ❌ Reportes gerenciales incorrectos

### Después (Esperado)

- ✅ 95%+ de capacitaciones cargadas
- ✅ 95%+ de asistencias con empleado correcto
- ✅ Reportes gerenciales confiables
- ✅ Análisis de puntualidad/ausentismo válido

---

## 🔧 ARCHIVOS GENERADOS

### Scripts de Diagnóstico (en `/scripts`)

1. **diagnostico_stg_vs_dwh.py** - Diagnóstico comprensivo STG vs DWH
2. **investigar_participacion.py** - Análisis detallado de participaciones
3. **investigar_asistencias.py** - Análisis detallado de asistencias
4. **analisis_dim_empleado.py** - Análisis de causa raíz

### Reportes

1. **DIAGNOSTICO_STG_DWH_2026-01-07.md** - Reporte completo con hallazgos
2. **RESUMEN_EJECUTIVO.md** - Este documento

---

## ⏱️ TIEMPO ESTIMADO DE CORRECCIÓN

- **Desarrollo de script de carga:** 2-4 horas
- **Pruebas en ambiente dev:** 1-2 horas
- **Ejecución en producción:** 1 hora
- **Validación:** 1 hora
- **Total:** 5-8 horas

---

## 📞 PRÓXIMOS PASOS

1. ✅ Diagnóstico completado
2. ⏳ Desarrollar script de carga incremental de dim_empleado
3. ⏳ Probar en ambiente dev
4. ⏳ Ejecutar en producción
5. ⏳ Validar con script de diagnóstico
6. ⏳ Documentar proceso

---

## 📝 NOTAS TÉCNICAS

**Conexión DB:**

```
host=localhost port=6000 dbname=rrhh_prod user=postgres
```

**Rango de datos:**

- Asistencias: 2024-04-29 a 2025-01-05 (252 días)
- Capacitaciones: 7 meses únicos

**Comandos de diagnóstico:**

```bash
cd d:\Code\SAIL\scripts
uv run python diagnostico_stg_vs_dwh.py
uv run python investigar_participacion.py
uv run python investigar_asistencias.py
uv run python analisis_dim_empleado.py
```
