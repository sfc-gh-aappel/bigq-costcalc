# Step 14 — Apply Low / High Range

## Purpose

Apply a confidence band around the calculated estimate to account for the inherent uncertainty in the conversion assumptions.

## Why This Matters

This estimate rests on several assumptions — the 16-slots-to-1-X-Small-node comparison, utilization percentages, growth rates, and the time travel / failsafe %. None of these are exact. Presenting a range rather than a single number sets the right expectation with the customer and gives the account team room to position the estimate honestly.

## Inputs

| Input | Source | Description |
|---|---|---|
| Year 1, 2, 3 Total Cost | Step 13 | Calculated annual cost for each year |
| Low Range Factor | Assumption | Lower bound multiplier (default: 0.80) |
| High Range Factor | Assumption | Upper bound multiplier (default: 1.20) |

## Formulas

```
Low Estimate  = Calculated Total x 0.80
High Estimate = Calculated Total x 1.20
```

## Final Output Table

Present the estimate in this format:

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| **Low (80%)** | $X | $Y | $Z |
| **Calculated** | $X | $Y | $Z |
| **High (120%)** | $X | $Y | $Z |

## Example

Sample Retail Co:

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| **Low (80%)** | $1,800,983 | $1,911,277 | $2,045,332 |
| **Calculated** | $2,251,228 | $2,389,096 | $2,556,665 |
| **High (120%)** | $2,701,474 | $2,866,915 | $3,067,998 |

## Notes

- The 80%/120% range is a starting point. Widen it if the input data quality is low or the observation period is short.
- If the customer has seasonal workloads not captured in the observation window, consider adjusting the range or noting the gap.
- This range applies to the **total** (storage + compute). You can also present ranges separately if one component has more uncertainty than the other.

## Summary

This is the final deliverable — a three-year Snowflake cost projection with a defensible low/high range, backed by the customer's actual BigQuery consumption data.
