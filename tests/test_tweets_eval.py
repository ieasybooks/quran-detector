from __future__ import annotations

from pathlib import Path

from quran_detector import detect
from quran_detector.config import Settings


def _load_gold(path: Path) -> dict[str, int]:
    table: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        table[parts[0].strip()] = int(parts[2].strip())
    return table


def _predict_counts(gold_path: Path, settings: Settings) -> dict[str, int]:
    table: dict[str, int] = {}
    for line in gold_path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        tweet_id = parts[0].strip()
        tweet = parts[1].strip()
        records = detect(tweet, settings=settings)
        spans = {(int(r["startInText"]), int(r["endInText"])) for r in records}
        table[tweet_id] = len(spans)
    return table


def _score_like_paper(gold: dict[str, int], pred: dict[str, int]) -> tuple[float, float, float, float]:
    gold_total = sum(gold.values())
    pred_total = sum(pred.values())

    tp = tn = fp = fn = 0
    for tweet_id, gold_count in gold.items():
        pred_count = pred.get(tweet_id, 0)
        if gold_count == pred_count == 0:
            tn += 1
        elif gold_count == pred_count >= 1:
            tp += pred_count
        else:
            if gold_count > pred_count:
                fn += gold_count - pred_count
            else:
                fp += pred_count - gold_count

    precision = tp / pred_total if pred_total else 0.0
    recall = tp / gold_total if gold_total else 0.0
    f_score = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0
    return precision, recall, f_score, accuracy


def test_tweets_eval_metrics_against_gold() -> None:
    gold_path = Path(__file__).resolve().parents[2] / "Quran_Detector" / "data" / "Tweets_Gold.txt"
    assert gold_path.exists(), f"Missing tweets gold file at {gold_path}"

    settings = Settings(allowed_error_pct=0.2)
    gold = _load_gold(gold_path)
    pred = _predict_counts(gold_path, settings=settings)
    precision, recall, f_score, _accuracy = _score_like_paper(gold, pred)

    # Paper-reported: precision 96.8%, recall 94.8%, F-score 95.8%.
    assert precision >= 0.968
    assert recall >= 0.948
    assert f_score >= 0.958

