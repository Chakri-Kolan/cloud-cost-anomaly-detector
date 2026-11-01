from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CostRecord:
    date: date
    service: str
    cost: Decimal


@dataclass(frozen=True, slots=True)
class Anomaly:
    date: date
    service: str
    actual: Decimal
    baseline: Decimal
    delta: Decimal
    percent_change: Decimal | None
    score: Decimal | None
    baseline_points: int

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "date": self.date.isoformat(),
            "service": self.service,
            "actual": format(self.actual, "f"),
            "baseline": format(self.baseline, "f"),
            "delta": format(self.delta, "f"),
            "percent_change": (
                format(self.percent_change, ".2f")
                if self.percent_change is not None
                else None
            ),
            "score": format(self.score, ".2f") if self.score is not None else None,
            "baseline_points": self.baseline_points,
        }
