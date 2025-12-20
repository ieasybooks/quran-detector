from __future__ import annotations

from dataclasses import dataclass

GLOBAL_DELIMITERS = r"#|،|\.|{|}|\n|؟|!|\(|\)|﴿|﴾|۞|۝|\*|-|\+|\:|…"


@dataclass(frozen=True)
class Settings:
    find_errors: bool = True
    find_missing: bool = True
    allowed_error_pct: float = 0.25
    min_match: int = 3
    delimiters: str = GLOBAL_DELIMITERS

