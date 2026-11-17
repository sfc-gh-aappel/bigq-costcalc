---
name: bigquery-to-snowflake-estimate
description: "Explains, step by step, the calculations used to estimate a customer's Snowflake compute and storage cost from their BigQuery usage, and produces an HTML report that walks through every calculation. This is an explainer, not the system of record: official estimates should still come from the Google Slot Calculator Streamlit app. Use when: explaining how a BigQuery-to-Snowflake estimate is calculated, walking a customer or account team through the slot-to-node math, showing the work behind an estimate. Triggers: explain bigquery estimate, bigquery to snowflake calculation, how is the bigquery estimate calculated, bq to snow walkthrough, slot to node, bigquery migration cost explained."
---

# BigQuery to Snowflake Cost Estimate: Calculation Explainer

> **Use the Google Slot Calculator for official estimates.** This skill explains the calculations behind a BigQuery-to-Snowflake estimate. It does not replace the Google Slot Calculator Streamlit app: https://app.snowflake.com/streamlit/sfcogsops/snowhouse_aws_us_west_2/#/apps/ki4qh2k5pei7xqdkpz7k
>
> Tell the user this at the start of every run, and include the same callout at the top of the HTML report.

`<SKILL_DIR>` = the directory containing this file.

## Rules
- 16 BigQuery slots = 1 **X-Small Snowflake node**. This is a hardware comparison. Never call it a "credit-hour."
- Never hardcode customer values. Everything comes from the Step 2 inputs.
- All math runs in `scripts/estimate.py`. Do not recalculate by hand.
- The HTML report is produced **only** by `scripts/estimate.py`. Its built-in template is the approved design. Never write, restyle, or rebuild the report HTML yourself, and do not use the `html-authoring` skill or any other template for it. If the script cannot run, stop and fix the environment; do not substitute a hand-built report.

## Workflow

### Step 1: Prepare the BigQuery query
1. Ask (with `ask_user_question`): customer name, start date, end date, BigQuery region (default `region-us`). The range can cover multiple months.
   - **Start date** = the first day of the first month (e.g., `2026-03-01` for March).
   - **End date** = the first day of the month **after** the last month (e.g., `2026-10-01` to end with September). The end date is not included.
   - Both dates must be the 1st of a month. If either isn't, explain the rule and ask again.
   - BigQuery keeps about **180 days** of job history in `INFORMATION_SCHEMA.JOBS`. The start date must be inside the last ~180 days; otherwise the earliest months come back empty or partial. `make_queries.py` warns when it isn't.
2. Generate one query for the whole range:
   ```bash
   uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/make_queries.py \
     --start <YYYY-MM-01> --end <YYYY-MM-01> --region <region> --out-dir <PROJECT_DIR>/<customer>_bq_estimate/queries
   ```
   The query returns one row per project per month, so a multi-month range is still one query.
3. Show the query in one code block.
4. Tell the user to run it in the BigQuery console and download the result as CSV.
5. **Project coverage:** `INFORMATION_SCHEMA.JOBS` covers only the project the query runs in (it is the same view as `JOBS_BY_PROJECT`). To capture every project at once, change the `FROM` line to `INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION` (organization-level permission required; the alternative is noted in the query). Otherwise run the query in each project and collect one CSV per project. Ask the user to confirm every project in scope is in the results.

### Step 2: Capture the customer inputs
Show this table of inputs and defaults, then make **one** `ask_user_question` call with three text questions:
- "Initial storage volume (TB)" (required, no default).
- "Estimate range: low % / high % of the calculated total" with `defaultValue: "80 / 120"`. Convert to `low_factor` / `high_factor` decimals (80 -> 0.80, 120 -> 1.20). Low must be below 100 and high above 100; if not, explain and ask again.
- "Overrides: type `key: value` per line (e.g. `price_per_credit: 3.10`, `storage_growth: 0.10, 0.12, 0.15`), or leave blank to accept all defaults."

The table lists Years 1, 2, and 3 separately, so each year is reviewed. Only change a year the user overrides; never copy one year's override to another unless they give one value for all three.

| Key | Input | Default |
|---|---|---|
| `initial_storage_tb` | Initial storage volume (TB) | **Required, no default** |
| `tt_fs_pct` | Time travel / failsafe % (extra storage; 8% means 100 MB becomes 108 MB) | 0 |
| `price_per_tb` | Price per TB per month | 23.00 |
| `storage_growth` | Storage growth: Year 1, Year 2, Year 3 (annual) | 0.127 / 0.127 / 0.127 |
| `price_per_credit` | Price per credit | 4.00 (Business Critical list price) |
| `compute_growth` | Compute growth: Year 1, Year 2, Year 3 (annual) | 0.05 / 0.05 / 0.05 |
| `low_factor` / `high_factor` | Estimate range (low % / high % of calculated total), always asked | 80% / 120% |

These are fixed and never asked for: 730 hours/month, 16 slots = 1 X-Small node.

Write the answers to `<PROJECT_DIR>/<customer>_bq_estimate/inputs.json` (percentages as decimals, include `customer`).

**⚠️ STOP**: Show all inputs in one table and get confirmation.

### Step 3: Collect the CSV results
1. Ask the user to attach the CSV(s) and copy them to `<customer>_bq_estimate/csv/`. Several CSVs are fine (for example one per project or per region), as long as the same project/month row does not appear twice. Required columns: `project_id`, `year_month`, `total_slot_ms`, `active_minutes_in_month`.
2. Validate:
   ```bash
   uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/estimate.py \
     --csv <DIR>/csv --inputs <DIR>/inputs.json \
     --start <YYYY-MM-01> --end <YYYY-MM-01> --out <DIR>/<Customer>_BigQuery_to_Snowflake_Estimate_<YYYY-MM-DD>.html --validate-only
   ```
   The script prints the months used for the monthly average: every calendar month from the first to the last month in the data, inclusive (the same rule as the app). A month inside that span with no rows counts as zero; requested months before the first or after the last data month are excluded with a warning (usually outside the ~180-day history). Show any warnings to the user. If validation fails (missing columns, no data, months outside the range, duplicate project/month rows), show the errors and fix them with the user. Try at most 3 times.

### Step 4: Run the calculations
Run the same command without `--validate-only`, adding `--results <DIR>/results.json`. Output file: `<DIR>/<Customer>_BigQuery_to_Snowflake_Estimate_<YYYY-MM-DD>.html`.

Compute uses **the same calculation as the Google Slot Calculator app**: every project-month is calculated **on its own** with that project's real measured clock time, then summed. Projects are never averaged together, and slot ms and active time are never pooled across projects.
- Steps 1-3 (per project-month): **Slot hours** = `total_slot_ms / 3,600,000`; **Average slots** = slot hours / 730; **X-Small nodes** = average slots / 16 (fractional, not rounded up).
- Step 4 (per project-month): **Active hours** = `active_minutes_in_month / 60`, the wall-clock time with at least one query running, overlaps merged, capped at the hours in that calendar month. This equals the app's hours/day × days/month.
- Step 5 (per project-month): **Credits** = X-Small nodes × active hours × 1 credit per X-Small node hour; **Cost** = credits × price per credit.
- Step 6: **Project total** = the sum of that project's months.
- Step 7: **Snowflake total for the observed period** = the sum of all project totals. This is the figure the app reports for the same CSV and price per credit, and the report shows it first.
- Step 8: **Projection baseline** = Step 7 credits / months observed (month 1 credits of the projection). Months observed = every calendar month from the first to the last month in the data, inclusive; the app uses the same rule.
- Steps 9-11: storage starts at initial TB × (1 + TT/FS %) and grows monthly at each year's rate, where monthly rate = (1 + annual)^(1/12) − 1.
- Step 12: compute grows from the Step 8 baseline the same way, using each year's compute rate.
- Steps 13-14: Year 1/2/3 projected totals (compute + storage), then the low/high range.

The Year 1-3 figures are **projections** and will not equal the app's total: the app's total covers only the observed months, while Year 1 covers 12 months with growth, plus storage.

### Step 5: Present the HTML report
Open the report with `open <report.html>`. Give the user the file path and a 4-line summary: the observed-period Snowflake total (matches the app), then the Year 1, 2, and 3 projected totals with ranges.

**⚠️ STOP**: Ask for changes to the report. Formatting changes go in `build_html()` / `CSS` in `scripts/estimate.py`, then re-run Step 4.

## Tools
- `scripts/make_queries.py`: writes one `.sql` covering the full range from `references/bq_monthly_usage_query.sql`.
- `scripts/estimate.py`: validates the inputs, runs every calculation, and writes the HTML report (and an optional results JSON). Standard library only.

## Output
`<customer>_bq_estimate/` folder containing the query, the CSV, `inputs.json`, `results.json`, and the HTML report.
