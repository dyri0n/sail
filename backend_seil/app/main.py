from fastapi import FastAPI
from app.api.v1.router import router as api_router
app = FastAPI(
    title="SAIL - Plataforma de Datos API",
    description="API para la plataforma de datos SAIL",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")