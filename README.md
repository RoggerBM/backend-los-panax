# AEGIS-MED · Backend (FastAPI)

API que simula los sensores biomédicos de cada tripulante y los envía al panel del frontend en tiempo real por **Server-Sent Events**.

## Requisitos

- Python 3.11 o superior (probado con 3.12)

## Puesta en marcha

```powershell
python -m venv .venv
.\.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # opcional
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva: http://localhost:8000/api/docs

Tests: `pytest`

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health` | Comprobación de vida |
| GET | `/api/scenarios` | Escenarios disponibles (`nominal`, `sensor`, `solar`, `mars`) |
| GET | `/api/telemetry/{crewId}?scenario=nominal` | Una lectura puntual |
| GET | `/api/telemetry/{crewId}/stream?scenario=nominal` | Stream SSE: un evento `telemetry` cada `TICK_SECONDS` |

`crewId` es el mismo id del frontend: el nombre del archivo de la cara en minúsculas, sin extensión (`ana-torres`).

## Cómo se relaciona con el frontend

Cada evento trae un snapshot con **la misma forma que un escenario de `frontend/src/features/dashboard/config/scenarios.js`** (`cardio`, `temp`, `sleep`, `rad`, `sans`, `nutri`, `spo2`, `risks`, `triage`, `eva`). Así el panel lo usa directamente. Además incluye:

- `readings`: lecturas crudas de los sensores (FC, VFC, presión, T1/T2, SpO2, dosis, PVT, glucosa, etc.);
- `crewId`, `scenario` y `timestamp`.

Las insignias, porcentajes y riesgos **se calculan con reglas a partir de las lecturas** (`app/telemetry/mapper.py`). Por ejemplo, FC > 100 da `TAQUICARDIA`, Δ entre T1 y T2 > 1 °C da `DERIVA`, y una dosis ≥ 2 mSv/d da `TORMENTA SPE`. Si el ruido cruza un umbral, el panel lo refleja.

## Estructura

```
app/
  main.py              App, CORS y routers
  config.py            Variables de entorno
  telemetry/
    scenarios.py       Lecturas base y contexto clínico por escenario
    simulator.py       Paseo aleatorio por tripulante y escenario
    mapper.py          Lecturas → snapshot del panel
    schemas.py         Modelos Pydantic (OpenAPI)
    router.py          Endpoints REST y SSE
tests/
```

## Variables de entorno

| Variable | Por defecto | Uso |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Orígenes permitidos, separados por comas. Añade tu dominio de Vercel. |
| `TICK_SECONDS` | `1.0` | Intervalo entre eventos del stream |

## Despliegue

Este backend mantiene conexiones abiertas (SSE), así que conviene un host con procesos persistentes, como Render, Railway o Fly.io, no funciones serverless:

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Luego, en el proyecto del frontend en Vercel, define `VITE_API_URL=https://tu-backend/api` y vuelve a desplegar.
