-- Smart City Traffic Capstone
-- Task 1.3: Analyse temperature around holidays

-- Holiday categories contained in the dataset
SELECT DISTINCT holiday
FROM Metro_Interstate_Traffic_Volume
ORDER BY holiday;

-- New Years Day and Labor Day records for 2015-2017
SELECT
    strftime('%Y', date_time) AS year,
    holiday,
    date_time,
    temp,
    traffic_volume
FROM Metro_Interstate_Traffic_Volume
WHERE holiday IN ('New Years Day', 'Labor Day')
    AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
ORDER BY year, holiday, date_time;

-- Check for duplicate holiday records
SELECT
    holiday,
    date_time,
    temp,
    traffic_volume,
    COUNT(*) AS duplicate_count
FROM Metro_Interstate_Traffic_Volume
WHERE holiday IN ('New Years Day', 'Labor Day')
    AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
GROUP BY
    holiday,
    date_time,
    temp,
    traffic_volume
HAVING COUNT(*) > 1
ORDER BY date_time;
-- returned duplicates of New Years Day and Labor Day

-- Examine all hourly observations on the identified holiday dates
WITH holiday_dates AS (
    SELECT DISTINCT
        date(date_time) AS holiday_date,
        holiday
    FROM Metro_Interstate_Traffic_Volume
    WHERE holiday IN ('New Years Day', 'Labor Day')
        AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
)
SELECT
    strftime('%Y', h.holiday_date) AS year,
    h.holiday,
    h.holiday_date,
    t.date_time,
    t.temp,
    t.traffic_volume
FROM holiday_dates AS h
JOIN Metro_Interstate_Traffic_Volume AS t
    ON date(t.date_time) = h.holiday_date
ORDER BY h.holiday_date, t.date_time;
-- 153 rows returned with duplicates at multiple timings

-- Number of records and unique timestamps on each holiday date
WITH holiday_dates AS (
    SELECT DISTINCT
        date(date_time) AS holiday_date,
        holiday
    FROM Metro_Interstate_Traffic_Volume
    WHERE holiday IN ('New Years Day', 'Labor Day')
        AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
)
SELECT
    strftime('%Y', h.holiday_date) AS year,
    h.holiday,
    h.holiday_date,
    COUNT(*) AS total_records,
    COUNT(DISTINCT t.date_time) AS unique_timestamps
FROM holiday_dates AS h
JOIN Metro_Interstate_Traffic_Volume AS t
    ON date(t.date_time) = h.holiday_date
GROUP BY
    h.holiday_date,
    h.holiday
ORDER BY
    h.holiday_date;
-- Duplicates records especially in 2016 Labor Day (40), 2017 New Years Day (42) and 2017 Labor Day (28)

-- Calculate holiday temperature and traffic statistics
-- after collapsing duplicate timestamps

WITH holiday_dates AS (
    SELECT DISTINCT
        date(date_time) AS holiday_date,
        holiday
    FROM Metro_Interstate_Traffic_Volume
    WHERE holiday IN ('New Years Day', 'Labor Day')
        AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
),

hourly_deduplicated AS (
    SELECT
        h.holiday_date,
        h.holiday,
        t.date_time,
        AVG(t.temp) AS temp,
        AVG(t.traffic_volume) AS traffic_volume
    FROM holiday_dates AS h
    JOIN Metro_Interstate_Traffic_Volume AS t
        ON date(t.date_time) = h.holiday_date
    GROUP BY
        h.holiday_date,
        h.holiday,
        t.date_time
)

SELECT
    strftime('%Y', holiday_date) AS year,
    holiday,
    COUNT(*) AS hourly_observations,
    ROUND(AVG(temp), 2) AS avg_temp_k,
    ROUND(MIN(temp), 2) AS min_temp_k,
    ROUND(MAX(temp), 2) AS max_temp_k,
    ROUND(AVG(traffic_volume), 2) AS avg_traffic_volume
FROM hourly_deduplicated
GROUP BY
    holiday_date,
    holiday
ORDER BY
    holiday,
    holiday_date;
