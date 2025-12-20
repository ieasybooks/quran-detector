from __future__ import annotations

import re
from typing import Iterable

from .config import GLOBAL_DELIMITERS


def normalize_text(text: str) -> str:
    """
    Legacy-equivalent normalization:
    - Normalizes alif variants to ا
    - Converts ة -> ه and ى/ی -> ي
    - Normalizes some punctuation/whitespace and the Allah ligature
    """

    search = [
        "أ",
        "إ",
        "آ",
        "ٱ",
        "ة",
        "_",
        "-",
        "/",
        ".",
        "،",
        " و ",
        '"',
        "ـ",
        "'",
        "ى",
        "ی",
        "\\",
        "\n",
        "\t",
        "&quot;",
        "?",
        "؟",
        "!",
        "ﷲ",
    ]
    replace = [
        "ا",
        "ا",
        "ا",
        "ا",
        "ه",
        " ",
        " ",
        "",
        "",
        "",
        " و",
        "",
        "",
        "",
        "ي",
        "ي",
        "",
        " ",
        " ",
        " ",
        " ? ",
        " ؟ ",
        " ! ",
        "الله",
    ]

    for s, r in zip(search, replace, strict=True):
        text = text.replace(s, r)
    return text


_TASHKEEL_RE = re.compile(r"[\u0616-\u061A\u064B-\u0652\u06D6-\u06ED\u08F0-\u08F3\uFC5E-\uFC63\u0670]")


def remove_tashkeel(text: str) -> str:
    return re.sub(_TASHKEEL_RE, "", text)


def pad_symbols(in_text: str, symbol_list: Iterable[str] = ("۞", "۝")) -> str:
    for sym in symbol_list:
        in_text = in_text.replace(sym, " " + sym + " ")
    return in_text


def remove_delims(in_str: str, delims: str) -> str:
    parts = re.split(delims, in_str)
    for part in parts:
        part = part.strip()
        if len(part) > 0:
            return part
    return ""


def normalize_term(term: str, delims: str = GLOBAL_DELIMITERS) -> str:
    term = remove_delims(term, delims)
    if len(term) < 1:
        return ""
    term = remove_tashkeel(term)
    term = normalize_text(term)
    return term.strip()


def get_next_valid_term(terms: list[str], delims: str, i: int) -> tuple[bool, str, int]:
    length = len(terms)
    while i < length:
        normalized = normalize_term(terms[i], delims)
        if len(normalized) > 1:
            return True, normalized, i
        i += 1
    return False, "", i

