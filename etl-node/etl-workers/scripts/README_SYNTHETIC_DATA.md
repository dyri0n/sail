# Generador de Datos Sintéticos para DWH RRHH

## 📋 Descripción

Script Python que genera datos sintéticos limpios y realistas para todas las fuentes de datos del Data Warehouse de RRHH, corrigiendo métricas impossibles como tasas de rotación de 52,700%.

## ✨ Características

- **Integridad Referencial**: IDs de empleados consistentes (10000-10099) en todos los archivos
- **Métricas Realistas**: Tasa de rotación 15% (vs 52,700% en datos sucios)
- **Fechas Válidas**: Fecha de baja siempre posterior a fecha de contratación
- **Formato Chileno**: RUTs válidos (XX.XXX.XXX-X)
- **Datos Consistentes**: 85% empleados activos, 15% dados de baja

## 📦 Requisitos

```bash
pip install pandas faker openpyxl numpy
```

## 🚀 Uso

```bash
# Desde el directorio etl-workers/scripts/
python generate_synthetic_data.py
```

## 📁 Archivos Generados

El script crea un directorio `synthetic_data/` con los siguientes archivos:

1. **data_sap.xlsx** - Maestro de empleados
   - 100 empleados (85 activos, 15 dados de baja)
   - Columnas: Nº pers., RUT, Empresa, Área, Desde, Hasta, Posición, Sueldo, Nacimiento, Alta, Baja

2. **data_rotaciones.xlsx** - Eventos de cambios
   - Eventos de contratación y baja
   - Solo 1 evento de baja por empleado (corrige duplicados)

3. **data_asistencias.xlsx** - Registro de asistencia
   - Sheet "Días": ~6,000 registros diarios (últimos 90 días)
   - Sheet "Semana": Resúmenes semanales

4. **data_capacitaciones.xlsx** - Capacitaciones
   - Sheet "Informe 2025": 8-12 cursos realizados (header en fila 5)
   - Sheet "Participantes": Participaciones individuales

5. **data_asistencia_capacitaciones.xlsx** - Asistencia a cursos
   - Consistente con data_capacitaciones.xlsx

6. **data_gestion_asistencia.xlsx** - Gestión operativa
   - Similar a asistencias con columna "Turno"

7. **ID.csv** - Mapping RUT a ID (sin header)
   - Formato: RUT, APELLIDO, NOMBRE, ID_EMPLEADO

8. **CORREOS.csv** - Emails corporativos (sin header)
   - Formato: ID_EMPLEADO, EMAIL

## 🔍 Validación de Datos

El script incluye validaciones automáticas:

✅ **Integridad Temporal**: `Baja > Alta` siempre  
✅ **Integridad Referencial**: Mismo set de IDs en todos archivos  
✅ **Tasa de Rotación**: 15% ± 2% (realista)  
✅ **Asistencia**: Solo para empleados activos en ese período  
✅ **Capacitaciones**: Participantes válidos del maestro  

## 📊 Métricas Esperadas

Después de cargar los datos en el DWH:

| Métrica | Valor Esperado |
|---------|----------------|
| Total Empleados | 100 |
| Empleados Activos | 85 (85%) |
| Empleados Dados de Baja | 15 (15%) |
| **Tasa de Rotación** | **15%** ✅ |
| Registros de Asistencia | ~6,000 |
| Capacitaciones | 8-12 cursos |

## 🛠️ Personalización

Puedes ajustar los parámetros en el script:

```python
NUM_EMPLOYEES = 100  # Número de empleados a generar
EMPLOYEE_ID_START = 10000  # ID inicial
ACTIVE_EMPLOYEES_RATIO = 0.85  # 85% activos
OUTPUT_DIR = "synthetic_data"  # Directorio de salida
```

## 📝 Notas Importantes

- Los datos son completamente sintéticos (generados con Faker)
- RUTs son válidos en formato pero ficticios
- Fechas de contratación: últimos 5 años
- Asistencia: últimos 90 días (solo días laborables L-V)
- Semilla fija (42) para reproducibilidad

## 🔧 Troubleshooting

**Error: ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Los archivos no se generan**
- Verificar permisos de escritura
- El directorio `synthetic_data/` se crea automáticamente

**Tasa de rotación sigue alta**
- Asegurar que ACTIVE_EMPLOYEES_RATIO = 0.85
- Regenerar datos con semilla diferente si es necesario
