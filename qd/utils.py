# quran_matcher/utils.py
import re

# Global delimiter pattern for splitting text
GLOBAL_DELIMITERS = r"#|،|\.|{|}|\n|؟|!|\(|\)|﴿|﴾|۞|۝|\*|-|\+|\:|…"


def normalize_text(text: str) -> str:
    """
    Normalizes Arabic text by converting variant forms of letters to a standard form,
    replacing specific punctuation and whitespace.
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
    for s, r in zip(search, replace):
        text = text.replace(s, r)
    return text


def pad_symbols(text: str, symbols: list = ["۞", "۝"]) -> str:
    """Inserts spaces around specific symbols."""
    for sym in symbols:
        text = text.replace(sym, f" {sym} ")
    return text


# Precompiled regular expression to remove Tashkeel (diacritical marks)
TASHKEEL_PATTERN = re.compile(
    r"[\u0616-\u061A\u064B-\u0652\u06D6-\u06ED\u08F0-\u08F3\uFC5E-\uFC63\u0670]"
)


def remove_tashkeel(text: str) -> str:
    """Removes Arabic Tashkeel from the input text."""
    return re.sub(TASHKEEL_PATTERN, "", text)


def remove_delimiters(text: str, delimiters: str = GLOBAL_DELIMITERS) -> str:
    """
    Splits the text using delimiters and returns the first non-empty segment.
    """
    parts = re.split(delimiters, text)
    for part in parts:
        part = part.strip()
        if part:
            return part
    return ""


def normalize_term(term_text: str, delimiters: str = GLOBAL_DELIMITERS) -> str:
    """
    Normalizes a term by removing delimiters, diacritical marks, and then applying text normalization.
    """
    term_text = remove_delimiters(term_text, delimiters)
    if not term_text:
        return ""
    term_text = remove_tashkeel(term_text)
    term_text = normalize_text(term_text)
    return term_text.strip()


def get_next_valid_term(terms: list, delimiters: str, index: int):
    """
    Given a list of terms and an index, returns a tuple (found, normalized_term, new_index).
    A valid term is one whose normalized version has length > 1.
    """
    while index < len(terms):
        normalized = normalize_term(terms[index], delimiters)
        if len(normalized) > 1:
            return True, normalized, index
        index += 1
    return False, "", index
