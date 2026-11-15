"""
Convierte lecturas crudas de sensores en el snapshot que consume el panel del frontend.
Las insignias, porcentajes y riesgos salen de reglas sobre las lecturas, no son fijos.
Tonos: ok | info | warn | danger
"""

from typing import Any

from app.telemetry.scenarios import SCENARIOS

TONE_RANK = {"ok": 0, "info": 0, "warn": 1, "danger": 2}


def _clamp(value: float, lo: float = 0, hi: float = 100) -> int:
    return int(round(min(hi, max(lo, value))))


def _risk(pct: int) -> list[Any]:
    if pct < 35:
        return [pct, "BAJO", "ok"]
    if pct < 60:
        return [pct, "MODERADO", "warn"]
    if pct < 80:
        return [pct, "ALTO", "danger"]
    return [pct, "CRÍTICO", "danger"]


def _cardio(r: dict, location: str) -> dict:
    if r["hr"] > 100:
        badge = ["TAQUICARDIA", "danger"]
    elif r["hr"] < 50:
        badge = ["BRADICARDIA", "warn"]
    elif location == "mars":
        badge = [f"CARGA {r['gravity_g']}G", "warn"]
    elif r["hrv"] < 35:
        badge = ["VFC BAJA", "warn"]
    else:
        badge = ["NOMINAL", "ok"]
    pct = 100 - max(0, r["hr"] - 65) * 0.9 - max(0, 55 - r["hrv"]) * 0.6 - max(0, 110 - r["bp_sys"]) * 1.2
    return {
        "hr": r["hr"],
        "hrv": r["hrv"],
        "badge": badge,
        "sub": f"PA: {r['bp_sys']}/{r['bp_dia']} mmHg • VFC: {r['hrv']} ms",
        "pct": _clamp(pct, 30),
    }


def _temp(r: dict) -> dict:
    delta = abs(r["t_core"] - r["t_skin"])
    if delta > 1.0:
        badge = ["DERIVA Δ>1°C", "warn"]
    elif r["t_core"] >= 38.0:
        badge = ["FIEBRE ALERTA", "danger"]
    elif r["t_core"] >= 37.5:
        badge = ["FEBRÍCULA", "warn"]
    else:
        badge = ["VERIFICADO", "ok"]
    pct = 100 - max(0, r["t_core"] - 37.0) * 30 - max(0, delta - 0.3) * 30
    return {
        # Con deriva se muestra el núcleo (T1), que es el canal fiable
        "value": f"{r['t_core'] if delta > 1.0 else (r['t_core'] + r['t_skin']) / 2:.1f}",
        "badge": badge,
        "sub": f"T1: {r['t_core']:.1f}° | T2: {r['t_skin']:.1f}° (Δ {delta:.1f}°C)",
        "pct": _clamp(pct, 30),
    }


def _sleep(r: dict) -> dict:
    day = r["light_k"] >= 5000
    return {
        "hours": r["sleep_hours"],
        "badge": [f"{int(r['light_k'])}K {'DÍA' if day else 'REPOSO'}", "info" if day else "warn"],
        "sub": f"Ánimo: {int(r['mood'])}/5 • Somnolencia KSS: {int(r['kss'])}/9",
        # Misma fórmula que el slider del frontend
        "pct": _clamp(r["sleep_hours"] / 8 * 100, 45),
    }


def _rad(r: dict, location: str) -> dict:
    dose = r["dose_msv_day"]
    if dose >= 2.0:
        badge = ["TORMENTA SPE", "danger"]
    elif dose >= 1.0:
        badge = ["SUPERFICIE" if location == "mars" else "DOSIS ELEVADA", "warn"]
    else:
        badge = ["ALARA OK", "ok"]
    if location == "mars":
        sub = f"GCR Marte: {r['dose_a_ugy_h']:.1f} µGy/h • Blindaje regolito"
    else:
        sub = f"JPM: {r['dose_a_ugy_h']:.2f} µGy/h vs Col: {r['dose_b_ugy_h']:.2f} µGy/h"
    return {"value": f"{dose:.2f}", "badge": badge, "sub": sub, "pct": _clamp(dose / 5.6 * 100)}


def _nutri(r: dict) -> dict:
    stressed = r["glucose"] > 110 or r["water_l"] < 2.0
    extra = "Electrolitos bajos" if stressed else f"Calórico: {int(r['caloric_pct'])}%"
    pct = 100 - abs(r["glucose"] - 90) - max(0, 2.4 - r["water_l"]) * 30
    return {
        "gluc": r["glucose"],
        "water": f"{r['water_l']:.1f}L",
        "badge": ["ESTRÉS METAB.", "warn"] if stressed else ["BALANCEADO", "ok"],
        "sub": f"Hidratación: {r['water_l']:.1f} L/d • {extra}",
        "pct": _clamp(pct, 30),
    }


def _risks(r: dict) -> dict:
    neuro = (r["pvt_ms"] - 230) * 0.3 + r["kss"] * 2
    cardio = (
        10
        + max(0, r["hr"] - 60) * 0.8
        + max(0, 55 - r["hrv"]) * 0.6
        + max(0, 110 - r["bp_sys"]) * 1.5
        + max(0, r["bp_sys"] - 130) * 1.0
    )
    return {
        "rad": _risk(_clamp(r["dose_msv_day"] / 5.6 * 100)),
        "neuro": _risk(_clamp(neuro)),
        "cardio": _risk(_clamp(cardio)),
    }


def build_snapshot(crew_id: str, scenario: str, readings: dict, timestamp: str) -> dict:
    ctx = SCENARIOS[scenario]
    location = ctx["location"]

    cardio = _cardio(readings, location)
    temp = _temp(readings)
    sleep = _sleep(readings)
    rad = _rad(readings, location)
    nutri = _nutri(readings)
    risks = _risks(readings)

    tones = [c["badge"][1] for c in (cardio, temp, rad, nutri)] + [v[2] for v in risks.values()]
    worst = max(tones, key=TONE_RANK.__getitem__)
    eva_pct = _clamp(
        (cardio["pct"] + temp["pct"] + sleep["pct"] + nutri["pct"] + (100 - max(v[0] for v in risks.values())))
        / 5
    )
    eva_label = {"danger": "NO APTO EVA", "warn": ctx["eva_caution_label"]}.get(worst, "APTO EVA")

    return {
        "crewId": crew_id,
        "scenario": scenario,
        "timestamp": timestamp,
        "label": ctx["label"],
        "tone": ctx["tone"],
        "eva": {"label": f"{eva_label} • {eva_pct}%", "tone": "ok" if worst == "info" else worst},
        "cardio": cardio,
        "temp": temp,
        "sleep": sleep,
        "rad": rad,
        "sans": {"pvt": readings["pvt_ms"], "sub": ctx["sans_note"]},
        "nutri": nutri,
        "spo2": f"SPO2 {readings['spo2']}% • {readings['resp']} resp/m",
        "risks": risks,
        "triage": ctx["triage"],
        "readings": readings,
    }
