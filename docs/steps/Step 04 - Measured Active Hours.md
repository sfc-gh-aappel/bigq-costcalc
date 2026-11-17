# Step 4 - Measured Active Hours

**Applies to:** Per project-month

## Purpose

Find how long this project actually ran queries in the month: real wall-clock time, not 24/7.

## Formula

```
Active Hours = active_minutes_in_month / 60
```

## Example

Worked example: Sample Retail Co, project **analytics-prod**, March 2026 (the largest project-month in the sample).

30,119.7 minutes / 60 = **502.0 active hours**

## Notes

`active_minutes_in_month` comes from the BigQuery query: every completed query job is clipped to its month and overlapping jobs are merged, so concurrent queries are counted once. It is capped at the hours in the calendar month. Each project uses **its own** active time; projects are never averaged together. This equals the app's hours/day x days/month.

## Next Step

[Step 5 - Credits and Cost per Project-Month](Step%2005%20-%20Credits%20and%20Cost%20per%20Project-Month.md)
