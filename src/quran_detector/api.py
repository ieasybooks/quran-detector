from __future__ import annotations

from .config import Settings
from .engine import Engine

_ENGINE: Engine | None = None


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = Engine.from_bundled_data()
    return _ENGINE


def detect(text: str, settings: Settings = Settings()) -> list[dict]:
    return get_engine().detect(text, settings=settings)


def annotate(text: str, settings: Settings = Settings()) -> str:
    return get_engine().annotate(text, settings=settings)

