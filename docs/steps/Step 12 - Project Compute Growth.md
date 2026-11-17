# Step 12 - Project Compute Growth

**Applies to:** Projection

## Purpose

Grow compute credits month by month from the Step 8 baseline, the same way as storage.

## Formula

```
Month 1 Credits = Baseline
Month N Credits = Month N-1 Credits x (1 + that year's monthly compute rate)
Compute Cost    = Credits x Price per Credit
```

## Example

Sample Retail Co, 7 observed months (March-September 2026), $4.00 per credit.

Y1 5% -> 0.4074%/mo, Y2/Y3 7% -> 0.5654%/mo; month 1 = 48,158.82 credits ($192,635.30); month 36 = **57,658.98 credits ($230,635.92)**

## Notes

Default compute growth is 5% for each year; the sample overrides Years 2 and 3.

## Next Step

[Step 13 - Sum Annual Totals](Step%2013%20-%20Sum%20Annual%20Totals.md)
