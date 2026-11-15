"""
Simulador de sensores. Cada (tripulante, escenario) tiene su propio estado que deriva
con un paseo aleatorio que vuelve hacia la lectura base, así los valores se mueven
de forma creíble sin dispararse.
"""

import hashlib
import random
import threading

from app.telemetry.scenarios import SCENARIOS

# sensor: (desviación del ruido por tick, decimales, mínimo, máximo)
SENSOR_SPECS: dict[str, tuple[float, int, float, float]] = {
    "hr": (1.6, 0, 35, 190),
    "hrv": (1.2, 0, 10, 120),
    "bp_sys": (1.2, 0, 80, 190),
    "bp_dia": (0.9, 0, 45, 120),
    "t_core": (0.03, 1, 34.0, 42.0),
    "t_skin": (0.04, 1, 30.0, 42.0),
    "spo2": (0.35, 0, 85, 100),
    "resp": (0.5, 0, 8, 35),
    "dose_msv_day": (0.03, 2, 0.0, 20.0),
    "dose_a_ugy_h": (0.5, 2, 0.0, 500.0),
    "dose_b_ugy_h": (0.5, 2, 0.0, 500.0),
    "pvt_ms": (4.0, 0, 180, 800),
    "glucose": (0.8, 0, 50, 250),
    "water_l": (0.0, 1, 0.0, 6.0),
    "caloric_pct": (0.0, 0, 0, 150),
}

# Variación individual de cada tripulante respecto a la base (se fija por hash del id)
PERSONAL_OFFSETS: dict[str, float] = {"hr": 4, "hrv": 5, "bp_sys": 4, "pvt_ms": 15, "glucose": 4}

MEAN_REVERSION = 0.25
MAX_STATES = 500


def _crew_seed(crew_id: str) -> int:
    return int(hashlib.sha256(crew_id.encode()).hexdigest()[:8], 16)


class SensorSimulator:
    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self._states: dict[tuple[str, str], dict[str, float]] = {}
        self._lock = threading.Lock()

    def _baseline(self, crew_id: str, scenario: str) -> dict[str, float]:
        base = dict(SCENARIOS[scenario]["base"])
        personal = random.Random(_crew_seed(crew_id))
        for key, spread in PERSONAL_OFFSETS.items():
            base[key] += personal.uniform(-spread, spread)
        return base

    def read(self, crew_id: str, scenario: str) -> dict[str, float]:
        """Avanza un tick y devuelve las lecturas actuales del tripulante."""
        key = (crew_id, scenario)
        with self._lock:
            baseline = self._baseline(crew_id, scenario)
            state = self._states.get(key)
            if state is None:
                if len(self._states) >= MAX_STATES:
                    self._states.pop(next(iter(self._states)))
                state = dict(baseline)
                self._states[key] = state

            for name, (sigma, _, lo, hi) in SENSOR_SPECS.items():
                drift = (baseline[name] - state[name]) * MEAN_REVERSION
                state[name] = min(hi, max(lo, state[name] + drift + self._rng.gauss(0, sigma)))

            return {name: self._round(name, value) for name, value in state.items()}

    @staticmethod
    def _round(name: str, value: float) -> float:
        decimals = SENSOR_SPECS.get(name, (0, 2, 0, 0))[1]
        return int(round(value)) if decimals == 0 else round(value, decimals)


simulator = SensorSimulator()
