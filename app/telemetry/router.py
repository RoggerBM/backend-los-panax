import asyncio
import json
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import StreamingResponse

from app.config import settings
from app.telemetry.mapper import build_snapshot
from app.telemetry.scenarios import SCENARIO_KEYS, SCENARIOS
from app.telemetry.schemas import ScenarioInfo, TelemetrySnapshot
from app.telemetry.simulator import simulator

router = APIRouter(tags=["telemetría"])

# Mismo id que el frontend: nombre del archivo de la cara en minúsculas (ej. "ana-torres")
CrewId = Annotated[str, Path(pattern=r"^[a-z0-9_-]{1,64}$", description="Id del tripulante")]
ScenarioKey = Annotated[str, Query(pattern=f"^({'|'.join(SCENARIO_KEYS)})$", description="Escenario")]


def _snapshot(crew_id: str, scenario: str) -> dict:
    readings = simulator.read(crew_id, scenario)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    return build_snapshot(crew_id, scenario, readings, timestamp)


@router.get("/scenarios", response_model=list[ScenarioInfo])
def list_scenarios() -> list[dict]:
    return [{"key": key, "label": s["label"], "tone": s["tone"]} for key, s in SCENARIOS.items()]


@router.get("/telemetry/{crew_id}", response_model=TelemetrySnapshot)
def get_telemetry(crew_id: CrewId, scenario: ScenarioKey = "nominal") -> dict:
    """Una lectura puntual de todos los sensores del tripulante."""
    return _snapshot(crew_id, scenario)


@router.get(
    "/telemetry/{crew_id}/stream",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}}, "description": "Un TelemetrySnapshot por evento"}},
)
async def stream_telemetry(request: Request, crew_id: CrewId, scenario: ScenarioKey = "nominal"):
    """Server-Sent Events: envía un snapshot `telemetry` cada TICK_SECONDS hasta que el cliente se desconecta."""

    async def events():
        yield "retry: 3000\n\n"
        while not await request.is_disconnected():
            payload = json.dumps(_snapshot(crew_id, scenario), ensure_ascii=False)
            yield f"event: telemetry\ndata: {payload}\n\n"
            await asyncio.sleep(settings.tick_seconds)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
