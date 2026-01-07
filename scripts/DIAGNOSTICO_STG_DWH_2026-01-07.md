# REPORTE DE DIAGNÓSTICO: STG vs DWH

**Fecha:** 2026-01-07  
**Sistema:** SAIL - Análisis de Integridad de Datos  
**Alcance:** Capacitaciones (Realización y Participación) + Asistencias

---

## � HALLAZGO CRÍTICO - CAUSA RAÍZ

### **dim_empleado está INCOMPLETO: 250 empleados faltantes (49.5%)**

**Problema Principal:**

- `dim_empleado` se carga ÚNICAMENTE desde `stg_rotacion_empleados` (255 empleados)
- `stg_asistencia_diaria` tiene **318 empleados únicos** (63 NO están en rotación)
- `stg_participacion_capacitaciones` tiene **262 empleados únicos** (7 NO están en rotación)
- **Total empleados únicos en STG:** 505 empleados
- **Total en dim_empleado:** 255 empleados
- **Empleados faltantes:** 250 empleados (49.5% de pérdida)

**Rangos de IDs por tabla:**
| Tabla | Min ID | Max ID | Empleados Únicos |
|-------|--------|--------|------------------|
| stg_rotacion_empleados | 101466 | 104439 | 255 |
| stg_participacion_capacitaciones | 100093 | 104360 | 262 |
| stg_asistencia_diaria | 100093 | 104404 | 318 |
| **dim_empleado** | **101466** | **104439** | **255** |

**Conclusión:** El rango de IDs en rotación (101466-104439) NO cubre el rango completo de participación/asistencia (100093-104404). Hay empleados con IDs más bajos que nunca se cargan.

---

## 🔴 HALLAZGOS CRÍTICOS

### 1. PARTICIPACIÓN EN CAPACITACIONES - PÉRDIDA MASIVA DE DATOS

**Severidad:** CRÍTICA 🔴

**Problema:**

- **STG:** 892 registros de participación
- **DWH:** 231 registros de participación (173 según análisis detallado)
- **Pérdida:** 661 registros (74.1% de los datos NO se están cargando)

**Causa Raíz Confirmada:**

- **194 empleados** en `stg_participacion_capacitaciones` NO están en `dim_empleado`
- Estos 194 empleados representan **218 participaciones perdidas**
- El ETL solo carga participaciones de empleados que existen en `dim_empleado`
- **Matching por ID:** Solo 70 de 272 empleados con RUT tienen match (25.7%)
- **Matching por RUT:** 0% (dim_empleado no tiene campo RUT o no se usa)

**Impacto en métricas:**

- Total horas formación STG: 4,024 horas
- Total horas formación DWH: 1,207 horas
- **Pérdida:** 2,817 horas (-70.0%)

**Empleados afectados:**

- Solo **68 empleados** tienen participaciones en DWH (vs 262-274 en STG)
- Promedio participaciones por empleado cargado: 2.54
- **195 empleados perdidos** (74.8%)

**Ejemplos de empleados con más participaciones perdidas:**
| ID | RUT | Nombre | Participaciones Perdidas |
|----|-----|--------|-------------------------|
| 102063 | 19353915-7 | MICHELLE ANNETTE LEAL LEYTON | 15 |
| 101938 | 18787113-1 | LORETO ANDREA FERNANDEZ GONZALEZ | 14 |
| 102642 | 17555090-9 | JOSE LUIS JIMENEZ VILLALOBOS | 14 |
| 102829 | 13006838-3 | WILSON DENNIS CASTILLO PEREZ | 13 |
| 102292 | 20348795-9 | ESKARLETT YUBINZA ZULETA COLQUE | 13 |

**Acción Requerida:**

- [x] **Causa raíz identificada:** dim_empleado incompleto
- [ ] Cargar 250 empleados faltantes en dim_empleado
- [ ] Recargar fact_participacion_capacitacion

---

### 2. ASISTENCIAS - PROBLEMA GRAVE DE EMPLEADO_SK

**Severidad:** CRÍTICA 🔴

**Problema:**

- **TODOS los 80,141 registros usan empleado_sk = -1 (valor por defecto/error)**
- La tabla fact_asistencia muestra solo 1 empleado único cuando deberían ser 318

**Causa Raíz Confirmada:**

- **230 empleados** en `stg_asistencia_diaria` NO están en `dim_empleado`
- Solo **88 de 318 empleados** (27.7%) tienen match en dim_empleado
- **57,964 asistencias** corresponden a empleados sin match
- El ETL usa `-1` como empleado_sk cuando no encuentra match (en lugar de omitir el registro)

**Datos comparativos:**

- STG: 318 empleados únicos
- Empleados con match en dim_empleado: 88 (27.7%)
- Empleados sin match: 230 (72.3%)
- DWH: 1 empleado_sk único (-1) = ERROR TOTAL

**Impacto:**

- ❌ Todas las asistencias están mal asignadas (empleado_sk = -1)
- ❌ No se pueden generar reportes por empleado
- ❌ Los análisis de puntualidad y ausentismo por persona son COMPLETAMENTE INVÁLIDOS
- ❌ 212,799 horas trabajadas sin atribución correcta

**Acción Requerida:**

- [x] **Causa raíz identificada:** dim_empleado incompleto + ETL usa -1 por defecto
- [ ] Cargar 250 empleados faltantes en dim_empleado
- [ ] Modificar ETL para que NO use -1 como default
- [ ] **TRUNCAR fact_asistencia**
- [ ] Recargar todas las asistencias con mapeo correcto

---

### 3. REALIZACIÓN DE CAPACITACIONES - DUPLICACIÓN MENOR

**Severidad:** MEDIA 🟡

**Problema:**

- STG: 75 realizaciones de capacitaciones
- DWH: 80 realizaciones de capacitaciones
- **Duplicación:** 5 registros adicionales (+6.67%)

**Impacto en métricas:**

- Total horas: STG=5,244, DWH=5,724 (+480 horas, +9.2%) ⚠️
- Total asistentes: STG=974, DWH=979 (+5, +0.5%) ✅
- Total coste: STG=$22,721, DWH=$22,969 (+$248, +1.1%) ✅

**Diferencias:**

- Cursos únicos: STG=57, DWH=59 (+2 cursos)
- Las fechas de inicio son las mismas (49 únicas)

**Causa Probable:**

- Algunos cursos se están insertando dos veces con diferentes curso_sk
- Posible problema en la deduplicación por (curso_sk, fecha_inicio_sk)
- La diferencia de +480 horas (+9.2%) sugiere registros duplicados con datos diferentes

**Acción Requerida:**

- [ ] Identificar los 5 registros duplicados en fact_realizacion_capacitacion
- [ ] Revisar la constraint UNIQUE (curso_sk, fecha_inicio_sk)
- [ ] Verificar por qué hay 2 cursos más en dim_curso que títulos únicos en STG

---

## ✅ ASPECTOS POSITIVOS

### 1. Asistencias - Conteo Total Correcto

- **Todos los registros de STG se cargan en DWH (80,141 = 80,141)**
- La información de fecha, hora, turnos y permisos se preserva correctamente
- Análisis de atrasos funciona (8,068 registros con atraso detectados)

### 2. Integridad Referencial Parcial

- ✅ fact_realizacion_capacitacion: Todas las FK de curso_sk y fecha_sk son válidas
- ✅ fact_participacion_capacitacion: Todas las FK de curso_sk son válidas
- ✅ fact_participacion_capacitacion: 100% vinculadas a realizaciones (realizacion_link_id)
- ✅ fact_asistencia: Todas las FK de fecha_sk son válidas

### 3. Dimensiones

- dim_curso tiene la mayoría de cursos mapeados
- dim_tiempo está correctamente poblado

---

## 📊 RESUMEN DE MÉTRICAS

### Realización de Capacitaciones

| Métrica          | STG     | DWH     | Diferencia      |
| ---------------- | ------- | ------- | --------------- |
| Total registros  | 75      | 80      | +5 (+6.7%)      |
| Cursos únicos    | 57      | 59      | +2 (+3.5%)      |
| Total asistentes | 974     | 979     | +5 (+0.5%)      |
| Total horas      | 5,244   | 5,724   | +480 (+9.2%) ⚠️ |
| Total coste      | $22,721 | $22,969 | +$248 (+1.1%)   |

### Participación en Capacitaciones

| Métrica          | STG     | DWH   | Diferencia         |
| ---------------- | ------- | ----- | ------------------ |
| Total registros  | 892     | 231   | -661 (-74.1%) 🔴   |
| Empleados únicos | 262-274 | 69    | -195 (-74.8%) 🔴   |
| Cursos únicos    | 56      | 58    | +2 (+3.6%)         |
| Total horas      | 4,024   | 1,207 | -2,817 (-70.0%) 🔴 |

### Asistencias

| Métrica          | STG    | DWH    | Diferencia       |
| ---------------- | ------ | ------ | ---------------- |
| Total registros  | 80,141 | 80,141 | 0 (0%) ✅        |
| Empleados únicos | 318    | 1      | -317 (-99.7%) 🔴 |
| Fechas únicas    | 252    | 252    | 0 (0%) ✅        |
| Con atraso       | 8,068  | 8,068  | 0 (0%) ✅        |

---

## 🎯 PLAN DE ACCIÓN PRIORITARIO

### PRIORIDAD 1 - CRÍTICO (Inmediato)

1. **Corregir mapeo de empleados en asistencias**

   - Archivo ETL: Revisar carga de fact_asistencia
   - Verificar JOIN entre id_empleado (STG) y empleado_sk (DWH)
   - Recargar todas las asistencias

2. **Recuperar 661 participaciones perdidas**
   - Revisar ETL de fact_participacion_capacitacion
   - Identificar por qué 195 empleados no tienen match
   - Corregir mapeo RUT/ID -> empleado_sk

### PRIORIDAD 2 - ALTA (Esta semana)

3. **Eliminar duplicados en realizaciones**
   - Identificar los 5 registros duplicados
   - Verificar constraint de negocio
   - Limpiar y recargar

### PRIORIDAD 3 - MEDIA (Próxima semana)

4. **Validar integridad de dim_empleado**
   - Verificar que todos los empleados de STG estén en DWH
   - Revisar proceso de carga de dimensión

---

## 📝 NOTAS TÉCNICAS

### Conexión utilizada:

```
host=localhost port=6000 dbname=rrhh_prod user=postgres
```

### Rangos de datos:

- **Asistencias:** 2024-04-29 a 2025-01-05 (252 días)
- **Capacitaciones:** 7 meses únicos de realización

### Próximos pasos sugeridos:

1. Ejecutar queries de investigación detallada
2. Revisar DAGs de Airflow para capacitaciones y asistencias
3. Validar dim_empleado contra stg_rotacion_empleados
4. Implementar tests de calidad de datos en el ETL
