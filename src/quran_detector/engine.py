from __future__ import annotations

from dataclasses import dataclass, field

import Levenshtein

from .config import Settings
from .records import MatchRecord
from .resources import QuranData, load_bundled_data, load_data_from_paths
from .text import get_next_valid_term, normalize_term, pad_symbols
from .trie import Node, VerseRef, add_verse


def _get_stop_percentage(in_str: str, stops: set[str]) -> float:
    terms = in_str.split()
    str_len = len(terms)
    num = 0
    for t in terms:
        if t in stops:
            num += 1
        elif t.startswith("و") and t[1:] in stops:
            num += 1
    return num / str_len


@dataclass
class Engine:
    trie: dict[str, Node]
    q_orig: dict[str, dict[str, str]]
    q_norm: dict[str, dict[str, str]]
    stops: set[str]
    ambig: set[str]
    surah_rank: dict[str, int]
    min_len_build: int = 3

    besm: str = "بسم الله الرحمن الرحيم"
    stop_verses: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.stop_verses:
            self.stop_verses = [self.besm, "الله ونعم الوكيل", "الحمد لله"]

    @classmethod
    def from_bundled_data(cls) -> "Engine":
        data = load_bundled_data()
        return cls._from_data(data)

    @classmethod
    def from_paths(cls, quran_simple_path: str, quran_index_path: str, nonterminals_path: str) -> "Engine":
        data = load_data_from_paths(quran_simple_path, quran_index_path, nonterminals_path)
        return cls._from_data(data)

    @classmethod
    def _from_data(cls, data: QuranData) -> "Engine":
        trie: dict[str, Node] = {}
        ambig: set[str] = set()
        for surah_name, verses in data.q_norm.items():
            for verse_number, verse_text_norm in verses.items():
                ref = VerseRef(surah_name, verse_number)
                add_verse(
                    verse_text_norm,
                    ref,
                    trie,
                    strict=True,
                    ambig=ambig,
                    min_len=3,
                    stops=data.stops,
                )
        surah_rank = {name: idx for idx, name in enumerate(data.sura_names, start=1)}
        return cls(
            trie=trie,
            q_orig=data.q_orig,
            q_norm=data.q_norm,
            stops=data.stops,
            ambig=ambig,
            surah_rank=surah_rank,
        )

    def _surah_sort_key(self, name: str) -> int:
        # Higher surah number first (more deterministic for ambiguous matches).
        return self.surah_rank.get(name, 0)

    def _match_with_error(self, in_str: str, curr: dict[str, Node]) -> str | int:
        for t in curr:
            if Levenshtein.distance(in_str, t) == 1 and (t not in self.ambig):
                return t
        return 0

    def _find_in_children(self, in_str: str, curr: dict[str, Node]) -> str | int:
        for c in curr:
            if in_str in curr[c].children:
                return c
        return 0

    def _match_detect_missing_verse(
        self, terms: list[str], curr: dict[str, Node], start_idx: int, delims: str, find_err: bool
    ) -> tuple[set[VerseRef], str, list[list], int]:
        errors: list[list] = []
        errs: list[list] = []
        result: set[VerseRef] = set()
        r_str = ""
        r_str_final = ""
        result_final: set[VerseRef] = set()
        wd_counter, end_idx = start_idx - 1, 0

        for t in terms[start_idx:]:
            wd_counter += 1
            t = normalize_term(t, delims)
            if len(t) < 1:
                continue
            e: str | int = 0
            if (t not in curr) and find_err:
                e = self._match_with_error(t, curr)
                if isinstance(e, str):
                    errors.append([t, e, wd_counter])
                    t = e
            if t in curr:
                r_str = r_str + t + " "
                result = curr[t].verses
                if curr[t].terminal or curr[t].abs_terminal:
                    r_str_final = r_str
                    result_final = result
                    errs = errors
                    end_idx = wd_counter + 1
                curr = curr[t].children
            else:
                missing = self._find_in_children(t, curr)
                if missing:
                    r_str = r_str + str(missing) + " " + t + " "
                    temp_cur = curr[str(missing)].children
                    result = temp_cur[t].verses
                    errors.append([t, str(missing) + " " + t, wd_counter])
                    if len(r_str.split()) > self.min_len_build and (temp_cur[t].terminal or temp_cur[t].abs_terminal):
                        r_str_final = r_str
                        result_final = result
                        errs = errors
                        end_idx = wd_counter + 1
                    curr = temp_cur[t].children
                else:
                    next_exists, next_term, indx = get_next_valid_term(terms, delims, wd_counter + 1)
                    if not next_exists:
                        return result_final, r_str_final.strip(), errs, end_idx
                    valid = self._find_in_children(next_term, curr)
                    if valid:
                        errors.append([t, valid, wd_counter])
                        r_str = r_str + t + " "
                        curr = curr[str(valid)].children
                        end_idx = indx + 1
                    else:
                        return result_final, r_str_final.strip(), errs, end_idx
        return result_final, r_str_final.strip(), errs, end_idx

    def _match_single_verse(
        self, terms: list[str], curr: dict[str, Node], start_idx: int, delims: str, find_err: bool
    ) -> tuple[set[VerseRef], str, list[list], int]:
        errors: list[list] = []
        errs: list[list] = []
        result: set[VerseRef] = set()
        r_str = ""
        r_str_final = ""
        result_final: set[VerseRef] = set()
        wd_counter, end_idx = start_idx - 1, 0

        for t in terms[start_idx:]:
            wd_counter += 1
            t = normalize_term(t, delims)
            if len(t) < 1:
                continue
            e: str | int = 0
            if (t not in curr) and find_err:
                e = self._match_with_error(t, curr)
                if isinstance(e, str):
                    errors.append([t, e, wd_counter])
                    t = e
            if t in curr:
                r_str = r_str + t + " "
                result = curr[t].verses
                if curr[t].terminal or curr[t].abs_terminal:
                    r_str_final = r_str
                    result_final = result
                    errs = errors
                    end_idx = wd_counter + 1
                curr = curr[t].children
            else:
                return result_final, r_str_final.strip(), errs, end_idx
        return result_final, r_str_final.strip(), errs, end_idx

    def _match_long_verse(
        self, terms: list[str], curr: dict[str, Node], start_idx: int, delims: str, find_err: bool
    ) -> tuple[set[VerseRef], str, list[list], int]:
        if not find_err:
            return self._match_single_verse(terms, curr, start_idx, delims, find_err)

        term = terms[start_idx]
        first = normalize_term(term, delims)
        e = "و" + first
        found = False
        rf2: set[VerseRef] = set()
        rs2 = ""
        err2: list[list] = []
        end2: int = 0

        if first.startswith("و") and first[1:] in curr:
            found = True
        if len(terms[start_idx:]) > 0 and (e not in curr) and (not found):
            return self._match_single_verse(terms, curr, start_idx, delims, find_err)

        rf1, rs1, err1, end1 = self._match_single_verse(terms, curr, start_idx, delims, find_err)
        if not found:
            terms[start_idx] = "و" + first
            rf2, rs2, err2, end2 = self._match_single_verse(terms, curr, start_idx, delims, find_err)
            err2.append([first, terms[start_idx], start_idx])
            terms[start_idx] = term
        else:
            terms[start_idx] = first[1:]
            rf2, rs2, err2, end2 = self._match_single_verse(terms, curr, start_idx, delims, find_err)
            err2.append([first, first[1:], start_idx])
            terms[start_idx] = term

        if len(rs2) > len(rs1):
            return rf2, rs2, err2, end2
        return rf1, rs1, err1, end1

    def _match_long_verse_detect_missing(
        self, terms: list[str], curr: dict[str, Node], start_idx: int, delims: str, find_err: bool
    ) -> tuple[set[VerseRef], str, list[list], int]:
        term = terms[start_idx]
        first = normalize_term(term, delims)
        e = "و" + first
        found = False
        rf2: set[VerseRef] = set()
        rs2 = ""
        err2: list[list] = []
        end2: int = 0

        if first.startswith("و") and first[1:] in curr:
            found = True
        if len(terms[start_idx:]) > 0 and (e not in curr) and (not found):
            return self._match_detect_missing_verse(terms, curr, start_idx, delims, find_err)

        rf1, rs1, err1, end1 = self._match_detect_missing_verse(terms, curr, start_idx, delims, find_err)
        if len(rs1.split()) == len(terms[start_idx:]):
            return rf1, rs1, err1, end1

        if not found:
            terms[start_idx] = "و" + first
            rf2, rs2, err2, end2 = self._match_detect_missing_verse(terms, curr, start_idx, delims, find_err)
            err2.append([first, terms[start_idx], start_idx])
            terms[start_idx] = term
        else:
            terms[start_idx] = first[1:]
            rf2, rs2, err2, end2 = self._match_detect_missing_verse(terms, curr, start_idx, delims, find_err)
            err2.append([first, first[1:], start_idx])
            terms[start_idx] = term

        if len(rs2.split()) > len(rs1.split()):
            return rf2, rs2, err2, end2
        return rf1, rs1, err1, end1

    def _locate_verse_with_name(
        self, name: str, verses: set[VerseRef], prefer_number: int | None = None
    ) -> VerseRef | None:
        candidates = [r for r in verses if r.name == name]
        if not candidates:
            return None
        # Only apply the merge-preference heuristic for small ambiguous sets.
        # Some very common fragments map to many verses in the same surah; in such cases
        # forcing a sequential merge candidate can create incorrect long merges.
        if prefer_number is not None and len(candidates) <= 2:
            for r in candidates:
                if int(r.number) == prefer_number:
                    return r
        # Deterministic fallback (legacy had set-order dependence here).
        return sorted(candidates, key=lambda r: int(r.number))[0]

    def _update_results(
        self,
        k: VerseRef,
        mem_aya: list[str],
        mem_vs: list[int],
        mem: list[str],
        result: dict[str, list[MatchRecord]],
        er: list[list],
        cv: str,
        start: int,
        end: int,
    ) -> bool:
        if k.name not in mem_aya:
            return True
        idx = mem_aya.index(k.name)
        prev = int(k.number) - 1
        if prev == mem_vs[idx]:
            active: MatchRecord | None = None
            recs = result[k.name]
            if len(recs) == 1:
                active = recs[0]
            else:
                for r in recs:
                    if r.aya_end == prev:
                        active = r
                        break
            if active is None:
                return True
            active.verses.append(cv)
            active.aya_end = int(k.number)
            active.end_in_text = end
            active.errors.append(er)

            for g in range(len(mem)):
                if g != idx:
                    n_to_del = mem[g].split(":")[0]
                    idx_to_del = mem[g].split(":")[1]
                    recs2 = result[n_to_del]
                    if len(recs2) > 1:
                        cnt = 0
                        for r in recs2:
                            # Preserve legacy behavior: idx_to_del is a str, r.aya_start is an int,
                            # so this comparison is effectively always False (no deletion occurs).
                            if r.aya_start == idx_to_del:
                                recs2.pop(cnt)
                                break
                            cnt = +1

            mem_aya.clear()
            mem_vs.clear()
            mem.clear()
            return False

        mem_aya.pop(idx)
        mem_vs.pop(idx)
        mem.pop(idx)
        return True

    def _match_verses_in_text(
        self, in_str: str, find_err: bool, find_missing: bool, delims: str
    ) -> tuple[dict[str, list[MatchRecord]], list[list]]:
        result: dict[str, list[MatchRecord]] = {}
        mem_aya: list[str] = []
        mem_vs: list[int] = []
        mem: list[str] = []
        errs: list[list] = []

        terms = in_str.split()
        i = 0
        while i < len(terms):
            end = -1
            valid, t, i = get_next_valid_term(terms, delims, i)
            if not valid:
                return result, errs
            v = "و" + t
            z = t[1:]
            if t in self.trie or v in self.trie or z in self.trie:
                r: set[VerseRef] = set()
                r_str = ""
                er: list[list] = []
                if find_missing:
                    r, r_str, er, end = self._match_long_verse_detect_missing(terms, self.trie, i, delims, find_err)
                else:
                    r, r_str, er, end = self._match_long_verse(terms, self.trie, i, delims, find_err)
                if len(r) == 0:
                    mem_aya = []
                    mem_vs = []
                    mem = []
                    i = i + 1
                    continue

                errs = errs + er
                curr_ayat = [x.name for x in r]
                overlap = sorted(set(curr_ayat).intersection(set(mem_aya)))
                found = False
                if len(overlap) > 0:
                    start = i
                    for v_name in overlap:
                        prefer_number = None
                        if v_name in mem_aya:
                            idx = mem_aya.index(v_name)
                            prefer_number = mem_vs[idx] + 1
                        k = self._locate_verse_with_name(v_name, r, prefer_number=prefer_number)
                        if k is None:
                            continue
                        create_new_rec = self._update_results(k, mem_aya, mem_vs, mem, result, er, r_str, start, end)
                        found = not create_new_rec
                        aya = k.to_str()
                        mem_aya.append(k.name)
                        mem_vs.append(int(k.number))
                        mem.append(aya)
                    if found:
                        i = i + len(r_str.split())

                if (not found) and len(r) > 0:
                    start = i
                    for k in r:
                        aya = k.to_str()
                        mem_aya.append(k.name)
                        mem_vs.append(int(k.number))
                        mem.append(aya)
                        new_rec = MatchRecord(
                            verses=[r_str],
                            surah_name=k.name,
                            aya_start=int(k.number),
                            aya_end=int(k.number),
                            errors=[er],
                            start_in_text=start,
                            end_in_text=end,
                        )
                        if k.name in result:
                            result[k.name].append(new_rec)
                        else:
                            result[k.name] = [new_rec]

                    i = i + len(r_str.split())
            else:
                i = i + 1
            if end > 0:
                i = end
        return result, errs

    def _is_valid_rec(self, r: MatchRecord, settings: Settings) -> bool:
        length = r.get_len()
        if length < settings.min_match:
            return False
        if r.get_err_num() > settings.allowed_error_pct * length:
            return False
        if len(r.verses) == 1:
            if r.verses[0] in self.stop_verses:
                return False
            v_len = len(r.verses[0].split())
            if v_len < 6:
                allowed_factor = (v_len - 3) / v_len
                if _get_stop_percentage(r.verses[0], self.stops) > allowed_factor:
                    return False
        return True

    def annotate(self, text: str, settings: Settings = Settings()) -> str:
        text = pad_symbols(text)
        recs, _errs = self._match_verses_in_text(text, settings.find_errors, settings.find_missing, settings.delimiters)
        seen: list[tuple[int, int]] = []
        all_terms = text.split()
        replacement_index = 0
        result = ""
        replacement_recs: dict[int, MatchRecord] = {}
        replacement_texts: dict[int, str] = {}

        for v in recs:
            matches = recs[v]
            for r in matches:
                if not self._is_valid_rec(r, settings):
                    continue
                c_text = r.get_orig_str(self.q_orig, self.q_norm)
                curr_loc = (r.start_in_text, r.end_in_text)
                if curr_loc not in seen:
                    replacement_recs[curr_loc[0]] = r
                    replacement_texts[curr_loc[0]] = c_text
                seen.append(curr_loc)

        for idx in sorted(replacement_recs):
            r = replacement_recs[idx]
            result = result + " ".join(all_terms[replacement_index : r.start_in_text]) + replacement_texts[idx] + " "
            replacement_index = r.end_in_text
        result = result.strip() + " ".join(all_terms[replacement_index:])
        return result

    def detect(self, text: str, settings: Settings = Settings()) -> list[dict]:
        text = pad_symbols(text)
        recs, _errs = self._match_verses_in_text(text, settings.find_errors, settings.find_missing, settings.delimiters)
        result: list[dict] = []
        for v in recs:
            matches = recs[v]
            for r in matches:
                if not self._is_valid_rec(r, settings):
                    continue
                result.append(r.to_dict())
        return result
