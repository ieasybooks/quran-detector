# quran_matcher/data_loader.py
import codecs
import xml.etree.ElementTree as ET

from quran_detector.models import Term, Verse
from quran_detector.utils import GLOBAL_DELIMITERS, normalize_text, remove_tashkeel


def build_sura_index(index_file: str) -> list:
    """
    Parses the Quran index XML file and returns a list of sura names.
    """
    suras = []
    root = ET.parse(index_file).getroot()
    for sura_elem in root.findall("sura"):
        suras.append(sura_elem.get("name"))
    return suras


def build_verse_dicts(sura_names: list) -> dict:
    """
    Initializes a dictionary for verses keyed by sura name.
    """
    return {sura: {} for sura in sura_names}


def add_verse(
    verse_text: str,
    verse_info: Verse,
    current_node: dict,
    strict: bool,
    ambig_set: set,
    min_length: int,
    stops: set,
):
    """
    Adds a verse into a trie-like data structure.
    If the verse is a single word, it is added to the ambiguity set.
    Also recursively adds sub-phrases of the verse.
    """
    original_node = current_node
    words = verse_text.split()
    num_words = len(words)
    if num_words == 1:
        ambig_set.add(verse_text.strip())

    for i, word in enumerate(words, start=1):
        if word in current_node:
            term_node = current_node[word]
            current_node = term_node.children
        else:
            term_node = Term()
            term_node.text = word
            current_node[word] = term_node
            current_node = term_node.children

        if i >= min_length:
            if strict:
                if word not in stops:
                    term_node.terminal = True
            else:
                term_node.terminal = True
            term_node.verses.add(verse_info)
        if i == num_words:
            term_node.abs_terminal = True
            term_node.verses.add(verse_info)

    if (num_words - min_length) > 0:
        # Recursively add the verse starting from the next word
        next_index = verse_text.find(" ") + 1
        add_verse(
            verse_text[next_index:],
            verse_info,
            original_node,
            strict,
            ambig_set,
            min_length,
            stops,
        )


def add_ayat(
    filename: str,
    suras: list,
    all_nodes: dict,
    q_orig: dict,
    q_norm: dict,
    ambig_set: set,
    min_length: int,
    stops: set,
):
    """
    Reads verses from a file and loads them into internal data structures.
    Expected format per line: <sura_num>|<verse_num>|<verse_text>
    """
    besm = "بسم الله الرحمن الرحيم"
    with codecs.open(filename, "r", "utf-8") as f:
        line_no = 1
        for line in f:
            line = line.strip()
            parts = line.split("|")
            if len(parts) < 3:
                print(f"Error in line: {line_no}")
                break
            line_no += 1
            sura_index = int(parts[0]) - 1
            sura_name = suras[sura_index]
            verse_number = parts[1]
            verse_text = parts[2]
            original_text = verse_text

            verse_text = normalize_text(verse_text)
            verse_text = remove_tashkeel(verse_text)
            if sura_index != 0 and verse_text.startswith(besm):
                offset = verse_text.index(besm) + len(besm)
                verse_text = verse_text[offset:]
                original_text = " ".join(original_text.split()[4:])

            q_orig[sura_name][verse_number] = original_text
            q_norm[sura_name][verse_number] = verse_text
            verse_obj = Verse(sura_name, verse_number)
            add_verse(
                verse_text, verse_obj, all_nodes, True, ambig_set, min_length, stops
            )
