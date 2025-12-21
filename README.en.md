<div align="center">
  <a href="https://pypi.org/project/quran-detector" target="_blank"><img src="https://img.shields.io/pypi/v/quran-detector?label=PyPI%20Version&color=limegreen" /></a>
  <a href="https://pypi.org/project/quran-detector" target="_blank"><img src="https://img.shields.io/pypi/pyversions/quran-detector?color=limegreen" /></a>
  <a href="https://github.com/ieasybooks/quran-detector/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/pypi/l/quran-detector?color=limegreen" /></a>
  <a href="https://pepy.tech/project/quran-detector" target="_blank"><img src="https://static.pepy.tech/badge/quran-detector" /></a>
  <a href="https://github.com/ieasybooks/quran-detector/actions/workflows/pre-commit.yml" target="_blank"><img src="https://github.com/ieasybooks/quran-detector/actions/workflows/pre-commit.yml/badge.svg" /></a>
</div>

<div align="center">

  [![ar](https://img.shields.io/badge/lang-ar-brightgreen.svg)](README.md)
  [![en](https://img.shields.io/badge/lang-en-red.svg)](README.en.md)

</div>

## quran-detector

Detect Quranic verses and verse fragments in Arabic text (tweets, articles, books) using an implementation based on the paper:

> “QDetect: An Intelligent Tool for Detecting Quranic Verses in any Text”  
> Samhaa R. El-Beltagy and Ahmed Rafea, Procedia Computer Science 189 (2021) 374–381.
>
> Paper link: https://www.sciencedirect.com/science/article/pii/S1877050921012321
>
> Legacy implementation repo: https://github.com/SElBeltagy/Quran_Detector

This is a modern rewrite of the legacy `Quran_Detector` project with a clean Python API, a CLI, bundled Quran resources, and golden-file regression tests.

## Installation

### Using `uv` (recommended)

In your project:

```bash
uv add quran-detector
```

For development (adds `ruff`, `mypy`, `pre-commit`):

```bash
uv add --dev "quran-detector[dev]"
```

### Using `pip`

```bash
python -m pip install quran-detector
```

For development extras:

```bash
python -m pip install "quran-detector[dev]"
```

### Repo local setup (this repository)

This repo includes `uv.lock`, so you can do:

```bash
uv sync --extra dev
```

If you use Mise:

```bash
mise exec python@3.12 -- uv sync --extra dev
```

## Quick Start

### Python API

```python
from quran_detector import Settings, detect, annotate

text = "وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ"

records = detect(text, settings=Settings())
annotated = annotate(text, settings=Settings())
```

### CLI

Detect (JSON output):

```bash
quran-detector detect --input input.txt > matches.json
```

Annotate (inserts verse references into the text output):

```bash
quran-detector annotate --input input.txt > annotated.txt
```

Read from stdin:

```bash
cat input.txt | quran-detector detect --stdin
```

## Public API

The public API is intentionally small:

- `quran_detector.detect(text: str, settings: Settings = Settings()) -> list[dict]`
- `quran_detector.annotate(text: str, settings: Settings = Settings()) -> str`
- `quran_detector.Settings` (configuration dataclass)

Internally, a singleton `Engine` is lazily initialized on first call and uses bundled Quran resources.

## Output Format

`detect()` returns a JSON-serializable `list[dict]`, where each record includes:

- `surah_name`: surah name (Arabic string)
- `aya_start`, `aya_end`: verse range (inclusive)
- `verses`: list of matched verse fragments (normalized words)
- `errors`: list-of-lists describing per-fragment corrections
- `start_in_text`, `end_in_text`: token indices into `text.split()` after internal symbol padding

Notes:

- Indices are **word positions**, not character offsets.
- When a match spans multiple consecutive verses, `verses` contains multiple fragments and `aya_end > aya_start`.

## Configuration (`Settings`)

`Settings` controls how matching behaves:

- `find_errors: bool = True`  
  Enables spelling-error correction (Levenshtein distance of 1 between an input token and a trie child).

- `find_missing: bool = True`  
  Enables missing-word detection by allowing a “skip” into children in the trie (expensive; see paper).

- `allowed_error_pct: float = 0.25`  
  Maximum allowed errors as a fraction of match length (in words). Records exceeding this are filtered out.

- `min_match: int = 3`  
  Minimum number of words for a fragment to be considered a valid match (paper default is 3).

- `delimiters: str = GLOBAL_DELIMITERS`  
  Regex used to split/strip punctuation tokens before matching.

CLI flags map 1:1 to these fields:

```bash
quran-detector detect --stdin --no-find-errors --no-find-missing --allowed-error-pct 0.5 --min-match 5
```

## How Annotation Works

`annotate()` returns a string where matched spans are replaced by the original Quran text (as stored in the bundled resources)
plus a reference marker:

```
"<quran text>"(سورة:آية[-آية])
```

Ambiguity note: some very common fragments can map to multiple verses. The legacy algorithm (and thus this rewrite)
has ambiguous cases where different valid outputs exist. The golden tests intentionally validate annotation only for
unambiguous start positions.

## Algorithm Overview (QDetect)

At a high level, the approach is a customized multi-pattern matching method inspired by Aho–Corasick, but implemented as:

1. **Normalization**
   - Normalizes Arabic variants (e.g. alif variants → `ا`, `ة` → `ه`, `ى/ی` → `ي`)
   - Removes Quran diacritics/tashkeel for matching

2. **Indexing Quran**
   - Builds a trie-like structure (“linked hash tables” in the paper) over **all verse suffixes** (>= 3 words)
   - Tracks terminals and absolute-terminals to support “longest match” behavior

3. **Scanning**
   - Scans the input word-by-word, attempting to extend matches as far as possible
   - Optionally applies:
     - Single-character spelling correction
     - Missing-word detection

4. **Filtering**
   - Applies minimum length, stop-verse filtering, and an error-rate threshold (`allowed_error_pct`)
   - Applies a stopword-percentage heuristic for short fragments (paper/legacy behavior)

For details, see the paper link in the above block.

## Data / Resources

The package bundles the required resources in `src/quran_detector/data/`:

- `quran-simple.txt` (Quran text)
- `quran-index.xml` (surah metadata)
- `non-terminals.txt` (stop words / non-terminal list)

The bundled resources are loaded via `importlib.resources`, so they work in wheels and zipped installs.

## Development

### Pre-commit

This repo uses:

- `ruff` (lint + import sorting)
- `ruff format` (formatting)
- `mypy` (type checking)

Install hooks:

```bash
pre-commit install
```

Run on all files:

```bash
pre-commit run --all-files
```

### Tests

Tests use **vendored fixtures** under `tests/fixtures/` (no dependency on external folders).

Run tests as separate commands:

```bash
pytest -q tests/test_tweets_eval.py
pytest -q tests/test_golden_outputs.py -k 'match_all_against_golden'
pytest -q tests/test_golden_outputs.py -k 'annotate_txt_against_golden'
```

Note: the golden suites are intentionally heavy and can take ~30–40 minutes each on a laptop.
