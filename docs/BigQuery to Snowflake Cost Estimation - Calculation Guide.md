# BigQuery to Snowflake Cost Estimation - Calculation Guide

This guide explains how a customer's BigQuery usage becomes an estimated Snowflake compute and storage cost.
The *bigquery-to-snowflake-estimate* skill and the [Google Slot Calculator app](https://app.snowflake.com/streamlit/sfcogsops/snowhouse_aws_us_west_2/#/apps/ki4qh2k5pei7xqdkpz7k) use the same
calculation, so for the same CSV and inputs they give the same numbers. Use the app for official estimates;
the skill explains the work behind them.

## The data

The customer runs one BigQuery query (`references/bq_monthly_usage_query.sql`) against
`INFORMATION_SCHEMA.JOBS` (or `JOBS_BY_ORGANIZATION` for every project) and exports a CSV with one row
per project per month. The calculation uses two columns from each row:

| Column | Meaning |
|---|---|
| `total_slot_ms` | Slot milliseconds the project used that month |
| `active_minutes_in_month` | Wall-clock minutes with at least one query running (overlapping jobs merged) |

## Principles

1. **Every project-month is calculated on its own** with that project's own measured active time.
   Projects are never averaged together, and slot ms or active time are never pooled across projects.
2. **16 BigQuery slots = 1 X-Small Snowflake node.** This is a hardware comparison, not a pricing
   conversion. Do not call it a "credit-hour." Credits enter because a running X-Small node uses 1 credit per hour.
3. **Nodes are fractional** and never rounded up.
4. **The observed total comes first.** Step 7 is the total for the months in the data, the same number the
   app reports. Steps 8-14 project it three years forward with growth and storage.

## Steps

### Compute, per project and month (Steps 1-5)

| Step | Formula |
|---|---|
| 1. Slot hours | total_slot_ms / 3,600,000 |
| 2. Average slots | slot hours / 730 |
| 3. X-Small nodes | average slots / 16 |
| 4. Active hours | active_minutes_in_month / 60 |
| 5. Credits and cost | nodes x active hours x 1 credit per node hour; cost = credits x price per credit |

### Totals (Steps 6-8)

| Step | Formula |
|---|---|
| 6. Project total | sum of that project's months |
| 7. Snowflake total (observed) | sum of all project totals |
| 8. Projection baseline | Step 7 credits / months observed (first to last data month, inclusive; a month with no rows counts as zero) |

### 3-year projection (Steps 9-14)

| Step | Formula |
|---|---|
| 9. Month 1 storage | initial TB x (1 + time travel / failsafe %) |
| 10. Storage growth | month N TB = month N-1 TB x (1 + monthly rate); monthly rate = (1 + annual)^(1/12) - 1 |
| 11. Storage cost | month N TB x price per TB |
| 12. Compute growth | month N credits = month N-1 credits x (1 + monthly compute rate), starting at the Step 8 baseline |
| 13. Annual totals | sum of compute + storage cost for months 1-12, 13-24, 25-36 |
| 14. Range | year total x low % and x high % |

## Inputs and defaults

| Input | Default |
|---|---|
| Initial storage (TB) | Required, no default |
| Time travel / failsafe % | 0% |
| Price per TB per month | $23.00 |
| Storage growth Y1 / Y2 / Y3 | 12.7% / 12.7% / 12.7% |
| Price per credit | $4.00 (Business Critical list price) |
| Compute growth Y1 / Y2 / Y3 | 5% / 5% / 5% |
| Range low / high | 80% / 120% |

Fixed: 730 hours per month, 16 slots per X-Small node, 1 credit per X-Small node hour.

## Worked example: Sample Retail Co

7 months (March-September 2026), 7 projects, $4.00 per credit, 50 TB with 8% time travel / failsafe,
storage growth 12.7% / 10% / 8%, compute growth 5% / 7% / 7%. Files are in `sample_estimate/`.

| Result | Value |
|---|---|
| Observed total (Step 7) | 337,111.77 credits = $1,348,447.08 |
| Projection baseline (Step 8) | 48,158.82 credits/month |
| Year 1 (low - high) | $2,379,884 ($1,903,908 - $2,855,861) |
| Year 2 (low - high) | $2,525,585 ($2,020,468 - $3,030,702) |
| Year 3 (low - high) | $2,702,708 ($2,162,167 - $3,243,250) |

See [steps/](steps/README.md) for one page per step with the numbers plugged in.

## Caveats

- 16 slots = 1 X-Small node is a hardware comparison; actual throughput varies by workload (ETL, BI, ad hoc).
- The projection starts from the observed monthly average. Short observation periods, one-time loads,
  or seasonal peaks outside the window make it less reliable.
- Snowflake does not charge for bytes scanned: compute is billed in credits only while a warehouse runs, plus storage.
- Prices are list-price defaults unless overridden with customer contract values.
