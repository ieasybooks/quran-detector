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

# quran-detector

Detect Quranic verses and verse fragments in Arabic text (tweets, articles, books) with a small Python API and a CLI.

## Scientific Source

This implementation is based on the QDetect paper:

> “QDetect: An Intelligent Tool for Detecting Quranic Verses in any Text”  
> Samhaa R. El-Beltagy and Ahmed Rafea, Procedia Computer Science 189 (2021) 374–381.  
> Paper link: https://www.sciencedirect.com/science/article/pii/S1877050921012321

This package is a modern rewrite of the legacy repository:

https://github.com/SElBeltagy/Quran_Detector

## Features

- Detect full verses and verse fragments in long Arabic text.
- Optional single-edit spelling correction (Levenshtein distance = 1).
- Optional missing-word detection (more expensive; can be aggressive).
- Clean API: `detect`, `annotate`, and `Settings`.
- CLI: `quran-detector`.
- Bundled Quran resources loaded via `importlib.resources`.
- Golden-file regression tests to preserve behavior.

## Requirements

- Python **3.12+**

## Installation

### Using `uv` (recommended)

```bash
uv add quran-detector
```

Dev extras (for contributors):

```bash
uv add --dev "quran-detector[dev]"
```

### Using `pip`

```bash
python -m pip install quran-detector
```

Dev extras:

```bash
python -m pip install "quran-detector[dev]"
```

### From source

- Clone: `git clone git@github.com:ieasybooks/quran-detector.git`
- Enter: `cd quran-detector`
- Install: `uv sync --extra dev`

If you use Mise:

```bash
mise exec python@3.12 -- uv sync --extra dev
```

## Usage

### CLI

- Detect (JSON): `quran-detector detect --input input.txt > matches.json`
- Annotate: `quran-detector annotate --input input.txt > annotated.txt`
- From stdin: `cat input.txt | quran-detector detect --stdin`

Example with custom settings:

```bash
quran-detector detect --stdin --no-find-errors --no-find-missing --allowed-error-pct 0.5 --min-match 5
```

### Python API

Public API surface:

- `quran_detector.detect(text: str, settings: Settings = Settings()) -> list[dict]`
- `quran_detector.annotate(text: str, settings: Settings = Settings()) -> str`
- `quran_detector.Settings`

#### Example: annotate

```python
from quran_detector import Settings, annotate

text = "قال تعالى: وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ"
print(annotate(text, settings=Settings(find_missing=False)))
```

Note: `find_missing=True` can be aggressive on general prose (it may pull in words before a verse). For user-facing UI,
it’s often better to set `Settings(find_missing=False)`.

#### Example: detect

```python
from quran_detector import Settings, detect

text = "وَاصْبِرْ وَمَا صَبْرُكَ إِلَّا بِاللَّهِ"
matches = detect(text, settings=Settings(find_missing=False))
print(matches)
```

## Settings

`Settings` controls matching behavior (and maps 1:1 to CLI flags):

- `find_errors`: enables spelling correction (Levenshtein=1).
- `find_missing`: enables missing-word detection (expensive; may be aggressive).
- `allowed_error_pct`: maximum allowed errors as a fraction of match length.
- `min_match`: minimum number of words in a match.
- `delimiters`: regex used to strip punctuation before matching.

## Output Format

### `detect()`

Returns `list[dict]` where each record includes:

- `surah_name`
- `aya_start`, `aya_end`
- `verses`
- `errors`
- `start_in_text`, `end_in_text` (word indices relative to `text.split()`)

Note: indices are word positions (not character offsets).

### `annotate()`

Returns the text with detected spans replaced by the Quran text and a reference marker:

```
"<quran text>" (surah:ayah[-ayah])
```

Ambiguity note: some common fragments map to multiple verses. In such cases, multiple valid outputs can exist; golden
tests validate annotation only for unambiguous start positions.

## Algorithm Overview (QDetect)

High level:

1. Normalize Arabic variants and strip tashkeel/diacritics for matching.
2. Build a trie-like index over all verse suffixes (>= 3 words), tracking terminals for longest-match behavior.
3. Scan input tokens and extend matches greedily.
4. Filter matches by minimum length, error ratio, and heuristics for short fragments.

See the paper link above for the full description.

## Data / Resources

Bundled in `src/quran_detector/data/`:

- `quran-simple.txt` (Quran text)
- `quran-index.xml` (surah metadata)
- `non-terminals.txt` (stop/non-terminal words)

Loaded via `importlib.resources` (works in wheels/zipped installs).

## Development

### pre-commit

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

Tests use vendored fixtures under `tests/fixtures/`.

Run as separate commands:

```bash
pytest -q tests/test_tweets_eval.py
pytest -q tests/test_golden_outputs.py -k 'match_all_against_golden'
pytest -q tests/test_golden_outputs.py -k 'annotate_txt_against_golden'
```

Note: golden suites are intentionally heavy and can take ~30–40 minutes each on a laptop.

