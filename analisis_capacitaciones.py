import pandas as pd

# Cargar archivo de capacitaciones - hoja de realizacion
# Buscar la hoja que empieza con "Informe"
xl = pd.ExcelFile("landing-zone/data_capacitaciones.xlsx")
print("=== HOJAS DISPONIBLES ===")
print(xl.sheet_names)

# Buscar hoja Informe 202X
hoja_informe = None
for sheet in xl.sheet_names:
    if "Informe" in sheet:
        hoja_informe = sheet
        break

print(f"\nUsando hoja: {hoja_informe}")

df = pd.read_excel(
    "landing-zone/data_capacitaciones.xlsx",
    sheet_name=hoja_informe,
    skiprows=4,
    header=0,
)

print("\n=== COLUMNAS DEL ARCHIVO ===")
print(df.columns.tolist())
print()

print("=== PRIMERAS 5 FILAS ===")
print(df.head().to_string())
print()

# La clave en fact_realizacion es (curso_sk, fecha_inicio_sk)
# curso_sk viene de titulo, fecha_inicio_sk viene de fecha_inicio
col_titulo = "Título capacitación"
col_fecha = "Fecha inicio"

print(f"=== BUSCANDO DUPLICADOS EN ({col_titulo}, {col_fecha}) ===")

# Normalizar titulo para la comparación (como hace el SQL con TRIM(UPPER()))
df["titulo_norm"] = df[col_titulo].astype(str).str.strip().str.upper()

# Encontrar duplicados
duplicados = df[df.duplicated(subset=["titulo_norm", col_fecha], keep=False)]
print(f"Total filas duplicadas: {len(duplicados)}")
print()

if len(duplicados) > 0:
    print("=== EJEMPLOS DE DUPLICADOS ===")
    count = 0
    for (titulo, fecha), grupo in duplicados.groupby(["titulo_norm", col_fecha]):
        if len(grupo) > 1:
            print(
                f"\n--- Titulo: {titulo[:50]}..., Fecha: {fecha} ({len(grupo)} registros) ---"
            )
            cols_mostrar = [
                c
                for c in [col_titulo, col_fecha, "Gerencia", "Asistentes", "Horas"]
                if c in grupo.columns
            ]
            print(grupo[cols_mostrar].to_string())
            count += 1
            if count >= 5:
                break

    print()
    print("=== RESUMEN DE DUPLICADOS ===")
    conteo = (
        duplicados.groupby(["titulo_norm", col_fecha])
        .size()
        .reset_index(name="repeticiones")
    )
    print(f"Combinaciones unicas con duplicados: {len(conteo)}")
    print("Distribucion de repeticiones:")
    print(conteo["repeticiones"].value_counts().to_string())
else:
    print("No se encontraron duplicados!")
