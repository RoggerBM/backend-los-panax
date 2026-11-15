import os
from dataclasses import dataclass, field


def _load_dotenv(path: str = ".env") -> None:
    """Carga un .env sencillo (CLAVE=valor) sin dependencias extra. Las variables ya definidas ganan."""
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def _split(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    cors_origins: list[str] = field(
        default_factory=lambda: _split(
            os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        )
    )
    tick_seconds: float = float(os.getenv("TICK_SECONDS", "1.0"))


settings = Settings()
