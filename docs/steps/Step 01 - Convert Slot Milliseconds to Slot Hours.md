# Step 1 - Convert Slot Milliseconds to Slot Hours

**Applies to:** Per project-month

## Purpose

Turn the BigQuery slot milliseconds for one project in one month into slot hours.

## Formula

```
Slot Hours = total_slot_ms / 3,600,000
```

## Example

Worked example: Sample Retail Co, project **analytics-prod**, March 2026 (the largest project-month in the sample).

1,411,368,954,596 / 3,600,000 = **392,047.0 slot hours**

## Notes

`total_slot_ms` from that project's row in the BigQuery CSV.

## Next Step

[Step 2 - Calculate Average Slots](Step%2002%20-%20Calculate%20Average%20Slots.md)
