from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from quran_detector import Settings, annotate, detect


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
INPUTS_DIR = WORKSPACE_ROOT / "tests" / "inputs"
OUTPUTS_DIR = WORKSPACE_ROOT / "tests" / "outputs"


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonicalize_match_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def norm_value(value: Any) -> Any:
        if isinstance(value, tuple):
            return [norm_value(v) for v in value]
        if isinstance(value, list):
            return [norm_value(v) for v in value]
        if isinstance(value, dict):
            return {k: norm_value(v) for k, v in value.items()}
        return value

    normalized: list[dict[str, Any]] = []
    for rec in records:
        rec = dict(rec)
        if "aya_name" in rec and "surah_name" not in rec:
            rec["surah_name"] = rec.pop("aya_name")
        normalized.append(norm_value(rec))

    def key(rec: dict[str, Any]) -> tuple[Any, ...]:
        return (
            rec.get("startInText"),
            rec.get("endInText"),
            rec.get("surah_name"),
            rec.get("aya_start"),
            rec.get("aya_end"),
        )

    return sorted(normalized, key=key)


@pytest.mark.parametrize(
    "setting_name,settings",
    [
        ("default", Settings()),
        ("find_errors_false", Settings(find_errors=False)),
        ("find_missing_false", Settings(find_missing=False)),
        ("high_error_tolerance", Settings(allowed_error_pct=0.5)),
        ("high_min_match", Settings(min_match=5)),
    ],
)
def test_match_all_against_golden(setting_name: str, settings: Settings) -> None:
    for i in range(1, 13):
        input_text = _load_text(INPUTS_DIR / f"{i}.txt")
        actual = detect(input_text, settings=settings)
        expected = _load_json(OUTPUTS_DIR / setting_name / f"matchAll_{i}.txt")
        assert _canonicalize_match_records(actual) == _canonicalize_match_records(expected)


@pytest.mark.parametrize(
    "setting_name,settings",
    [
        ("default", Settings()),
        ("find_errors_false", Settings(find_errors=False)),
        ("find_missing_false", Settings(find_missing=False)),
        ("high_error_tolerance", Settings(allowed_error_pct=0.5)),
        ("high_min_match", Settings(min_match=5)),
    ],
)
def test_annotate_txt_against_golden(setting_name: str, settings: Settings) -> None:
    for i in range(1, 13):
        input_text = _load_text(INPUTS_DIR / f"{i}.txt")
        actual = annotate(input_text, settings=settings)
        expected = _load_json(OUTPUTS_DIR / setting_name / f"annotateTxt_{i}.txt")
        assert actual.rstrip() == expected.rstrip()

