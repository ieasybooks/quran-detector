# quran_matcher/models.py
from typing import Set


class Verse:
    """
    Represents a single verse in the Quran.

    Attributes:
        name: The sura name.
        number: The verse number.
    """

    def __init__(self, name: str, number: str):
        self.name = name
        self.number = number

    def __eq__(self, other):
        if isinstance(other, Verse):
            return (self.name == other.name) and (self.number == other.number)
        return False

    def __hash__(self):
        return hash((self.name, self.number))

    def __str__(self):
        return f"{self.name}:{self.number}"


class Term:
    """
    Represents a node in the trie structure used for verse matching.

    Attributes:
        text: The text of the term.
        terminal: Whether this term can terminate a verse.
        abs_terminal: Whether this term is the actual end of a verse.
        verses: A set of Verse objects where this term appears.
        children: A dictionary of subsequent term nodes.
    """

    def __init__(self):
        self.text: str = ""
        self.terminal: bool = False
        self.abs_terminal: bool = False
        self.verses: Set[Verse] = set()
        self.children: dict = {}

    def print(self, spaces=""):
        print(
            f"{spaces}{self.text} (terminal: {self.terminal}, abs_terminal: {self.abs_terminal})"
        )
        for verse in self.verses:
            print(f"{spaces}  {verse}")
        for child in self.children.values():
            child.print(spaces + "  ")


class MatchRecord:
    """
    Stores information about a matched verse in text.
    """

    def __init__(
        self,
        verse_text: str,
        sura_name: str,
        start_idx: int,
        end_idx: int,
        errors,
        start_in_text: int,
        end_in_text: int,
    ):
        self.verses = [verse_text]  # List of matched verse texts
        self.aya_name = sura_name
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.errors = [errors]
        self.start_in_text = start_in_text
        self.end_in_text = end_in_text

    def get_structured(self, json_format: bool = False):
        result = {
            "aya_name": self.aya_name,
            "verses": self.verses,
            "errors": self.errors,
            "startInText": self.start_in_text,
            "endInText": self.end_in_text,
            "aya_start": self.start_idx,
            "aya_end": self.end_idx,
        }
        if json_format:
            import json

            return json.dumps(result, ensure_ascii=False)
        return result

    def __str__(self):
        return f"{self.aya_name} {self.start_idx}-{self.end_idx}"

    def get_key(self) -> str:
        return self.aya_name + str(self.start_idx)

    def get_length(self) -> int:
        """Returns the total word count across the matched verses."""
        return sum(len(verse.split()) for verse in self.verses)

    def correct_errors(self, i: int, text: str) -> str:
        tokens = text.split()
        for error in self.errors[i]:
            err, corr, pos = error
            tokens[pos] = corr
        return " ".join(tokens)

    def get_extra_count(self, text: str, extra_list: list) -> int:
        count = 0
        for extra in extra_list:
            count += text.count(extra)
        return count

    def get_start_index(
        self, token1: str, token2: str, normalized_original: str
    ) -> int:
        tokens = normalized_original.split()
        count = tokens.count(token1)
        if count < 1:
            return -1
        if count == 1:
            return tokens.index(token1)
        offset = 0
        for _ in range(count):
            try:
                idx = tokens[offset:].index(token1) + offset
            except ValueError:
                return -1
            if idx + 1 < len(tokens) and tokens[idx + 1] == token2:
                return idx
            offset = idx + len(token1)
        return -1

    def get_error_number(self) -> int:
        return sum(len(e) for e in self.errors)

    def get_adjusted(
        self, start_idx: int, start_term: str, original_tokens: list
    ) -> int:
        while start_idx < len(original_tokens):
            current = original_tokens[start_idx].strip()
            if (
                current == start_term
                or ("و" + current == start_term)
                or ("و" + start_term == current)
            ):
                return start_idx
            start_idx += 1
        return -1

    def get_correct_span(
        self,
        record_idx: int,
        sura_name: str,
        verse_number: str,
        original_verses: dict,
        normalized_verses: dict,
    ) -> str:
        extra_list = ["ۖ", " ۗ", "ۚ", "ۗ"]
        orig = original_verses[sura_name][verse_number]
        in_text = self.verses[record_idx]
        orig_tokens = orig.split()
        orig_tokens = list(filter(lambda a: a != "ۛ", orig_tokens))
        in_text_tokens = in_text.split()
        if (len(orig_tokens) - self.get_extra_count(orig, extra_list)) > len(
            in_text_tokens
        ):
            normalized_orig = normalized_verses[sura_name][verse_number]
            start_idx = self.get_start_index(
                in_text_tokens[0], in_text_tokens[1], normalized_orig
            )
            if start_idx < 0:
                print("Error in get_correct_span")
                return orig
            st_str = "..." if start_idx > 0 else ""
            start_idx += self.get_extra_count(
                " ".join(orig_tokens[:start_idx]), extra_list
            )
            adj_idx = self.get_adjusted(start_idx, in_text_tokens[0], orig_tokens)
            if adj_idx > -1:
                start_idx = adj_idx
            orig_tokens = orig_tokens[start_idx:]
            l = len(in_text_tokens)
            result_tokens = orig_tokens[:l]
            extra_count = self.get_extra_count(" ".join(result_tokens), extra_list)
            for i in range(extra_count):
                if l + i < len(orig_tokens):
                    result_tokens.append(orig_tokens[l + i])
            end_str = "..." if len(orig_tokens) != len(result_tokens) else ""
            return st_str + " ".join(result_tokens) + end_str
        return orig

    def get_original_str(self, original_verses: dict, normalized_verses: dict) -> str:
        count = self.end_idx - self.start_idx + 1
        result_str = '"'
        end_str = f"({self.aya_name}:{self.start_idx}"
        if count > 1:
            end_str += f"-{self.end_idx}"
        end_str += ")"
        for i in range(count - 1):
            result_str += (
                self.get_correct_span(
                    i,
                    self.aya_name,
                    str(self.start_idx + i),
                    original_verses,
                    normalized_verses,
                )
                + "، "
            )
        result_str += self.get_correct_span(
            count - 1,
            self.aya_name,
            str(self.start_idx + count - 1),
            original_verses,
            normalized_verses,
        )
        result_str += '"' + end_str
        return result_str

    def get_concatenated(self) -> str:
        return " ".join(self.verses)
