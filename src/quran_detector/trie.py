from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VerseRef:
    name: str
    number: str

    def to_str(self) -> str:
        return f"{self.name}:{self.number}"

    def __hash__(self) -> int:  # legacy-equivalent
        # Preserve legacy behavior: hash by surah name only. This intentionally causes
        # collisions across verse numbers and influences set behavior/order.
        return hash(self.name)


@dataclass
class Node:
    term: str = ""
    terminal: bool = False
    abs_terminal: bool = False
    verses: set[VerseRef] = field(default_factory=set)
    children: dict[str, "Node"] = field(default_factory=dict)


def add_verse(
    verse_text: str,
    verse_ref: VerseRef,
    root: dict[str, Node],
    *,
    strict: bool,
    ambig: set[str],
    min_len: int,
    stops: set[str],
) -> None:
    orig = root
    words = verse_text.split()
    length = len(words)
    if length == 1:
        ambig.add(verse_text.strip())
    counter = 0
    curr = root
    for w in words:
        counter += 1
        if w in curr:
            node = curr[w]
        else:
            node = Node(term=w)
            curr[w] = node
        curr = node.children
        if counter >= min_len:
            if strict:
                if w not in stops:
                    node.terminal = True
            else:
                node.terminal = True
            node.verses.add(verse_ref)
        if counter == length:
            node.abs_terminal = True
            node.verses.add(verse_ref)

    if (length - min_len) > 0:
        i = verse_text.index(" ") + 1
        add_verse(
            verse_text[i:],
            verse_ref,
            orig,
            strict=strict,
            ambig=ambig,
            min_len=min_len,
            stops=stops,
        )
