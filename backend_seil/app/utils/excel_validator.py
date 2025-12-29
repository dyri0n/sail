import pandas as pd
from fastapi import UploadFile, HTTPException, status

REQUIRED_COLUMNS = {
    "rut",
    "fecha_movimiento",
    "tipo_movimiento",
    "cargo",
    "centro_costo"
}


async def validate_rotacion_excel(file: UploadFile):
    try:
        df = pd.read_excel(file.file)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo Excel inválido"
        )

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Columnas faltantes: {missing}"
        )

    file.file.seek(0)  # 🔥 IMPORTANTE
