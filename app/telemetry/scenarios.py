"""
Escenarios de simulación. Mismas claves que el frontend (src/features/dashboard/config/scenarios.js).

`base` son las lecturas de sensores de referencia; el simulador añade ruido alrededor de ellas.
El resto es contexto que no sale de un sensor: texto de triaje, notas clínicas, ubicación.
"""

from typing import Any

SCENARIOS: dict[str, dict[str, Any]] = {
    "nominal": {
        "label": "1. Nominal orbital",
        "tone": "ok",
        "location": "iss",
        "eva_caution_label": "REVISIÓN",
        "sans_note": "Rejilla Amsler: recta • Apto EVA",
        "base": {
            "hr": 67, "hrv": 56, "bp_sys": 117, "bp_dia": 75,
            "t_core": 36.7, "t_skin": 36.8, "spo2": 99, "resp": 14,
            "sleep_hours": 7.2, "mood": 4, "kss": 3, "light_k": 6500,
            "dose_msv_day": 0.70, "dose_a_ugy_h": 14.52, "dose_b_ugy_h": 17.41,
            "pvt_ms": 265, "glucose": 92, "water_l": 2.4, "caloric_pct": 96,
            "gravity_g": 0.0,
        },
        "triage": {
            "tag": "RADIACIÓN",
            "tone": "info",
            "title": "Exposición a radiación dentro de límites ALARA",
            "reason": "Motivo: la tasa de dosis actual en ISS JPM es nominal.",
            "bullets": [
                "Continuar operaciones nominales de la estación.",
                "Monitorear presupuesto acumulado de carrera (límite NASA 600 mSv).",
            ],
        },
    },
    "sensor": {
        "label": "2. Fallo sensor (>1°C)",
        "tone": "warn",
        "location": "iss",
        "eva_caution_label": "REVISIÓN",
        "sans_note": "Rejilla Amsler: recta • Apto EVA",
        "base": {
            "hr": 74, "hrv": 49, "bp_sys": 121, "bp_dia": 78,
            "t_core": 36.8, "t_skin": 38.1, "spo2": 98, "resp": 15,
            "sleep_hours": 7.0, "mood": 4, "kss": 4, "light_k": 6500,
            "dose_msv_day": 0.72, "dose_a_ugy_h": 14.80, "dose_b_ugy_h": 17.50,
            "pvt_ms": 278, "glucose": 95, "water_l": 2.3, "caloric_pct": 94,
            "gravity_g": 0.0,
        },
        "triage": {
            "tag": "SENSOR DUAL",
            "tone": "warn",
            "title": "Discrepancia de termistor redundante",
            "reason": "Motivo: el sensor cutáneo T2 diverge >1.0°C respecto al núcleo T1 sin taquicardia asociada.",
            "bullets": [
                "Aislar canal T2 y recalibrar nodo biométrico del traje.",
                "Validar temperatura timpánica manual antes de iniciar EVA.",
            ],
        },
    },
    "solar": {
        "label": "3. Tormenta solar + fiebre",
        "tone": "danger",
        "location": "iss",
        "eva_caution_label": "REVISIÓN",
        "sans_note": "Rejilla Amsler: leve ondulación",
        "base": {
            "hr": 112, "hrv": 28, "bp_sys": 138, "bp_dia": 88,
            "t_core": 38.6, "t_skin": 38.5, "spo2": 95, "resp": 22,
            "sleep_hours": 5.4, "mood": 2, "kss": 7, "light_k": 2700,
            "dose_msv_day": 4.85, "dose_a_ugy_h": 98.4, "dose_b_ugy_h": 112.0,
            "pvt_ms": 365, "glucose": 118, "water_l": 1.7, "caloric_pct": 88,
            "gravity_g": 0.0,
        },
        "triage": {
            "tag": "EMERGENCIA SPE",
            "tone": "danger",
            "title": "Evento de partículas solares + respuesta febril",
            "reason": "Motivo: flujo RadLab elevado acompañado de hipertermia y taquicardia.",
            "bullets": [
                "Trasladar tripulación al refugio blindado de polietileno (Módulo Zvezda / Columbus).",
                "Administrar protocolo antipirético + hidratación oral isotónica 500 mL/h.",
            ],
        },
    },
    "mars": {
        "label": "4. Cambio Marte 0.38g",
        "tone": "warn",
        "location": "mars",
        "eva_caution_label": "ADAPTACIÓN",
        "sans_note": "Rejilla Amsler: recta • Presión PIC baja",
        "base": {
            "hr": 88, "hrv": 41, "bp_sys": 104, "bp_dia": 68,
            "t_core": 37.0, "t_skin": 37.1, "spo2": 98, "resp": 16,
            "sleep_hours": 6.8, "mood": 3, "kss": 4, "light_k": 6500,
            "dose_msv_day": 1.15, "dose_a_ugy_h": 23.9, "dose_b_ugy_h": 23.9,
            "pvt_ms": 295, "glucose": 89, "water_l": 2.6, "caloric_pct": 93,
            "gravity_g": 0.38,
        },
        "triage": {
            "tag": "GRAVEDAD 0.38G",
            "tone": "warn",
            "title": "Redistribución ortostática en transición a 0.38g",
            "reason": "Motivo: descenso de presión arterial por retorno venoso hacia extremidades inferiores.",
            "bullets": [
                "Activar prendas de compresión graduada en miembros inferiores.",
                "Completar protocolo de carga hídrica y sodio antes de caminata superficial.",
            ],
        },
    },
}

SCENARIO_KEYS = list(SCENARIOS)
