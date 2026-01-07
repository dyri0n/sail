# Scripts de Diagnóstico - Sistema SAIL

Este directorio contiene scripts para diagnóstico y análisis de integridad de datos entre Staging (STG) y Data Warehouse (DWH).

## 📋 Scripts Disponibles

### 1. Diagnóstico Comprensivo

**Archivo:** `diagnostico_stg_vs_dwh.py`

Script principal que compara datos de STG vs DWH en todas las áreas críticas:

- ✅ Realización de capacitaciones
- ✅ Participación en capacitaciones
- ✅ Asistencias diarias
- ✅ Integridad de dimensiones
- ✅ Calidad de datos general

**Uso:**

```bash
uv run python diagnostico_stg_vs_dwh.py
```

**Salida:** Reporte detallado en consola con métricas comparativas y diagnóstico de problemas.

---

### 2. Resumen Visual

**Archivo:** `resumen_visual.py`

Muestra un resumen ejecutivo rápido y visual del estado del DWH.

**Uso:**

```bash
uv run python resumen_visual.py
```

**Salida:** Dashboard en consola con estado de cada área y plan de acción.

---

### 3. Investigación de Participaciones

**Archivo:** `investigar_participacion.py`

Análisis detallado de por qué se pierden participaciones en capacitaciones.

**Características:**

- Identifica empleados sin match en dim_empleado
- Analiza mapeo por ID vs RUT
- Muestra ejemplos de participaciones perdidas
- Calcula impacto en horas de formación

**Uso:**

```bash
uv run python investigar_participacion.py
```

---

### 4. Investigación de Asistencias

**Archivo:** `investigar_asistencias.py`

Análisis detallado del problema de empleado_sk en asistencias.

**Características:**

- Identifica por qué todos los registros usan empleado_sk = -1
- Analiza mapeo de id_empleado -> empleado_sk
- Muestra empleados con/sin match
- Calcula asistencias afectadas

**Uso:**

```bash
uv run python investigar_asistencias.py
```

---

### 5. Análisis de dim_empleado

**Archivo:** `analisis_dim_empleado.py`

Investiga la causa raíz: por qué dim_empleado está incompleto.

**Características:**

- Compara rangos de IDs en STG vs DWH
- Identifica empleados faltantes por tabla
- Verifica origen de dim_empleado
- Propone soluciones

**Uso:**

```bash
uv run python analisis_dim_empleado.py
```

---

## 📊 Reportes Generados

### RESUMEN_EJECUTIVO.md

Resumen breve con:

- Problema principal identificado
- Impacto en métricas
- Solución recomendada
- Tiempo estimado de corrección

### DIAGNOSTICO_STG_DWH_2026-01-07.md

Reporte completo con:

- Hallazgos críticos detallados
- Comparación de métricas STG vs DWH
- Análisis de integridad referencial
- Plan de acción prioritario

---

## 🔍 Hallazgos Principales (2026-01-07)

### 🔴 Problema Crítico Identificado

**dim_empleado está incompleto:**

- Solo tiene 255 empleados de 505 únicos en STG (50.5% faltantes)
- Se carga ÚNICAMENTE desde stg_rotacion_empleados
- Ignora empleados de stg_asistencia_diaria y stg_participacion_capacitaciones

### 📉 Impacto

| Área                         | Pérdida de Datos                      |
| ---------------------------- | ------------------------------------- |
| Participaciones capacitación | **74.1%** (661 de 892)                |
| Asistencias válidas          | **100%** (todas con empleado_sk = -1) |
| Empleados en participación   | **74.8%** (195 de 262)                |
| Empleados en asistencia      | **72.3%** (230 de 318)                |

### ✅ Solución Recomendada

1. **Completar dim_empleado** con empleados de todas las fuentes STG
2. **Recargar facts afectadas:**
   - TRUNCATE fact_asistencia
   - TRUNCATE fact_participacion_capacitacion
   - Re-ejecutar DAGs de ETL
3. **Validar** con scripts de diagnóstico

---

## 🛠️ Otros Scripts Útiles

### verify_dim_empleado.py

Verifica duplicados en dim_empleado (SCD Type 2).

### diag_dotacion.py

Diagnóstico de fact_dotacion_snapshot.

### diag_rotacion.py

Diagnóstico de fact_rotacion.

### check_dup.py

Verifica duplicados en varias tablas.

---

## 📝 Configuración

**Credenciales de Base de Datos:**

```python
DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"
```

**Ubicación:** Los scripts están en `d:\Code\SAIL\scripts\`

---

## 🚀 Workflow Recomendado

1. **Diagnóstico inicial:**

   ```bash
   uv run python resumen_visual.py
   ```

2. **Si hay problemas, ejecutar diagnóstico completo:**

   ```bash
   uv run python diagnostico_stg_vs_dwh.py
   ```

3. **Investigación detallada según el área:**

   ```bash
   # Para participaciones:
   uv run python investigar_participacion.py

   # Para asistencias:
   uv run python investigar_asistencias.py

   # Para dim_empleado:
   uv run python analisis_dim_empleado.py
   ```

4. **Implementar correcciones**

5. **Validar:**
   ```bash
   uv run python diagnostico_stg_vs_dwh.py
   ```

---

## 📚 Documentación Adicional

- Ver `RESUMEN_EJECUTIVO.md` para un resumen ejecutivo
- Ver `DIAGNOSTICO_STG_DWH_2026-01-07.md` para el reporte completo
- Ver `/dwh-node/init-scripts/*.sql` para esquemas de tablas

---

## 🤝 Contribuir

Para agregar nuevos scripts de diagnóstico:

1. Usar el mismo formato de DSN para conexión
2. Incluir manejo de errores con try/except
3. Usar `print_section()` para separar secciones
4. Documentar en este README

---

**Última actualización:** 7 de enero de 2026
