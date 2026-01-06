import pandas as pd

# Cargar archivo de capacitaciones
xl = pd.ExcelFile("landing-zone/data_capacitaciones.xlsx")
hoja_informe = [s for s in xl.sheet_names if "Informe" in s][0]
df = pd.read_excel(
    "landing-zone/data_capacitaciones.xlsx",
    sheet_name=hoja_informe,
    skiprows=4,
    header=0,
)

# Simular lo que hace el SQL: COALESCE(dc.curso_sk, -1) usando TRIM(UPPER(titulo))
# Si no encuentra curso en dim_curso, usa -1

# Normalizar titulo
df["titulo_norm"] = df["Título capacitación"].astype(str).str.strip().str.upper()

# La clave en fact_realizacion es (curso_sk, fecha_inicio_sk)
# Como curso_sk viene del JOIN, si no existe el curso, todos van a -1
# Esto puede causar duplicados

# Simulamos: titulo normalizado + fecha inicio
df["fecha_inicio_str"] = pd.to_datetime(df["Fecha inicio"]).dt.strftime("%Y%m%d")

# La clave seria (titulo_norm, fecha_inicio_str) - pero si varios titulos van a -1...
print("=== VERIFICANDO DUPLICADOS EN LA CLAVE FINAL ===")
print(f"Total registros: {len(df)}")

# Contar combinaciones únicas
combinaciones = (
    df.groupby(["titulo_norm", "fecha_inicio_str"]).size().reset_index(name="count")
)
duplicados = combinaciones[combinaciones["count"] > 1]
print(f"Combinaciones con duplicados: {len(duplicados)}")

if len(duplicados) > 0:
    print("\n=== DUPLICADOS ===")
    print(duplicados)

# Ahora el caso más probable: cursos con titulo NULL o vacio que van a -1
print("\n=== TITULOS PROBLEMATICOS ===")
titulos_vacios = df[
    df["Título capacitación"].isna()
    | (df["Título capacitación"].astype(str).str.strip() == "")
]
print(f"Titulos vacios/NULL: {len(titulos_vacios)}")

# Ver si hay cursos que podrían mapear al mismo curso_sk
print("\n=== TITULOS UNICOS ===")
print(f"Titulos unicos (normalizado): {df['titulo_norm'].nunique()}")
print(f"Fechas unicas: {df['fecha_inicio_str'].nunique()}")

# El problema real: la query puede generar múltiples filas por los JOINs
# Si dim_curso tiene múltiples filas para el mismo nombre_curso...
print("\n=== POSIBLE CAUSA: JOINS DUPLICAN FILAS ===")
print("Si dim_curso tiene múltiples filas con el mismo nombre_curso")
print("(diferente categoria_tematica o modalidad), el JOIN produce múltiples filas.")
print(
    "Esto causa que la misma combinación (curso_sk, fecha_inicio_sk) aparezca 2+ veces."
)
