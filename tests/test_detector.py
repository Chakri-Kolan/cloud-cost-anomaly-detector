from __future__ import annotations

import unittest
from datetime import date, timedelta
from decimal import Decimal

from cloud_cost_anomaly.detector import detect_anomalies
from cloud_cost_anomaly.models import CostRecord


def records_for(costs: list[str], service: str = "Compute") -> list[CostRecord]:
    start = date(2026, 10, 1)
    return [
        CostRecord(start + timedelta(days=index), service, Decimal(cost))
        for index, cost in enumerate(costs)
    ]


class DetectionTests(unittest.TestCase):
    def test_detects_large_spend_spike(self) -> None:
        anomalies = detect_anomalies(records_for(["10", "11", "10", "9", "10", "11", "50"]))
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].actual, Decimal("50"))
        self.assertEqual(anomalies[0].baseline, Decimal("10"))

    def test_does_not_flag_small_absolute_change(self) -> None:
        anomalies = detect_anomalies(
            records_for(["1", "1", "1", "1", "2"]), minimum_delta=Decimal("10")
        )
        self.assertEqual(anomalies, [])

    def test_detects_new_spend_after_zero_baseline(self) -> None:
        anomalies = detect_anomalies(records_for(["0", "0", "0", "0", "25"]))
        self.assertEqual(len(anomalies), 1)
        self.assertIsNone(anomalies[0].percent_change)

    def test_services_are_analyzed_independently(self) -> None:
        records = records_for(["10", "10", "10", "10", "50"], "Compute")
        records += records_for(["5", "5", "5", "5", "5"], "Storage")
        anomalies = detect_anomalies(records)
        self.assertEqual([item.service for item in anomalies], ["Compute"])

    def test_validates_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "window"):
            detect_anomalies([], window=1)
        with self.assertRaisesRegex(ValueError, "baseline"):
            detect_anomalies([], window=4, minimum_baseline_points=5)


if __name__ == "__main__":
    unittest.main()
