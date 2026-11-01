from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
from typing import Sequence, TextIO

from .detector import detect_anomalies
from .parser import BillingDataError, load_csv
from .report import write_json, write_text

EXIT_OK = 0
EXIT_ANOMALY = 1
EXIT_ERROR = 2


def decimal_value(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("must be a decimal number") from exc
    if not parsed.is_finite():
        raise argparse.ArgumentTypeError("must be finite")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect unusual cloud spend in a normalized billing CSV"
    )
    parser.add_argument("input", help="CSV path, or - for stdin")
    parser.add_argument("--window", type=int, default=7, help="trailing data points")
    parser.add_argument(
        "--minimum-baseline-points", type=int, default=4, help="history required"
    )
    parser.add_argument(
        "--score-threshold", type=decimal_value, default=Decimal("3.5")
    )
    parser.add_argument(
        "--minimum-delta", type=decimal_value, default=Decimal("10")
    )
    parser.add_argument(
        "--minimum-percent", type=decimal_value, default=Decimal("50")
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--fail-on-anomaly",
        action="store_true",
        help="return exit code 1 when anomalies are detected",
    )
    return parser


def run(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        records = load_csv(args.input)
        anomalies = detect_anomalies(
            records,
            window=args.window,
            minimum_baseline_points=args.minimum_baseline_points,
            score_threshold=args.score_threshold,
            minimum_delta=args.minimum_delta,
            minimum_percent=args.minimum_percent,
        )
    except (BillingDataError, OSError, ValueError) as exc:
        stderr.write(f"error: {exc}\n")
        return EXIT_ERROR

    if args.format == "json":
        write_json(stdout, records, anomalies)
    else:
        write_text(stdout, records, anomalies)
    return EXIT_ANOMALY if anomalies and args.fail_on_anomaly else EXIT_OK


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
