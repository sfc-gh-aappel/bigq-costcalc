# Step 9 — Calculate Month-One Storage

## Purpose

Estimate the total Snowflake storage footprint in month one by adding the time travel / failsafe percentage to the customer's starting data volume.

## Why This Matters

Snowflake stores more than just the active data. Time travel (allows querying/restoring historical data) and failsafe (disaster recovery buffer) create additional storage that doesn't exist in BigQuery. The time travel / failsafe percentage accounts for this overhead.

## Inputs

| Input | Source | Description |
|---|---|---|
| Initial Storage Volume (TB) | Customer | Total active data stored in BigQuery |
| Time Travel / Failsafe % | Customer-specific | Extra storage as a percentage of active data (default: 0%) |

## Formula

```
Month 1 Storage (TB) = Initial Storage (TB) x (1 + Time Travel / Failsafe %)
```

## Notes on the Time Travel / Failsafe %

- An 8% value means 100 TB of active data becomes 108 TB of Snowflake storage.
- It is **customer-specific**. If the customer is already on Snowflake, use their historical overhead; otherwise estimate it from their planned retention settings.
- Default time travel is 1 day (Enterprise: up to 90 days). Failsafe is 7 days and cannot be disabled.

## Example

| Input | Value |
|---|---|
| Initial Storage | 50 TB |
| Time Travel / Failsafe % | 8% |
| **Month 1 Storage** | **54 TB** |

## Output

Month-one total Snowflake storage in TB — carried forward to Step 10 for growth projection.

## Next Step

[Step 10 — Project Storage Growth](Step%2010%20-%20Project%20Storage%20Growth.md)
