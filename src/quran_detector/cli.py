from __future__ import annotations

import argparse
import json
import sys

from .api import annotate, detect
from .config import GLOBAL_DELIMITERS, Settings


def _read_input(args: argparse.Namespace) -> str:
    if args.stdin:
        return sys.stdin.read()
    return open(args.input, "r", encoding="utf-8").read()


def _settings_from_args(args: argparse.Namespace) -> Settings:
    return Settings(
        find_errors=args.find_errors,
        find_missing=args.find_missing,
        allowed_error_pct=args.allowed_error_pct,
        min_match=args.min_match,
        delimiters=args.delimiters,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="quran-detector")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        io = sp.add_mutually_exclusive_group(required=True)
        io.add_argument("--input", type=str, help="Input file path")
        io.add_argument("--stdin", action="store_true", help="Read input text from stdin")
        sp.add_argument("--find-errors", dest="find_errors", action=argparse.BooleanOptionalAction, default=True)
        sp.add_argument(
            "--find-missing",
            dest="find_missing",
            action=argparse.BooleanOptionalAction,
            default=True,
        )
        sp.add_argument("--allowed-error-pct", type=float, default=0.25)
        sp.add_argument("--min-match", type=int, default=3)
        sp.add_argument("--delimiters", type=str, default=GLOBAL_DELIMITERS)

    p_detect = sub.add_parser("detect", help="Detect Quran matches and output JSON")
    add_common(p_detect)
    p_detect.add_argument("--pretty", action=argparse.BooleanOptionalAction, default=None)

    p_annotate = sub.add_parser("annotate", help="Annotate text with detected Quran spans")
    add_common(p_annotate)
    p_annotate.add_argument("--json", action="store_true", help="Output JSON string (useful for golden comparisons)")

    args = parser.parse_args(argv)
    text = _read_input(args)
    settings = _settings_from_args(args)

    if args.cmd == "detect":
        records = detect(text, settings=settings)
        pretty = args.pretty
        if pretty is None:
            pretty = sys.stdout.isatty()
        json.dump(records, sys.stdout, ensure_ascii=False, indent=2 if pretty else None)
        sys.stdout.write("\n")
        return 0

    if args.cmd == "annotate":
        annotated = annotate(text, settings=settings)
        if args.json:
            sys.stdout.write(json.dumps(annotated, ensure_ascii=False, indent=2))
            sys.stdout.write("\n")
        else:
            sys.stdout.write(annotated)
        return 0

    return 2
