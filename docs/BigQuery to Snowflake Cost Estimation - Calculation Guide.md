# BigQuery to Snowflake Cost Estimation — Calculation Guide

This document describes the step-by-step calculations needed to estimate what a customer's BigQuery workload would cost on Snowflake. It covers both compute and storage, and produces a Year 1, Year 2, and Year 3 projection with low/high ranges.

---

## Inputs Required

You need the following data from the customer's BigQuery environment (by month, broken out by project):

| Input | Description |
|---|---|
| **Project name** | BigQuery project identifier |
| **Pricing model** | Whether the project uses **reservation** (flat-rate/editions) or **on-demand** pricing |
| **Slot milliseconds** | Total slot time consumed by queries, per month |
| **Clock time** | Wall-clock time that queries ran for, per month |
| **Starting data volume** | Total data stored in BigQuery (TB) |

You also need these Snowflake-side assumptions:

| Assumption | Description | Example |
|---|---|---|
| **Slot-to-node comparison** | 16 BigQuery slots = 1 X-Small Snowflake node (hardware comparison) | 16 |
| **Hours per month** | Standard calendar hours | 730 |
| **Price per credit** | Customer's Snowflake credit price | $4.00 (Business Critical list price) |
| **Price per TB storage** | Snowflake storage price per TB per month | $23.00 |
| **Time travel / failsafe %** | Extra storage for time travel and failsafe, as a % of active data | 0% (8% means 100 TB becomes 108 TB) |
| **Storage growth rate** | Annual storage growth, set separately for Years 1, 2, 3 | 12.7% per year |
| **Compute growth rate** | Annual compute growth, set separately for Years 1, 2, 3 | 5% per year |
| **Low / high range** | Range factors applied to each year's total | 80% / 120% |

---

## Part 1: Compute Estimation

### Step 1 — Calculate Utilization Percentage

For each pricing model (reservation and on-demand separately), calculate utilization across all months:

```
Utilization % = Total Active Minutes / Total Minutes
```

- **Total Active Minutes**: sum of minutes where queries were actively running (derived from clock time)
- **Total Minutes**: calendar minutes for every project-month that had activity

This tells you how much of the available capacity the customer actually uses. Reservation projects typically run much higher than on-demand projects.

### Step 2 — Convert Slot Milliseconds to Slot Hours

For each month, for each pricing model:

```
Slot Hours = Slot Milliseconds / (1,000 x 60 x 60)
```

This converts the raw BigQuery slot consumption metric into hours.

### Step 3 — Calculate Average Number of Slots

```
Average Slots = Slot Hours / Total Hours in Month
```

Where Total Hours in Month = 730 (standard assumption).

This gives you the average sustained slot count the customer ran during each month.

### Step 4 — Convert Slots to X-Small Snowflake Nodes

```
X-Small Nodes = Average Slots / 16
```

Where 16 BigQuery slots = 1 X-Small Snowflake node. This is a hardware comparison, not a pricing conversion.

### Step 5 — Calculate Credits per Month

```
Credits per Month = X-Small Nodes x 1 credit/hr x Hours per Month x Utilization %
```

Where:
- Hours per Month = 730
- Utilization % = the value from Step 1 (use the appropriate % for reservation vs. on-demand)

This accounts for the fact that compute is not running 24/7 — only during the utilized portion.

### Step 6 — Calculate Monthly Snowflake Compute Cost

```
Monthly Compute Cost ($) = Credits per Month x Price per Credit
```

### Step 7 — Average Across Observation Period

If you have multiple months of data (e.g., March through September):

```
Avg Monthly Credits (Reservation) = SUM(Monthly Reservation Credits) / Number of Months
Avg Monthly Credits (On-Demand)   = SUM(Monthly On-Demand Credits) / Number of Months
```

### Step 8 — Determine Starting Compute Credits

```
Starting Monthly Credits = Avg Monthly Credits (Reservation) + Avg Monthly Credits (On-Demand)
```

This is the baseline monthly credit consumption used for the projection.

---

## Part 2: Storage Estimation

### Step 9 — Calculate Month-One Storage

```
Month 1 Storage (TB) = Initial Storage (TB) x (1 + Time Travel / Failsafe %)
```

The percentage accounts for the additional storage Snowflake uses for time travel and failsafe beyond the active data. It is customer-specific — use their historical overhead if they are already on Snowflake, or estimate it from their retention settings.

### Step 10 — Project Storage Growth

Convert each year's annual rate to monthly, then grow month by month:

```
Monthly Rate = (1 + Annual Rate) ^ (1/12) - 1
Month N Storage (TB) = Month N-1 Storage x (1 + Monthly Rate for that year)
```

Months 1–12 use the Year 1 rate, 13–24 the Year 2 rate, and 25–36 the Year 3 rate.

### Step 11 — Calculate Monthly Storage Cost

```
Monthly Storage Cost ($) = Month N Storage (TB) x Price per TB
```

---

## Part 3: Multi-Year Projection

### Step 12 — Project Compute Growth

Convert each year's annual compute growth rate to monthly:

```
Monthly Rate = (1 + Annual Rate) ^ (1/12) - 1
```

Example: 5% annual = ~0.41% monthly.

Then for each of the 36 months, using the rate for the year that month falls in:

```
Month N Credits = Month N-1 Credits x (1 + Monthly Rate for that year)
Month N Compute Cost ($) = Month N Credits x Price per Credit
```

### Step 13 — Sum Annual Totals

```
Year 1 Total = SUM of monthly storage + compute cost for months 1–12
Year 2 Total = SUM of monthly storage + compute cost for months 13–24
Year 3 Total = SUM of monthly storage + compute cost for months 25–36
```

### Step 14 — Apply Low / High Range

To account for estimation uncertainty, apply a range:

```
Low Estimate  = Calculated Total x 0.80
High Estimate = Calculated Total x 1.20
```

Present the final output as:

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| **Low (80%)** | $X | $Y | $Z |
| **Calculated** | $X | $Y | $Z |
| **High (120%)** | $X | $Y | $Z |

---

## Calculation Flow Summary

```
BigQuery Source Data
        |
        v
[Step 1]  Utilization % (by pricing model)
        |
        v
[Step 2]  Slot ms  -->  Slot Hours
        |
        v
[Step 3]  Slot Hours  -->  Avg Slots
        |
        v
[Step 4]  Avg Slots  -->  X-Small Nodes  (÷ 16 slots per node)
        |
        v
[Step 5]  X-Small Nodes  -->  Credits/Month  (x 1 credit/hr x 730 hrs x Utilization %)
        |
        v
[Step 6]  Credits/Month  -->  $/Month  (x price per credit)
        |
        v
[Step 7-8]  Average across months  -->  Starting Monthly Credits
        |
        v
[Step 12]  Apply each year's growth  -->  36-month projection
        |
        v
        +--- COMPUTE TOTAL ---+
                              |
BigQuery Data Volume          |
        |                     |
        v                     |
[Step 9]   x (1 + TT/FS %)  -->  Month 1 Storage      |
        |                     |
        v                     |
[Step 10]  Apply each year's growth  -->  Monthly Storage |
        |                     |
        v                     |
[Step 11]  x $/TB  -->  Monthly Storage Cost             |
        |                     |
        v                     v
        +--- STORAGE TOTAL ---+--- COMBINED TOTAL
                                        |
                                        v
                              [Step 14]  x 0.80 / 1.20
                                        |
                                        v
                                  LOW / HIGH RANGE
```
