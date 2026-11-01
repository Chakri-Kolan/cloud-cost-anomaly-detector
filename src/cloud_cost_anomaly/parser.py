from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import TextIO

from .models import CostRecord

REQUIRED_COLUMNS = {"date", "service", "cost"}


class BillingDataError(ValueError):
    """Raised when billing data cannot be validated."""


def parse_csv(stream: TextIO) -> list[CostRecord]:
    reader = csv.DictReader(stream)
    columns = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise BillingDataError(f"missing required columns: {', '.join(sorted(missing))}")

    totals: defaultdict[tuple[date, str], Decimal] = defaultdict(Decimal)
    for line_number, row in enumerate(reader, start=2):
        try:
            record_date = date.fromisoformat((row.get("date") or "").strip())
        except ValueError as exc:
            raise BillingDataError(f"line {line_number}: invalid ISO date") from exc

        service = (row.get("service") or "").strip()
        if not service:
            raise BillingDataError(f"line {line_number}: service is empty")

        try:
            cost = Decimal((row.get("cost") or "").strip())
        except InvalidOperation as exc:
            raise BillingDataError(f"line {line_number}: cost is not numeric") from exc
        if not cost.is_finite() or cost < 0:
            raise BillingDataError(f"line {line_number}: cost must be finite and non-negative")

        totals[(record_date, service)] += cost

    if not totals:
        raise BillingDataError("billing CSV contains no data rows")

    return [
        CostRecord(record_date, service, cost)
        for (record_date, service), cost in sorted(totals.items())
    ]


def load_csv(path: str) -> list[CostRecord]:
    if path == "-":
        import sys

        return parse_csv(sys.stdin)
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return parse_csv(stream)
