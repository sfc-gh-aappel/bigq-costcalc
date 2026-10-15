# BigQuery to Snowflake Cost Conversion Steps

Step-by-step calculation guide for estimating what a customer's BigQuery workload would cost on Snowflake.

---

## Part 1: Compute Estimation

| Step | Title | Description |
|---|---|---|
| [Step 1](Step%2001%20-%20Calculate%20Utilization%20Percentage.md) | Calculate Utilization Percentage | Active minutes / total minutes, by pricing model |
| [Step 2](Step%2002%20-%20Convert%20Slot%20Milliseconds%20to%20Slot%20Hours.md) | Convert Slot Milliseconds to Slot Hours | Raw BQ metric to usable unit |
| [Step 3](Step%2003%20-%20Calculate%20Average%20Number%20of%20Slots.md) | Calculate Average Number of Slots | Slot hours / 730 hours per month |
| [Step 4](Step%2004%20-%20Convert%20Slots%20to%20X-Small%20Nodes.md) | Convert Slots to X-Small Nodes | 16 slots = 1 X-Small node |
| [Step 5](Step%2005%20-%20Calculate%20Credits%20per%20Month.md) | Calculate Credits per Month | X-Small nodes x 1 credit/hr x 730 hrs x utilization % |
| [Step 6](Step%2006%20-%20Calculate%20Monthly%20Compute%20Cost.md) | Calculate Monthly Compute Cost | Credits x price per credit |
| [Step 7](Step%2007%20-%20Average%20Across%20Observation%20Period.md) | Average Across Observation Period | Smooth monthly variation into a baseline |
| [Step 8](Step%2008%20-%20Determine%20Starting%20Compute%20Credits.md) | Determine Starting Compute Credits | Sum reservation + on-demand averages |

## Part 2: Storage Estimation

| Step | Title | Description |
|---|---|---|
| [Step 9](Step%2009%20-%20Calculate%20Month-One%20Storage.md) | Calculate Month-One Storage | Initial TB x (1 + time travel/failsafe %) |
| [Step 10](Step%2010%20-%20Project%20Storage%20Growth.md) | Project Storage Growth | Apply each year's annual storage growth over 36 months |
| [Step 11](Step%2011%20-%20Calculate%20Monthly%20Storage%20Cost.md) | Calculate Monthly Storage Cost | Storage TB x price per TB |

## Part 3: Multi-Year Projection

| Step | Title | Description |
|---|---|---|
| [Step 12](Step%2012%20-%20Project%20Compute%20Growth.md) | Project Compute Growth | Apply each year's annual compute growth over 36 months |
| [Step 13](Step%2013%20-%20Sum%20Annual%20Totals.md) | Sum Annual Totals | Aggregate monthly costs into annual figures |
| [Step 14](Step%2014%20-%20Apply%20Low%20High%20Range.md) | Apply Low / High Range | 80% low / 120% high confidence band |

---

## Key Assumptions

| Assumption | Default Value | Notes |
|---|---|---|
| Slot-to-node comparison | 16 slots = 1 X-Small node | Hardware comparison; discuss with account team |
| Hours per month | 730 | Standard |
| Reservation / on-demand utilization | Calculated | From the customer's BigQuery data |
| Price per credit | $4.00 | Business Critical list price; use the customer's rate if known |
| Price per TB storage | $23.00 | Use the customer's rate if known |
| Time travel / failsafe % | 0% | Customer-specific |
| Storage growth rate | 12.7% annual (Years 1, 2, 3 set separately) | Adjustable |
| Compute growth rate | 5% annual (Years 1, 2, 3 set separately) | Adjustable |
| Low / high range | 80% / 120% | Adjustable |
| Low/high range | 80% / 120% | Adjustable based on confidence |
