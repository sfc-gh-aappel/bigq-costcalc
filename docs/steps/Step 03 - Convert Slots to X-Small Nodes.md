# Step 3 - Convert Slots to X-Small Nodes

**Applies to:** Per project-month

## Purpose

Translate average slots into equivalent X-Small Snowflake nodes.

## Formula

```
X-Small Nodes = Average Slots / 16
```

## Example

Worked example: Sample Retail Co, project **analytics-prod**, March 2026 (the largest project-month in the sample).

537.05 / 16 = **33.5657 X-Small nodes**

## Notes

16 BigQuery slots = 1 X-Small node is a hardware comparison, not a pricing conversion. Nodes are fractional and are never rounded up.

## Next Step

[Step 4 - Measured Active Hours](Step%2004%20-%20Measured%20Active%20Hours.md)
