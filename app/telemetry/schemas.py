"""Modelos de respuesta. Reflejan la forma de un escenario en el frontend (config/scenarios.js)."""

from typing import Literal

from pydantic import BaseModel

Tone = Literal["ok", "info", "warn", "danger"]
Badge = tuple[str, Tone]
Risk = tuple[int, str, Tone]


class ScenarioInfo(BaseModel):
    key: str
    label: str
    tone: Tone


class Eva(BaseModel):
    label: str
    tone: Tone


class Cardio(BaseModel):
    hr: int
    hrv: int
    badge: Badge
    sub: str
    pct: int


class Metric(BaseModel):
    value: str
    badge: Badge
    sub: str
    pct: int


class Sleep(BaseModel):
    hours: float
    badge: Badge
    sub: str
    pct: int


class Sans(BaseModel):
    pvt: int
    sub: str


class Nutri(BaseModel):
    gluc: int
    water: str
    badge: Badge
    sub: str
    pct: int


class Risks(BaseModel):
    rad: Risk
    neuro: Risk
    cardio: Risk


class Triage(BaseModel):
    tag: str
    tone: Tone
    title: str
    reason: str
    bullets: list[str]


class Readings(BaseModel):
    """Lecturas crudas de los sensores en este tick."""

    hr: int
    hrv: int
    bp_sys: int
    bp_dia: int
    t_core: float
    t_skin: float
    spo2: int
    resp: int
    sleep_hours: float
    mood: int
    kss: int
    light_k: int
    dose_msv_day: float
    dose_a_ugy_h: float
    dose_b_ugy_h: float
    pvt_ms: int
    glucose: int
    water_l: float
    caloric_pct: int
    gravity_g: float


class TelemetrySnapshot(BaseModel):
    crewId: str
    scenario: str
    timestamp: str
    label: str
    tone: Tone
    eva: Eva
    cardio: Cardio
    temp: Metric
    sleep: Sleep
    rad: Metric
    sans: Sans
    nutri: Nutri
    spo2: str
    risks: Risks
    triage: Triage
    readings: Readings
