# Step 8 - Projection Baseline

**Applies to:** All projects

## Purpose

Turn the observed total into month 1 credits for the 3-year projection.

## Formula

```
Baseline Credits/Month = Snowflake Total Credits / Months Observed
```

## Example

Sample Retail Co, 7 observed months (March-September 2026), $4.00 per credit.

337,111.77 / 7 = **48,158.82 credits/month**

## Notes

Months observed = every calendar month from the first to the last month in the data, inclusive. A month inside that span with no rows counts as zero usage. Requested months before the first or after the last data month are excluded with a warning (usually outside BigQuery's ~180-day job history). The app uses the same rule.

## Next Step

[Step 9 - Month-One Storage](Step%2009%20-%20Month-One%20Storage.md)
