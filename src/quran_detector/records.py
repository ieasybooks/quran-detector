from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .config import GLOBAL_DELIMITERS
from .text import normalize_term

logger = logging.getLogger(__name__)


@dataclass
class MatchRecord:
    verses: list[str]
    surah_name: str
    aya_start: int
    aya_end: int
    errors: list[list]
    start_in_text: int
    end_in_text: int

    def key(self) -> str:
        return self.surah_name + str(self.aya_start)

    def get_len(self) -> int:
        return sum(len(v.split()) for v in self.verses)

    def get_err_num(self) -> int:
        return sum(len(e) for e in self.errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "surah_name": self.surah_name,
            "verses": self.verses,
            "errors": self.errors,
            "startInText": self.start_in_text,
            "endInText": self.end_in_text,
            "aya_start": self.aya_start,
            "aya_end": self.aya_end,
        }

    def _get_extra_cnt(self, in_list: list[str] | str, extra_list: list[str]) -> int:
        cnt = 0
        for item in extra_list:
            cnt += in_list.count(item)
        return cnt

    def _get_start_index(self, t1: str, t2: str, n_orig: str) -> int:
        n_tokens = n_orig.split()
        cnt = n_tokens.count(t1)
        if cnt < 1:
            return -1
        if cnt == 1:
            return n_tokens.index(t1)
        offset = 0
        for _ in range(cnt):
            i1 = n_tokens[offset:].index(t1) + offset
            if (i1 + 1) < len(n_tokens) and n_tokens[i1 + 1] == t2:
                return i1
            offset = i1 + 1
        return -1

    def _get_adjusted(self, start_idx: int, start_term: str, orig_tokens: list[str]) -> int:
        length = len(orig_tokens)
        while start_idx < length:
            curr = normalize_term(orig_tokens[start_idx], GLOBAL_DELIMITERS)
            if (curr == start_term) or ("و" + curr == start_term) or ("و" + start_term == curr):
                return start_idx
            start_idx += 1
        return -1

    def _get_correct_span(
        self,
        record_idx: int,
        surah_name: str,
        verse_number: str,
        orig_verses: dict[str, dict[str, str]],
        norm_verses: dict[str, dict[str, str]],
    ) -> str:
        extra_list = ["ۖ", " ۗ", "ۚ", "ۗ"]
        orig = orig_verses[surah_name][verse_number]
        in_txt = self.verses[record_idx]
        orig_tokens = orig.split()
        orig_tokens = list(filter(lambda a: a != "ۛ", orig_tokens))
        in_text_tokens = in_txt.split()
        if (len(orig_tokens) - self._get_extra_cnt(orig, extra_list)) > len(in_text_tokens):
            n_orig = norm_verses[surah_name][verse_number]
            start_idx = self._get_start_index(in_text_tokens[0], in_text_tokens[1], n_orig)
            if start_idx < 0:
                # Preserve legacy fallback behavior but avoid noisy stdout in library usage.
                logger.debug("getCorrectSpan alignment failed for %s:%s", surah_name, verse_number)
                return orig
            st_str = "..." if start_idx > 0 else ""
            start_idx = start_idx + self._get_extra_cnt(orig_tokens[0:start_idx], extra_list)
            adj_idx = self._get_adjusted(start_idx, in_text_tokens[0], orig_tokens)
            if adj_idx > -1:
                start_idx = adj_idx
            orig_tokens = orig_tokens[start_idx:]
            length = len(in_text_tokens)
            result = orig_tokens[:length]
            extra = self._get_extra_cnt(result, extra_list)
            for i in range(extra):
                result.append(orig_tokens[length + i])
            end_str = "..."
            if len(orig_tokens) == len(result):
                end_str = ""
            return st_str + " ".join(result) + end_str
        return orig

    def get_orig_str(self, orig_verses: dict[str, dict[str, str]], norm_verses: dict[str, dict[str, str]]) -> str:
        v_count = self.aya_end - self.aya_start + 1
        out = '"'
        end_str = "(" + self.surah_name + ":" + str(self.aya_start)
        if v_count > 1:
            end_str = end_str + "-" + str(self.aya_end)
        end_str = end_str + ")"
        for i in range(v_count - 1):
            out = (
                out
                + self._get_correct_span(i, self.surah_name, str(self.aya_start + i), orig_verses, norm_verses)
                + "، "
            )
        out = (
            out
            + self._get_correct_span(
                v_count - 1,
                self.surah_name,
                str(self.aya_start + v_count - 1),
                orig_verses,
                norm_verses,
            )
            + '"'
            + end_str
        )
        return out
