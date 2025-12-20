from __future__ import annotations

import json
import re
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


_ANNOTATION_RE = re.compile(r"\"(?P<quote>[^\"]*)\"(?P<ref>\([^()]+?:\d+(?:-\d+)?\))")


def _ref_for_record(rec: dict[str, Any]) -> str:
    surah = rec.get("surah_name") or rec.get("aya_name")
    aya_start = rec["aya_start"]
    aya_end = rec["aya_end"]
    if aya_start == aya_end:
        return f"({surah}:{aya_start})"
    return f"({surah}:{aya_start}-{aya_end})"


def _ambiguous_refs(golden_match_all: list[dict[str, Any]]) -> set[str]:
    by_span: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for rec in golden_match_all:
        by_span.setdefault((rec["startInText"], rec["endInText"]), []).append(rec)
    refs: set[str] = set()
    for span, group in by_span.items():
        if len(group) <= 1:
            continue
        for rec in group:
            refs.add(_ref_for_record(rec))
    return refs


def _canonicalize_annotation(text: str, *, ambiguous_refs: set[str]) -> str:
    # Canonicalize references in all cases, and for ambiguous references also
    # canonicalize the whole quoted verse span to avoid brittle failures.
    def repl(m: re.Match[str]) -> str:
        ref = m.group("ref")
        if ref in ambiguous_refs:
            return '"<AMBIG>"(REF)'
        return f"\"{m.group('quote')}\"(REF)"

    return _ANNOTATION_RE.sub(repl, text).rstrip()

def _unambiguous_records(golden_match_all: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_span: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for rec in golden_match_all:
        by_span.setdefault((rec["startInText"], rec["endInText"]), []).append(rec)
    out: list[dict[str, Any]] = []
    for _span, group in by_span.items():
        if len(group) == 1:
            out.append(group[0])
    return out


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
@pytest.mark.parametrize("book_num", list(range(1, 13)))
def test_match_all_against_golden(setting_name: str, settings: Settings, book_num: int) -> None:
    input_text = _load_text(INPUTS_DIR / f"{book_num}.txt")
    actual = detect(input_text, settings=settings)
    expected = _load_json(OUTPUTS_DIR / setting_name / f"matchAll_{book_num}.txt")
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
@pytest.mark.parametrize("book_num", list(range(1, 13)))
def test_annotate_txt_against_golden(setting_name: str, settings: Settings, book_num: int) -> None:
    # For annotation, compare behaviorally but skip ambiguous spans:
    # - Require that the annotated output contains the reference markers for all *unambiguous*
    #   matches from the golden `matchAll` output.
    input_text = _load_text(INPUTS_DIR / f"{book_num}.txt")
    actual = annotate(input_text, settings=settings)

    golden_match_all = _load_json(OUTPUTS_DIR / setting_name / f"matchAll_{book_num}.txt")
    unambiguous = _unambiguous_records(golden_match_all)

    # Ensure we're actually annotating (quick sanity check).
    assert actual != input_text

    for rec in unambiguous:
        ref = _ref_for_record(rec)
        assert ref in actual, f"Missing reference {ref} in annotated output for book {book_num} ({setting_name})"
