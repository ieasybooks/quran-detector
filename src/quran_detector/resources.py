from __future__ import annotations

import xml.etree.ElementTree as ET
from contextlib import ExitStack
from dataclasses import dataclass
from importlib import resources

from .text import normalize_text, remove_tashkeel


@dataclass(frozen=True)
class QuranData:
    sura_names: list[str]
    q_orig: dict[str, dict[str, str]]
    q_norm: dict[str, dict[str, str]]
    stops: set[str]


def _build_verse_dicts(
    sura_names: list[str],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    q_orig: dict[str, dict[str, str]] = {name: {} for name in sura_names}
    q_norm: dict[str, dict[str, str]] = {name: {} for name in sura_names}
    return q_orig, q_norm


def load_stops(path: str) -> set[str]:
    stop_list: set[str] = set()
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            line = remove_tashkeel(line)
            line = normalize_text(line)
            stop_list.add(line)
    return stop_list


def load_sura_names(index_xml_path: str) -> list[str]:
    suras: list[str] = []
    root = ET.parse(index_xml_path).getroot()
    for sura in root.findall("sura"):
        suras.append(sura.get("name"))  # type: ignore[arg-type]
    return suras


def load_quran_simple(
    quran_simple_path: str,
    sura_names: list[str],
    q_orig: dict[str, dict[str, str]],
    q_norm: dict[str, dict[str, str]],
) -> None:
    besm = "بسم الله الرحمن الرحيم"
    with open(quran_simple_path, "r", encoding="utf-8") as file:
        line_no = 1
        for raw_line in file:
            line = raw_line.strip()
            parts = line.split("|")
            if len(parts) < 3:
                raise ValueError(f"Malformed quran-simple.txt line {line_no}: {raw_line!r}")
            line_no += 1
            sura_index = int(parts[0]) - 1
            sura_name = sura_names[sura_index]
            verse_number = parts[1]
            verse_text_orig = parts[2]

            verse_text_norm = normalize_text(verse_text_orig)
            verse_text_norm = remove_tashkeel(verse_text_norm)

            if (sura_index != 0) and verse_text_norm.startswith(besm):
                new_i = verse_text_norm.index(besm) + len(besm)
                verse_text_norm = verse_text_norm[new_i:]
                verse_text_orig = " ".join(verse_text_orig.split()[4:])

            q_orig[sura_name][verse_number] = verse_text_orig
            q_norm[sura_name][verse_number] = verse_text_norm


def load_bundled_data() -> QuranData:
    data_dir = resources.files("quran_detector") / "data"
    with ExitStack() as stack:
        quran_index = stack.enter_context(resources.as_file(data_dir / "quran-index.xml"))
        quran_simple = stack.enter_context(resources.as_file(data_dir / "quran-simple.txt"))
        nonterminals = stack.enter_context(resources.as_file(data_dir / "non-terminals.txt"))

        sura_names = load_sura_names(str(quran_index))
        q_orig, q_norm = _build_verse_dicts(sura_names)
        load_quran_simple(str(quran_simple), sura_names, q_orig, q_norm)
        stops = load_stops(str(nonterminals))
        return QuranData(sura_names=sura_names, q_orig=q_orig, q_norm=q_norm, stops=stops)


def load_data_from_paths(quran_simple_path: str, quran_index_path: str, nonterminals_path: str) -> QuranData:
    sura_names = load_sura_names(quran_index_path)
    q_orig, q_norm = _build_verse_dicts(sura_names)
    load_quran_simple(quran_simple_path, sura_names, q_orig, q_norm)
    stops = load_stops(nonterminals_path)
    return QuranData(sura_names=sura_names, q_orig=q_orig, q_norm=q_norm, stops=stops)
