from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from cloud_cost_anomaly.cli import EXIT_ANOMALY, EXIT_ERROR, EXIT_OK, run


class CLITests(unittest.TestCase):
    def write_csv(self, content: str) -> str:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "costs.csv"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def test_fail_on_anomaly_exit_code(self) -> None:
        path = self.write_csv(
            "date,service,cost\n"
            "2026-10-01,Compute,10\n"
            "2026-10-02,Compute,10\n"
            "2026-10-03,Compute,10\n"
            "2026-10-04,Compute,10\n"
            "2026-10-05,Compute,50\n"
        )
        stdout, stderr = io.StringIO(), io.StringIO()
        code = run([path, "--fail-on-anomaly", "--format", "json"], stdout=stdout, stderr=stderr)
        self.assertEqual(code, EXIT_ANOMALY)
        self.assertIn('"anomaly_count": 1', stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_clean_data_returns_success(self) -> None:
        path = self.write_csv(
            "date,service,cost\n"
            "2026-10-01,Compute,10\n"
            "2026-10-02,Compute,10\n"
            "2026-10-03,Compute,10\n"
            "2026-10-04,Compute,10\n"
        )
        code = run([path], stdout=io.StringIO(), stderr=io.StringIO())
        self.assertEqual(code, EXIT_OK)

    def test_invalid_input_returns_error(self) -> None:
        path = self.write_csv("date,service\n2026-10-01,Compute\n")
        stderr = io.StringIO()
        code = run([path], stdout=io.StringIO(), stderr=stderr)
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("missing required columns", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
