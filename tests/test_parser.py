from __future__ import annotations

import io
import unittest
from decimal import Decimal

from cloud_cost_anomaly.parser import BillingDataError, parse_csv


class ParseCSVTests(unittest.TestCase):
    def test_aggregates_duplicate_service_day_rows(self) -> None:
        records = parse_csv(
            io.StringIO(
                "date,service,cost\n"
                "2026-10-01,Compute,10.25\n"
                "2026-10-01,Compute,2.75\n"
                "2026-10-01,Storage,1.00\n"
            )
        )
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].cost, Decimal("13.00"))

    def test_rejects_missing_columns(self) -> None:
        with self.assertRaisesRegex(BillingDataError, "missing required columns"):
            parse_csv(io.StringIO("date,cost\n2026-10-01,1\n"))

    def test_rejects_negative_cost(self) -> None:
        with self.assertRaisesRegex(BillingDataError, "non-negative"):
            parse_csv(io.StringIO("date,service,cost\n2026-10-01,Compute,-1\n"))

    def test_rejects_empty_data(self) -> None:
        with self.assertRaisesRegex(BillingDataError, "no data"):
            parse_csv(io.StringIO("date,service,cost\n"))


if __name__ == "__main__":
    unittest.main()
