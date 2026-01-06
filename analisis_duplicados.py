import pandas as pd

# Cargar archivo de asistencia
df = pd.read_excel("landing-zone/data_asistencias.xlsx", sheet_name="Días", header=0)

# Ver valores unicos en Cargo
print("=== VALORES UNICOS EN CARGO ===")
print(df["Cargo"].unique()[:20])
print(f"Total valores unicos: {df['Cargo'].nunique()}")

# Ver cuantos son 'Sin Cargo'
sin_cargo = df[df["Cargo"] == "Sin Cargo"]
print(f"\nRegistros con Sin Cargo: {len(sin_cargo)}")

# Intentar convertir a INTEGER como hace el loader
print("\n=== CONVERSION A INTEGER ===")
df["id_empleado"] = pd.to_numeric(df["Cargo"], errors="coerce")
print(f"Valores NULL despues de conversion: {df['id_empleado'].isna().sum()}")

# Si filtramos los NULL, quedan duplicados?
df_filtrado = df.dropna(subset=["id_empleado"])
print(f"Registros despues de filtrar NULL: {len(df_filtrado)}")

duplicados_post = df_filtrado[
    df_filtrado.duplicated(subset=["Fecha", "id_empleado"], keep=False)
]
print(f"Duplicados despues de filtrar: {len(duplicados_post)}")

if len(duplicados_post) > 0:
    print("\n=== DUPLICADOS RESTANTES ===")
    for (fecha, empleado), grupo in duplicados_post.groupby(["Fecha", "id_empleado"]):
        if len(grupo) > 1:
            print(f"\n--- Fecha: {fecha}, Empleado: {int(empleado)} ---")
            print(grupo.to_string())
            break
