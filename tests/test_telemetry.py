import random

from fastapi.testclient import TestClient

from app.main import app
from app.telemetry.mapper import build_snapshot
from app.telemetry.scenarios import SCENARIO_KEYS, SCENARIOS
from app.telemetry.simulator import SensorSimulator

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_scenarios_match_frontend_keys():
    keys = [s["key"] for s in client.get("/api/scenarios").json()]
    assert keys == ["nominal", "sensor", "solar", "mars"]


def test_snapshot_shape():
    res = client.get("/api/telemetry/ana-torres", params={"scenario": "solar"})
    assert res.status_code == 200
    body = res.json()
    assert body["crewId"] == "ana-torres"
    for key in ("eva", "cardio", "temp", "sleep", "rad", "sans", "nutri", "spo2", "risks", "triage", "readings"):
        assert key in body
    assert body["cardio"]["badge"][0] == "TAQUICARDIA"
    assert body["rad"]["badge"][0] == "TORMENTA SPE"


def test_rejects_unknown_scenario_and_bad_id():
    assert client.get("/api/telemetry/ana-torres", params={"scenario": "luna"}).status_code == 422
    assert client.get("/api/telemetry/Ana Torres").status_code == 422


def test_base_readings_produce_expected_badges():
    """Con las lecturas base (sin ruido) cada escenario debe dar el diagnóstico esperado."""
    expected = {
        "nominal": ("NOMINAL", "VERIFICADO", "ALARA OK", "APTO EVA"),
        "sensor": ("NOMINAL", "DERIVA Δ>1°C", "ALARA OK", "REVISIÓN"),
        "solar": ("TAQUICARDIA", "FIEBRE ALERTA", "TORMENTA SPE", "NO APTO EVA"),
        "mars": ("CARGA 0.38G", "VERIFICADO", "SUPERFICIE", "ADAPTACIÓN"),
    }
    for key in SCENARIO_KEYS:
        s = build_snapshot("x", key, dict(SCENARIOS[key]["base"]), "t")
        got = (s["cardio"]["badge"][0], s["temp"]["badge"][0], s["rad"]["badge"][0], s["eva"]["label"])
        assert got[:3] == expected[key][:3], key
        assert got[3].startswith(expected[key][3]), key


def test_simulator_stays_near_baseline():
    sim = SensorSimulator(random.Random(1))
    hrs = [sim.read("ana-torres", "nominal")["hr"] for _ in range(300)]
    assert 55 <= min(hrs) and max(hrs) <= 80
