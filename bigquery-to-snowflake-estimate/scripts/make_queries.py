#!/usr/bin/env python3
"""
make_queries.py - Generate one ready-to-run BigQuery usage query covering the full date range.

Usage:
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/make_queries.py \
        --start 2026-03-01 --end 2026-10-01 --region region-us --out-dir <DIR>

--start is the first day of the first month. --end is the first day of the month
AFTER the last month (exclusive). Both must be the 1st of a month.
The query returns one row per project per month, so the user runs it once and downloads one CSV.
"""

import argparse
from datetime import date
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "bq_monthly_usage_query.sql"


def parse_first_of_month(value: str, label: str) -> date:
    try:
        d = date.fromisoformat(value)
    except ValueError:
        raise SystemExit(f"Error: {label} '{value}' must be a date in YYYY-MM-DD format")
    if d.day != 1:
        raise SystemExit(f"Error: {label} '{value}' must be the first day of a month (YYYY-MM-01)")
    return d


def main():
    p = argparse.ArgumentParser(description="Generate the BigQuery usage query for a date range")
    p.add_argument("--start", required=True, help="First day of the first month, YYYY-MM-01")
    p.add_argument("--end", required=True, help="First day of the month after the last month, YYYY-MM-01 (exclusive)")
    p.add_argument("--region", default="region-us", help="BigQuery region qualifier, e.g. region-us")
    p.add_argument("--out-dir", required=True, help="Directory to write the .sql file")
    args = p.parse_args()

    s = parse_first_of_month(args.start, "start date")
    e = parse_first_of_month(args.end, "end date")
    if e <= s:
        raise SystemExit(f"Error: end date {args.end} must be after start date {args.start}")
    n_months = (e.year - s.year) * 12 + (e.month - s.month)

    sql = (TEMPLATE.read_text()
           .replace("{{RANGE_START}}", s.isoformat())
           .replace("{{RANGE_END}}", e.isoformat())
           .replace("{{REGION}}", args.region))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"bq_usage_{s:%Y-%m}_to_{e:%Y-%m}_excl.sql"
    path.write_text(sql)
    print(f"{path} ({n_months} months)")


if __name__ == "__main__":
    main()
