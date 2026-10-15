-- BigQuery to Snowflake cost estimate - usage query for the full date range
-- Returns one row per project per month (UTC). Run once and download the result as one CSV.
DECLARE range_start DATE DEFAULT DATE '{{RANGE_START}}';
DECLARE range_end   DATE DEFAULT DATE '{{RANGE_END}}'; -- exclusive: first day after the last month

WITH months AS (
  SELECT
    TIMESTAMP(d) AS month_start,
    TIMESTAMP(DATE_ADD(d, INTERVAL 1 MONTH)) AS month_end
  FROM UNNEST(GENERATE_DATE_ARRAY(range_start, DATE_SUB(range_end, INTERVAL 1 DAY), INTERVAL 1 MONTH)) AS d
),

jobs AS (
  SELECT
    j.project_id,
    FORMAT_TIMESTAMP('%Y-%m', m.month_start) AS year_month,
    m.month_start,
    m.month_end,
    j.total_slot_ms,
    j.start_time,
    j.end_time,
    -- Clip each job to its month so active time never exceeds the month
    GREATEST(j.start_time, m.month_start) AS clip_start,
    LEAST(j.end_time, m.month_end) AS clip_end
  FROM `{{REGION}}`.INFORMATION_SCHEMA.JOBS j
  JOIN months m
    ON j.creation_time >= m.month_start AND j.creation_time < m.month_end
  WHERE
    j.job_type = 'QUERY'
    AND j.statement_type != 'SCRIPT' -- Filters out procedural SQL wrapper jobs to avoid double counting
    AND j.state = 'DONE'
    AND j.start_time IS NOT NULL
    AND j.end_time IS NOT NULL
    AND j.creation_time >= TIMESTAMP(range_start)
    AND j.creation_time < TIMESTAMP(range_end)
),

-- Merge overlapping/concurrent jobs into continuous "active" intervals (wall-clock time)
ordered AS (
  SELECT *,
    MAX(clip_end) OVER (PARTITION BY project_id, year_month ORDER BY clip_start, clip_end
      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_max_end
  FROM jobs
  WHERE clip_end > clip_start
),
flagged AS (
  SELECT *,
    SUM(IF(prev_max_end IS NULL OR clip_start > prev_max_end, 1, 0))
      OVER (PARTITION BY project_id, year_month ORDER BY clip_start, clip_end ROWS UNBOUNDED PRECEDING) AS interval_id
  FROM ordered
),
intervals AS (
  SELECT project_id, year_month, interval_id, MIN(clip_start) AS s, MAX(clip_end) AS e
  FROM flagged
  GROUP BY 1, 2, 3
),
active_time AS (
  SELECT project_id, year_month, SUM(TIMESTAMP_DIFF(e, s, MILLISECOND)) / 1000 AS active_clock_seconds
  FROM intervals
  GROUP BY 1, 2
),
active_days AS (
  -- Distinct calendar days (UTC) on which the project had any running query
  SELECT project_id, year_month, COUNT(DISTINCT d) AS active_days_in_month
  FROM intervals, UNNEST(GENERATE_DATE_ARRAY(DATE(s), DATE(TIMESTAMP_SUB(e, INTERVAL 1 MILLISECOND)))) AS d
  GROUP BY 1, 2
),
totals AS (
  SELECT
    project_id,
    year_month,
    ANY_VALUE(month_start) AS month_start,
    ANY_VALUE(month_end) AS month_end,
    COUNT(1) AS total_queries,
    SUM(total_slot_ms) AS total_slot_ms,
    SUM(TIMESTAMP_DIFF(end_time, start_time, MILLISECOND)) AS total_query_ms
  FROM jobs
  GROUP BY 1, 2
)

SELECT
  t.project_id,
  t.year_month,
  t.total_queries,

  -- 1. Total Compute Time (Slot Milliseconds)
  t.total_slot_ms,

  -- 2. Sum of individual query durations (overlapping queries counted multiple times)
  ROUND(t.total_query_ms / 3.6e6, 2) AS total_real_clock_hours,

  -- 3. Overall Average Slots Used across executed queries
  ROUND(SAFE_DIVIDE(t.total_slot_ms, t.total_query_ms), 2) AS avg_slots_per_query,

  -- 4. ACTUAL wall-clock active time: time when at least one query was running (overlaps merged)
  ROUND(a.active_clock_seconds / 60, 1) AS active_minutes_in_month,
  ROUND(a.active_clock_seconds / 3600, 2) AS active_hours_in_month,
  d.active_days_in_month,
  ROUND(SAFE_DIVIDE(a.active_clock_seconds / 3600, d.active_days_in_month), 2) AS avg_active_hours_per_active_day,
  ROUND(100 * a.active_clock_seconds / TIMESTAMP_DIFF(t.month_end, t.month_start, SECOND), 2) AS pct_of_month_active,

  -- 5. Average slots in use while the project was actually active
  ROUND(SAFE_DIVIDE(t.total_slot_ms, a.active_clock_seconds * 1000), 2) AS avg_slots_while_active

FROM totals t
JOIN active_time a USING (project_id, year_month)
JOIN active_days d USING (project_id, year_month)
ORDER BY t.year_month, t.total_slot_ms DESC;
-- Adapted from the BigQ calculator at https://app.snowflake.com/streamlit/sfcogsops/snowhouse_aws_us_west_2/#/apps/icosbexzbmbas7a4gzfw
