# Cloud Cost Anomaly Detector

Offline Python CLI that detects unusual service-level cloud spend from normalized billing CSV files. It uses a trailing median and median absolute deviation baseline, requires a minimum dollar increase, and can fail CI when anomalies are present.

## Run

The input CSV requires `date`, `service`, and `cost` columns. Duplicate rows for the same service and day are aggregated using decimal arithmetic.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .

cloud-cost-anomaly examples/costs.csv
```

JSON output and CI failure behavior:

```bash
cloud-cost-anomaly examples/costs.csv \
  --window 7 \
  --minimum-baseline-points 4 \
  --score-threshold 3.5 \
  --minimum-delta 10 \
  --minimum-percent 50 \
  --format json \
  --fail-on-anomaly
```

Exit codes:

- `0`: analysis completed and no failing anomaly condition was requested
- `1`: anomalies were found with `--fail-on-anomaly`
- `2`: invalid input or configuration

## Verify

```bash
python -m pip install "coverage[toml]"
python -m compileall -q src tests
coverage run -m unittest discover -s tests -v
coverage report
```

The tool runs locally, contacts no cloud APIs, and requires no credentials. Export billing data separately and normalize it to the three-column input format before analysis.
