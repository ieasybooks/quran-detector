# quran_matcher/matcher.py
from utils import pad_symbols, normalize_term, get_next_valid_term, GLOBAL_DELIMITERS
from data_loader import build_sura_index, build_verse_dicts, add_ayat
from models import MatchRecord
import Levenshtein

DEBUG = False

class QuranMatcherAnnotator:
    """
    Main class for matching and annotating Quran verses in a given text.
    """
    def __init__(self, index_file: str = 'dfiles/quran-index.xml', 
                 ayat_file: str = 'dfiles/quran-simple.txt', 
                 stops_file: str = 'dfiles/nonTerminals.txt'):
        suras = build_sura_index(index_file)
        self.all_nodes = {}  # Trie structure for verse matching
        self.q_orig = build_verse_dicts(suras)
        self.q_norm = build_verse_dicts(suras)
        self.stops = self._load_stops(stops_file)
        self.ambig = set()
        self.min_length = 3  # Minimum acceptable match length
        add_ayat(ayat_file, suras, self.all_nodes, self.q_orig, self.q_norm, self.ambig, self.min_length, self.stops)
        self.besm = 'بسم الله الرحمن الرحيم'
        self.stop_verses = [self.besm, 'الله ونعم الوكيل', 'الحمد لله']
        print("Done loading...")

    def _load_stops(self, filename: str) -> set:
        stops = set()
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                word = normalize_term(word)
                stops.add(word)
        return stops

    def get_stop_percentage(self, text: str) -> float:
        terms = text.split()
        total = len(terms)
        count = 0
        for t in terms:
            if t in self.stops or (t.startswith("و") and t[1:] in self.stops):
                count += 1
        return count / total if total > 0 else 0

    def find_in_children(self, term_text: str, current: dict):
        for key, node in current.items():
            if term_text in node.children:
                return key
        return None

    def match_with_error(self, term_text: str, current: dict):
        for key in current:
            if Levenshtein.distance(term_text, key) == 1 and key not in self.ambig:
                return key
        return None

    def update_results(self, verse_obj, mem_aya: list, mem_vs: list, mem: list, results: dict, errors, current_match: str, end_idx: int):
        idx = mem_aya.index(verse_obj.name)
        prev = int(verse_obj.number) - 1
        if prev == mem_vs[idx]:
            active = None
            recs = results[verse_obj.name]
            if len(recs) == 1:
                active = recs[0]
            else:
                for rec in recs:
                    if rec.end_idx == prev:
                        active = rec
                        break
            if active:
                active.verses.append(current_match)
                active.end_idx = int(verse_obj.number)
                active.end_in_text = end_idx
                active.errors.append(errors)
                for i, item in enumerate(mem):
                    if i != idx:
                        parts = item.split(':')
                        n_to_delete = parts[0]
                        idx_to_delete = parts[1]
                        if n_to_delete in results:
                            recs_list = results[n_to_delete]
                            if len(recs_list) > 1:
                                for rec in recs_list:
                                    if rec.start_idx == int(idx_to_delete):
                                        recs_list.remove(rec)
                                        break
                mem_aya.clear()
                mem_vs.clear()
                mem.clear()
                return False
        else:
            mem_aya.pop(idx)
            mem_vs.pop(idx)
            mem.pop(idx)
            return True

    def match_detect_missing_verse(self, terms: list, current: dict, start_idx: int, delimiters: str, find_error: bool):
        errors = []
        final_result = set()
        result_str_final = ""
        end_idx = 0
        wd_counter = start_idx - 1
        r_str = ""
        for t in terms[start_idx:]:
            wd_counter += 1
            t_norm = normalize_term(t, delimiters)
            if not t_norm:
                continue
            if t_norm not in current:
                if find_error:
                    match = self.match_with_error(t_norm, current)
                    if match:
                        errors.append((t_norm, match, wd_counter))
                        t_norm = match
            if t_norm in current:
                r_str += t_norm + " "
                final_result = current[t_norm].verses
                if current[t_norm].terminal or current[t_norm].abs_terminal:
                    result_str_final = r_str
                    errors_final = errors
                    end_idx = wd_counter + 1
                current = current[t_norm].children
            else:
                missing = self.find_in_children(t_norm, current)
                if missing:
                    r_str += missing + " " + t_norm + " "
                    temp_current = current[missing].children
                    final_result = temp_current[t_norm].verses
                    errors.append((t_norm, missing + " " + t_norm, wd_counter))
                    if len(r_str.split()) > self.min_length and (temp_current[t_norm].terminal or temp_current[t_norm].abs_terminal):
                        result_str_final = r_str
                        errors_final = errors
                        end_idx = wd_counter + 1
                    current = temp_current[t_norm].children
                else:
                    valid, next_term, next_index = get_next_valid_term(terms, delimiters, wd_counter+1)
                    if not valid:
                        return final_result, result_str_final.strip(), errors, end_idx
                    valid_child = self.find_in_children(next_term, current)
                    if valid_child:
                        errors.append((t_norm, valid_child, wd_counter))
                        r_str += t_norm + " "
                        current = current[valid_child].children
                        end_idx = next_index + 1
                    else:
                        return final_result, result_str_final.strip(), errors, end_idx
        return final_result, result_str_final.strip(), errors, end_idx

    def match_single_verse(self, terms: list, current: dict, start_idx: int, delimiters: str, find_error: bool):
        errors = []
        result_str_final = ""
        final_result = set()
        wd_counter = start_idx - 1
        r_str = ""
        end_idx = 0
        for t in terms[start_idx:]:
            wd_counter += 1
            t_norm = normalize_term(t, delimiters)
            if not t_norm:
                continue
            if t_norm not in current and find_error:
                match = self.match_with_error(t_norm, current)
                if match:
                    errors.append((t_norm, match, wd_counter))
                    t_norm = match
            if t_norm in current:
                r_str += t_norm + " "
                final_result = current[t_norm].verses
                if current[t_norm].terminal or current[t_norm].abs_terminal:
                    result_str_final = r_str
                    errors_final = errors
                    end_idx = wd_counter + 1
                current = current[t_norm].children
            else:
                if DEBUG:
                    print(f"{t_norm} not found")
                return final_result, result_str_final.strip(), errors, end_idx
        return final_result, result_str_final.strip(), errors, end_idx

    def match_long_verse(self, terms: list, current: dict, start_idx: int, delimiters: str, find_error: bool):
        # Handles possible missing or extra characters at the beginning of a verse.
        first_term = terms[start_idx]
        normalized_first = normalize_term(first_term, delimiters)
        alternative = "و" + normalized_first
        found = False
        if normalized_first.startswith("و") and normalized_first[1:] in current:
            found = True
        if len(terms[start_idx:]) > 0 and alternative not in current and not found:
            return self.match_single_verse(terms, current, start_idx, delimiters, find_error)
        r1, s1, err1, end1 = self.match_single_verse(terms, current, start_idx, delimiters, find_error)
        if not found:
            terms[start_idx] = alternative
            r2, s2, err2, end2 = self.match_single_verse(terms, current, start_idx, delimiters, find_error)
            err2.append((normalized_first, alternative, start_idx))
            terms[start_idx] = first_term
        else:
            terms[start_idx] = normalized_first[1:]
            r2, s2, err2, end2 = self.match_single_verse(terms, current, start_idx, delimiters, find_error)
            err2.append((normalized_first, normalized_first[1:], start_idx))
            terms[start_idx] = first_term
        return (r2, s2, err2, end2) if len(s2) > len(s1) else (r1, s1, err1, end1)

    def match_long_verse_detect_missing(self, terms: list, current: dict, start_idx: int, delimiters: str, find_error: bool):
        first_term = terms[start_idx]
        normalized_first = normalize_term(first_term, delimiters)
        alternative = "و" + normalized_first
        found = False
        if normalized_first.startswith("و") and normalized_first[1:] in current:
            found = True
        if DEBUG:
            print('Found:', found)
        if len(terms[start_idx:]) > 0 and alternative not in current and not found:
            return self.match_detect_missing_verse(terms, current, start_idx, delimiters, find_error)
        r1, s1, err1, end1 = self.match_detect_missing_verse(terms, current, start_idx, delimiters, find_error)
        if len(s1.split()) == len(terms[start_idx:]):
            return r1, s1, err1, end1
        if not found:
            terms[start_idx] = alternative
            r2, s2, err2, end2 = self.match_detect_missing_verse(terms, current, start_idx, delimiters, find_error)
            err2.append((normalized_first, alternative, start_idx))
            terms[start_idx] = first_term
        else:
            terms[start_idx] = normalized_first[1:]
            r2, s2, err2, end2 = self.match_detect_missing_verse(terms, current, start_idx, delimiters, find_error)
            err2.append((normalized_first, normalized_first[1:], start_idx))
            terms[start_idx] = first_term
        return (r2, s2, err2, end2) if len(s2.split()) > len(s1.split()) else (r1, s1, err1, end1)

    def locate_verse_by_name(self, name: str, verses: set):
        for verse in verses:
            if verse.name == name:
                return verse
        return None

    def match_verses_in_text(self, text: str, current: dict, find_error: bool = True, find_missing: bool = False,
                             delimiters: str = GLOBAL_DELIMITERS):
        results = {}
        mem_aya = []
        mem_vs = []
        mem = []
        errors_accumulated = []
        
        text = pad_symbols(text)
        terms = text.split()
        i = 0
        while i < len(terms):
            # Initialize end_idx to 0 at the start of each loop iteration.
            end_idx = 0

            valid, term_candidate, i = get_next_valid_term(terms, delimiters, i)
            if not valid:
                return results, errors_accumulated
            if (term_candidate in current or 
                ("و" + term_candidate) in current or 
                ((term_candidate.startswith("و") and term_candidate[1:]) in current)):
                if find_missing:
                    matched_result, matched_str, errs, end_idx = self.match_long_verse_detect_missing(terms, self.all_nodes, i, delimiters, find_error)
                else:
                    matched_result, matched_str, errs, end_idx = self.match_long_verse(terms, self.all_nodes, i, delimiters, find_error)
                if not matched_result:
                    mem_aya.clear()
                    mem_vs.clear()
                    mem.clear()
                    i += 1
                    continue
                errors_accumulated += errs
                current_ayahs = [v.name for v in matched_result]
                overlap = set(current_ayahs).intersection(set(mem_aya))
                found = False
                if overlap:
                    for name in overlap:
                        verse_obj = self.locate_verse_by_name(name, matched_result)
                        self.update_results(verse_obj, mem_aya, mem_vs, mem, results, errs, matched_str, end_idx)
                        found = True
                    if found:
                        i += len(matched_str.split())
                if not found and matched_result:
                    start = i
                    for verse_obj in matched_result:
                        aya_str = str(verse_obj)
                        mem_aya.append(verse_obj.name)
                        mem_vs.append(int(verse_obj.number))
                        mem.append(aya_str)
                        record = MatchRecord(matched_str, verse_obj.name, int(verse_obj.number),
                                               int(verse_obj.number), errs, start, end_idx)
                        if verse_obj.name in results:
                            results[verse_obj.name].append(record)
                        else:
                            results[verse_obj.name] = [record]
                    i += len(matched_str.split())
            else:
                i += 1
            if end_idx > 0:
                i = end_idx
        return results, errors_accumulated

    def is_valid_record(self, record: MatchRecord, allowed_err_pct: float = 0.25, min_match: int = 3) -> bool:
        length = record.get_length()
        if length < min_match:
            return False
        if record.get_error_number() > allowed_err_pct * length:
            return False
        if len(record.verses) == 1:
            if record.verses[0] in self.stop_verses:
                return False
            word_count = len(record.verses[0].split())
            if word_count < 6:
                allowed_factor = (word_count - 3) / word_count
                if self.get_stop_percentage(record.verses[0]) > allowed_factor:
                    return False
        return True

    def annotate_text(self, text: str, find_errors: bool = True, find_missing: bool = True,
                      allowed_err_pct: float = 0.25, min_match: int = 3,
                      delimiters: str = GLOBAL_DELIMITERS) -> str:
        text = pad_symbols(text)
        results, _ = self.match_verses_in_text(text, self.all_nodes, find_errors, find_missing, delimiters)
        all_terms = text.split()
        replacement_index = 0
        annotated_result = ""
        seen = []
        replacement_records = {}
        replacement_texts = {}

        for key in results:
            for record in results[key]:
                if not self.is_valid_record(record, allowed_err_pct, min_match):
                    continue
                annotated_text = record.get_original_str(self.q_orig, self.q_norm)
                current_loc = (record.start_in_text, record.end_in_text)
                if current_loc not in seen:
                    replacement_records[current_loc[0]] = record
                    replacement_texts[current_loc[0]] = annotated_text
                seen.append(current_loc)
        
        sorted_indices = sorted(replacement_records)
        for idx in sorted_indices:
            record = replacement_records[idx]
            annotated_result += " ".join(all_terms[replacement_index:record.start_in_text]) + replacement_texts[idx] + ' '
            replacement_index = record.end_in_text
        annotated_result = annotated_result.strip() + " " + " ".join(all_terms[replacement_index:])
        return annotated_result.strip()

    def match_all(self, text: str, find_errors: bool = True, find_missing: bool = True,
                  allowed_err_pct: float = 0.25, min_match: int = 3, return_json: bool = False,
                  delimiters: str = GLOBAL_DELIMITERS):
        text = pad_symbols(text)
        results, _ = self.match_verses_in_text(text, self.all_nodes, find_errors, find_missing, delimiters)
        match_records = []
        for key in results:
            for record in results[key]:
                if not self.is_valid_record(record, allowed_err_pct, min_match):
                    continue
                match_records.append(record.get_structured(json_format=return_json))
        return match_records
