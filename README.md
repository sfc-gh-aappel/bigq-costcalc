# BigQuery to Snowflake Cost Calculation Explainer

A Cortex Code (CoCo) skill that walks through, step by step, how a customer's BigQuery usage converts into an estimated Snowflake compute and storage cost, and produces an HTML report showing every calculation.

> **This is an explainer, not the system of record.** Official estimates come from the
> [Google Slot Calculator Streamlit app](https://app.snowflake.com/streamlit/sfcogsops/snowhouse_aws_us_west_2/#/apps/icosbexzbmbas7a4gzfw).

## Contents

| Path | What it is |
|---|---|
| `bigquery-to-snowflake-estimate/` | The skill: `SKILL.md`, scripts, and the BigQuery query template |
| `sample_estimate/` | A fictional "Sample Retail Co" run: input CSVs, `inputs.json`, `project_tags.json`, `results.json`, and the HTML report |
| `docs/` | The Calculation Guide and one page per step (Steps 1–14). Worked examples use the Sample Retail Co numbers. |

## Requirements

- [Cortex Code Desktop](https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code)
- [`uv`](https://docs.astral.sh/uv/) (`brew install uv`). The scripts use only the Python standard library; `uv` provides Python 3.11+.
- Access to the customer's BigQuery console (they run one query and send back a CSV)

## Install

```bash
git clone https://github.com/sfc-gh-aappel/bigq-costcalc.git
mkdir -p ~/.snowflake/cortex/skills
cp -R bigq-costcalc/bigquery-to-snowflake-estimate ~/.snowflake/cortex/skills/
```

The repo is private; ask Andy Appel for access if the clone fails.

Restart CoCo (or start a new chat). The skill appears as `/bigquery-to-snowflake-estimate`.

## Use

In CoCo chat, type `/bigquery-to-snowflake-estimate` (or "explain the bigquery to snowflake calculation"). The skill:

1. Asks for the customer, date range, and BigQuery region, then generates **one** BigQuery query for the whole range.
2. Collects inputs in one form (initial storage TB plus any overrides to the defaults).
3. Takes the CSV the customer exports, tags projects (default **RES**; you list the **OD** ones), and validates.
4. Runs every calculation in `scripts/estimate.py` and opens the HTML report.

Output goes to `<customer>_bq_estimate/` in your current project folder. That folder is ignored by git so customer data is never committed.

## Try it on the sample

```bash
cd bigq-costcalc
K=~/.snowflake/cortex/skills/bigquery-to-snowflake-estimate
uv run --project $K python $K/scripts/estimate.py \
  --csv sample_estimate/csv --inputs sample_estimate/inputs.json --tags sample_estimate/project_tags.json \
  --start 2026-03-01 --end 2026-10-01 --out /tmp/sample_report.html && open /tmp/sample_report.html
```

Expected: Year 1 $2,251,228, Year 2 $2,389,096, Year 3 $2,556,665 (calculated totals). The report should look exactly like `sample_estimate/Sample_Retail_Co_BigQuery_to_Snowflake_Estimate_2026-10-14.html`.

## Report looks different?

The HTML report is built only by `scripts/estimate.py`. If yours doesn't match the sample report, the agent built its own HTML instead of running the script. Check that:

1. `uv` is installed (`uv --version`). Without it the script can't run.
2. The skill is installed at `~/.snowflake/cortex/skills/bigquery-to-snowflake-estimate/` with `scripts/estimate.py` present. Re-run the `cp` in Install after every `git pull`.
3. You ran "Try it on the sample" above and the result matches the sample report.

Then re-run the skill in a new chat.

## Key rule

16 BigQuery slots = 1 X-Small Snowflake node. This is a hardware comparison, not a pricing conversion. Do not call it a "credit-hour." Credits enter the math because a running X-Small node uses 1 credit per hour.
