from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as api_router
from app.api.v1.endpoints import etl_routes

app = FastAPI(
    title="SAIL - Plataforma de Datos API",
    description="API para la plataforma de datos SAIL",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # SvelteKit dev server
        "http://localhost:4173",  # SvelteKit preview
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos los headers
    expose_headers=["*"],  # Expone todos los headers en las respuestas
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(etl_routes.router, prefix="/api/v1")