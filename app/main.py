from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.telemetry.router import router as telemetry_router

app = FastAPI(
    title="AEGIS-MED API",
    version="0.1.0",
    description="Telemetría simulada de sensores biomédicos para el panel AEGIS-MED.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(telemetry_router, prefix="/api")
