# Step 10 - Project Storage Growth

**Applies to:** Projection

## Purpose

Grow storage month by month for 36 months using each year's own annual rate.

## Formula

```
Monthly Rate = (1 + Annual Growth)^(1/12) - 1
Month N TB   = Month N-1 TB x (1 + that year's monthly rate)
```

## Example

Sample Retail Co, 7 observed months (March-September 2026), $4.00 per credit.

Y1 12.7% -> 1.0013%/mo, Y2 10% -> 0.7974%/mo, Y3 8% -> 0.6434%/mo; month 2 = 54.54 TB; month 36 = **71.58 TB**

## Notes

Default storage growth is 12.7% for each year; the sample overrides Years 2 and 3.

## Next Step

[Step 11 - Monthly Storage Cost](Step%2011%20-%20Monthly%20Storage%20Cost.md)
