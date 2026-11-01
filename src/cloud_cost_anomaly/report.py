from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal
from typing import TextIO

from .models import Anomaly, CostRecord


def summarize(records: list[CostRecord]) -> dict[str, object]:
    by_service: defaultdict[str, Decimal] = defaultdict(Decimal)
    total = Decimal()
    for record in records:
        total += record.cost
        by_service[record.service] += record.cost
    return {
        "records": len(records),
        "total_cost": format(total, ".2f"),
        "service_totals": {
            service: format(cost, ".2f")
            for service, cost in sorted(by_service.items())
        },
    }


def write_json(
    stream: TextIO, records: list[CostRecord], anomalies: list[Anomaly]
) -> None:
    payload = {
        "summary": summarize(records),
        "anomaly_count": len(anomalies),
        "anomalies": [anomaly.as_dict() for anomaly in anomalies],
    }
    json.dump(payload, stream, indent=2)
    stream.write("\n")


def write_text(
    stream: TextIO, records: list[CostRecord], anomalies: list[Anomaly]
) -> None:
    summary = summarize(records)
    stream.write(
        f"Cloud cost summary: {summary['records']} records, "
        f"${summary['total_cost']} total\n"
    )
    if not anomalies:
        stream.write("Anomalies: none\n")
        return
    stream.write(f"Anomalies: {len(anomalies)}\n")
    for anomaly in anomalies:
        percent = (
            f"{anomaly.percent_change:.1f}%"
            if anomaly.percent_change is not None
            else "new spend"
        )
        score = f", score {anomaly.score:.2f}" if anomaly.score is not None else ""
        stream.write(
            f"- {anomaly.date} {anomaly.service}: ${anomaly.actual:.2f} "
            f"vs ${anomaly.baseline:.2f} baseline "
            f"(+${anomaly.delta:.2f}, {percent}{score})\n"
        )
