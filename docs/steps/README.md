# Calculation Steps

The skill (`scripts/estimate.py`) and the [Google Slot Calculator app](https://app.snowflake.com/streamlit/sfcogsops/snowhouse_aws_us_west_2/#/apps/ki4qh2k5pei7xqdkpz7k) use the same calculation.
Steps 1-5 run for **every project and month on its own**, with that project's own measured active time.
Steps 6-7 add them up; the Step 7 total is the number the app reports for the observed months.
Steps 8-14 project three years forward.

| Step | Calculation | Applies to |
|---|---|---|
| 1 | [Convert Slot Milliseconds to Slot Hours](Step%2001%20-%20Convert%20Slot%20Milliseconds%20to%20Slot%20Hours.md) | Per project-month |
| 2 | [Calculate Average Slots](Step%2002%20-%20Calculate%20Average%20Slots.md) | Per project-month |
| 3 | [Convert Slots to X-Small Nodes](Step%2003%20-%20Convert%20Slots%20to%20X-Small%20Nodes.md) | Per project-month |
| 4 | [Measured Active Hours](Step%2004%20-%20Measured%20Active%20Hours.md) | Per project-month |
| 5 | [Credits and Cost per Project-Month](Step%2005%20-%20Credits%20and%20Cost%20per%20Project-Month.md) | Per project-month |
| 6 | [Project Total](Step%2006%20-%20Project%20Total.md) | Per project |
| 7 | [Snowflake Total for the Observed Period](Step%2007%20-%20Snowflake%20Total%20for%20the%20Observed%20Period.md) | All projects |
| 8 | [Projection Baseline](Step%2008%20-%20Projection%20Baseline.md) | All projects |
| 9 | [Month-One Storage](Step%2009%20-%20Month-One%20Storage.md) | Projection |
| 10 | [Project Storage Growth](Step%2010%20-%20Project%20Storage%20Growth.md) | Projection |
| 11 | [Monthly Storage Cost](Step%2011%20-%20Monthly%20Storage%20Cost.md) | Projection |
| 12 | [Project Compute Growth](Step%2012%20-%20Project%20Compute%20Growth.md) | Projection |
| 13 | [Sum Annual Totals](Step%2013%20-%20Sum%20Annual%20Totals.md) | Projection |
| 14 | [Apply Low High Range](Step%2014%20-%20Apply%20Low%20High%20Range.md) | Projection |

Fixed values: 16 BigQuery slots = 1 X-Small node, 730 hours per month, 1 credit per X-Small node hour.
