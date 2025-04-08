# Quran Detector

## Description

**Quran Detector** is a Python-based tool designed to detect, match, and annotate Quranic verses within any input text. The tool performs the following functions:

- Reads Quranic data files.
- Normalizes Arabic text.
- Builds a trie-based data structure for fast and efficient matching.
- Uses error-tolerant techniques (via Levenshtein distance) to handle minor typos or omissions.

## Features

- **Accurate Quranic Verse Detection**
  Utilizes a trie-based data structure for efficient lookup and matching of Quranic verses within input texts.

- **Error-Tolerant Matching**
  Employs Levenshtein distance algorithms to handle minor errors (e.g., typos or missing words) ensuring robust verse identification.

- **Comprehensive Annotation**
  Provides detailed annotations for detected verses including Surah and Ayah references.

- **Arabic Text Normalization**
  Preprocesses and normalizes Arabic script to improve detection accuracy.

## Upcoming Features

- Additional customization options for matching criteria.
- Improved performance enhancements.
- Extended API support for integration with other applications.

---

## Installation

You can easily install Quran Detector using `pip`:

1. **Install via pip:**

   ```bash
   pip install quran-detector
   ```

2. **Verify the installation:**

   ```bash
   pip show quran-detector
   ```

   If installed correctly, you will see output that includes the package name, version, and other related details.

---

## How to Use

### 1. Creating an Instance

Begin by creating an instance of the `QuranMatcherAnnotator` class:

```python
from quran_detector import matcher

# Create a QuranMatcherAnnotator object
quran_matcher_annotator = matcher.QuranMatcherAnnotator()
```

---

### 2. Detecting Verses in Text

To detect all Quranic verses in a piece of text, call the `match_all` method with your input text. All other parameters have default values, so you may simply pass in the text:

```python
results = quran_matcher_annotator.match_all(inText)
```

#### Method Parameters

The method signature is:

```python
match_all(text, find_errors=True, find_missing=True, allowed_err_pct=0.25,
         min_match=3, return_json=False, delimiters='#|،|\\.|{|}|\n|؟|!|\\(|\\)|﴿|﴾|۞|\u06dd|\\*|-|\\+|\\:|…')
```

- **text**:
  The text in which to detect Quranic verses (mandatory).

- **find_errors**:
  Boolean flag to detect spelling errors (default: `True`).

- **find_missing**:
  Boolean flag to detect missing words (default: `True`).

- **allowed_err_pct**:
  The allowed error percentage if error detection is enabled (default: `0.25`).

- **min_match**:
  Minimum number of words required to return a match (default: `3`).

- **return_json**:
  If `True`, returns results as JSON objects instead of dictionaries (default: `False`).

- **delimiters**:
  Custom list of delimiters used for splitting the text. Defaults to a comprehensive list of punctuation characters.

#### Sample Usage

**Example 1:** Detecting verses with default parameters

```python
txt = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحونَ بِحمدِ ربهِم واذكر ربك إذا نسيت…"
results = quran_matcher_annotator.match_all(txt)
print(results)
print(len(results), "entry(s) returned.")
```

*Expected Output:*

```python
[
    {
        'aya_name': 'غافر',
        'verses': ['الذين يحملون العرش ومن حوله يسبحون بحمد ربهم'],
        'errors': [[('يسبحو', 'يسبحون', 18)]],
        'startInText': 13,
        'endInText': 21,
        'aya_start': 7,
        'aya_end': 7
    },
    {
        'aya_name': 'الكهف',
        'verses': ['واذكر ربك اذا نسيت'],
        'errors': [[]],
        'startInText': 21,
        'endInText': 25,
        'aya_start': 24,
        'aya_end': 24
    }
]
```

**Example 2:** Handling a missing word

```python
txt = "الم ذلك الكتاب لا ريب هدي للمتقين"
results = quran_matcher_annotator.match_all(txt)
print(results)
print(len(results), "entry(s) returned.")
```

*Expected Output:*

```python
[
    {
        'aya_name': 'البقرة',
        'verses': ['الم', 'ذلك الكتاب لا ريب فيه هدي للمتقين'],
        'errors': [[], [('هدي', 'فيه هدي', 5)]],
        'startInText': 0,
        'endInText': 7,
        'aya_start': 1,
        'aya_end': 2
    }
]
```

---

### 3. Using Error Detection Flags

Error detection improves match quality by detecting common spelling mistakes or omissions, but it may slow down processing. Below are the main flags available:

```python
# Enable error detection (default)
find_errors = True

# Set allowed error percentage (default 0.25 means 25%)
allowed_err_pct = 0.25

# Enable detection of missing words (default)
find_missing = True
```

#### Examples

**Example 1:** With error detection enabled (default):

```python
txt = "RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا .. ﴿قُلْ هُوَا اللَّهُ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…"
results = quran_matcher_annotator.match_all(txt)
print(results)
print(len(results), "entry(s) returned.")
```

*Expected Output:*

```python
[
    {
        'aya_name': 'الإخلاص',
        'verses': ['قل هو الله احد', 'الله الصمد', 'لم يلد ولم يولد'],
        'errors': [[('هوا', 'هو', 12)], [], []],
        'startInText': 11,
        'endInText': 23,
        'aya_start': 1,
        'aya_end': 3
    }
]
```

**Example 2:** Disabling error detection:

```python
results = quran_matcher_annotator.match_all(txt, find_errors=False)
print(results)
```

*Expected Output:*
Verses with errors (if any) will not be detected; only fully matched verses will be returned.

```python
[
    {
    'aya_name': 'الإخلاص',
    'verses': ['الله الصمد', 'لم يلد ولم يولد'],
    'errors': [[], []],
    'startInText': 15,
    'endInText': 22,
    'aya_start': 2,
    'aya_end': 3
    }
]
```


**Example 3:** Increasing the error tolerance:

```python
txt = "RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا .. ﴿قُلْ هُوَا اللَّهُ أَحَ…"
print("Default tolerance (0.25):")
print(quran_matcher_annotator.match_all(txt))  # May return no matches

print("Increased tolerance (0.5):")
results = quran_matcher_annotator.match_all(txt, allowed_err_pct=0.5)
print(results)
```

*Expected Output:*
Increasing the tolerance may return matches despite higher errors, but may reduce precision.

---

### 4. Annotating Text

Annotating text involves detecting Quranic verses, replacing them with their correct diacriticized forms, and appending the corresponding Quranic reference. To annotate text, use the `annotateTxt` method:

```python
annotated_text = quran_matcher_annotator.annotateTxt(inText)
print(annotated_text)
```

#### Example 1: Annotating a Text with Leading and Trailing Ellipses

```python
txt = "RT @user:... كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحونَ بِحمدِ ربهِم…"
annotated = quran_matcher_annotator.annotateTxt(txt)
print(annotated)
```

*Expected Output:*

```
RT @user:... كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له "الَّذِينَ يَحْمِلُونَ الْعَرْشَ وَمَنْ حَوْلَهُ يُسَبِّحُونَ بِحَمْدِ رَبِّهِمْ..." (غافر:7)
```

#### Example 2: Annotating Text with Auto-Correction

```python
txt = " واستعينوا بالصبر والصلاه وانها لكبيره الا علي الخشعين"
annotated = quran_matcher_annotator.annotateTxt(txt)
print(annotated)
```

*Expected Output:*

```
"وَاسْتَعِينُوا بِالصَّبْرِ وَالصَّلَاةِ ۚ وَإِنَّهَا لَكَبِيرَةٌ إِلَّا عَلَى الْخَاشِعِينَ" (البقرة:45)
```
