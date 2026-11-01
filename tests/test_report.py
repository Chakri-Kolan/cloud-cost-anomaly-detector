from __future__ import annotations

import io
import json
import unittest
from datetime import date
from decimal import Decimal

from cloud_cost_anomaly.models import Anomaly, CostRecord
from cloud_cost_anomaly.report import summarize, write_json, write_text


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = [
            CostRecord(date(2026, 10, 1), "Compute", Decimal("10.50")),
            CostRecord(date(2026, 10, 1), "Storage", Decimal("2.25")),
        ]
        self.anomaly = Anomaly(
            date(2026, 10, 2),
            service="Compute",
            actual=Decimal("50"),
            baseline=Decimal("10"),
            delta=Decimal("40"),
            percent_change=Decimal("400"),
            score=Decimal("5.2"),
            baseline_points=4,
        )

    def test_summary_uses_decimal_totals(self) -> None:
        summary = summarize(self.records)
        self.assertEqual(summary["total_cost"], "12.75")

    def test_json_output_is_machine_readable(self) -> None:
        output = io.StringIO()
        write_json(output, self.records, [self.anomaly])
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["anomaly_count"], 1)
        self.assertEqual(payload["anomalies"][0]["service"], "Compute")

    def test_text_output_contains_actionable_values(self) -> None:
        output = io.StringIO()
        write_text(output, self.records, [self.anomaly])
        self.assertIn("Compute: $50.00", output.getvalue())


if __name__ == "__main__":
    unittest.main()
