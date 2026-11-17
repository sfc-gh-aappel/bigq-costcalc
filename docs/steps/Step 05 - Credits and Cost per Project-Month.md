# Step 5 - Credits and Cost per Project-Month

**Applies to:** Per project-month

## Purpose

Combine nodes and active hours into Snowflake credits, then price them.

## Formula

```
Credits = X-Small Nodes x Active Hours x 1 credit per X-Small node hour
Cost    = Credits x Price per Credit
```

## Example

Worked example: Sample Retail Co, project **analytics-prod**, March 2026 (the largest project-month in the sample).

33.5657 x 502.0 = **16,849.79 credits**; 16,849.79 x $4.00 = **$67,399.18**

## Notes

An X-Small warehouse uses 1 credit per hour while it runs. Steps 1-5 run for every project and month in the CSV.

## Next Step

[Step 6 - Project Total](Step%2006%20-%20Project%20Total.md)
