from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from statistics import median

from .models import Anomaly, CostRecord

MAD_SCALE = Decimal("1.4826")


def detect_anomalies(
    records: list[CostRecord],
    *,
    window: int = 7,
    minimum_baseline_points: int = 4,
    score_threshold: Decimal = Decimal("3.5"),
    minimum_delta: Decimal = Decimal("10"),
    minimum_percent: Decimal = Decimal("50"),
) -> list[Anomaly]:
    if window < 2:
        raise ValueError("window must be at least 2")
    if minimum_baseline_points < 2 or minimum_baseline_points > window:
        raise ValueError("minimum baseline points must be between 2 and window")
    if score_threshold <= 0 or minimum_delta < 0 or minimum_percent < 0:
        raise ValueError("thresholds must be non-negative and score threshold positive")

    by_service: defaultdict[str, list[CostRecord]] = defaultdict(list)
    for record in records:
        by_service[record.service].append(record)

    anomalies: list[Anomaly] = []
    for service, service_records in sorted(by_service.items()):
        ordered = sorted(service_records, key=lambda record: record.date)
        for index, current in enumerate(ordered):
            history = ordered[max(0, index - window) : index]
            if len(history) < minimum_baseline_points:
                continue
            costs = [record.cost for record in history]
            baseline = Decimal(median(costs))
            delta = current.cost - baseline
            if delta < minimum_delta:
                continue

            deviations = [abs(cost - baseline) for cost in costs]
            mad = Decimal(median(deviations))
            score = delta / (mad * MAD_SCALE) if mad > 0 else None
            percent = (delta / baseline * 100) if baseline > 0 else None

            score_triggered = score is not None and score >= score_threshold
            percent_triggered = percent is not None and percent >= minimum_percent
            zero_baseline_triggered = baseline == 0 and current.cost >= minimum_delta
            if not (score_triggered or percent_triggered or zero_baseline_triggered):
                continue

            anomalies.append(
                Anomaly(
                    date=current.date,
                    service=service,
                    actual=current.cost,
                    baseline=baseline,
                    delta=delta,
                    percent_change=percent,
                    score=score,
                    baseline_points=len(history),
                )
            )
    return sorted(anomalies, key=lambda item: (item.date, item.service))
