-- Part 1, Task 4: SQL cross-check of the Power BI dashboard figures.
--
-- Run: python3 part1_data_analytics/sql/run_sql.py part1_data_analytics/powerbi/task4_dashboard_checks.sql
-- Uses SQLite's built-in math function sqrt (SQLite 3.35.0 or later).
--
-- Each query mirrors one dashboard element. Like the DAX measures, traffic volume
-- counts each hour once and temperature ignores 0 K readings. A weather condition
-- covers every hour that lists it, which is what filtering the table by
-- weather_main does in Power BI.

-- Query 1. Data quality figures for Task 4.1 and the KPI cards.
SELECT
    COUNT(*) AS rows_in_csv,
    9 AS columns_in_csv,
    SUM(holiday = 'None') AS holiday_none_rows,
    SUM(temp = 0) AS temp_zero_kelvin_rows,
    COUNT(DISTINCT date_time) AS total_hours_analysed,
    (
        SELECT ROUND(AVG(v), 2)
        FROM (SELECT DISTINCT date_time, traffic_volume AS v FROM traffic)
    ) AS average_traffic_volume,
    (
        SELECT ROUND(AVG(t), 2)
        FROM (
            SELECT AVG(CASE WHEN temp > 0 THEN temp END) - 273.15 AS t
            FROM traffic
            GROUP BY date_time
        )
        WHERE t IS NOT NULL
    ) AS average_temperature_c
FROM traffic;

-- Query 2. Average traffic by hour of day in 2017 (Task 4.2 B).
SELECT
    CAST(substr(date_time, 12, 2) AS INTEGER) AS hour,
    COUNT(*) AS hours,
    ROUND(AVG(traffic_volume), 1) AS average_traffic_volume
FROM (SELECT DISTINCT date_time, traffic_volume FROM traffic)
WHERE date_time >= '2017-01-01' AND date_time < '2018-01-01'
GROUP BY hour
ORDER BY hour;

-- Query 3. Average traffic by weather condition, highest first (Task 4.2 C).
WITH hour_weather AS (
    SELECT DISTINCT date_time, weather_main, traffic_volume
    FROM traffic
)
SELECT
    weather_main,
    COUNT(*) AS hours,
    ROUND(AVG(traffic_volume), 1) AS average_traffic_volume
FROM hour_weather
GROUP BY weather_main
ORDER BY AVG(traffic_volume) DESC;

-- Query 4. Highest and lowest weather condition and the difference (Task 4.2 C).
WITH by_weather AS (
    SELECT weather_main, AVG(traffic_volume) AS average_traffic_volume
    FROM (SELECT DISTINCT date_time, weather_main, traffic_volume FROM traffic)
    GROUP BY weather_main
)
SELECT
    (SELECT weather_main FROM by_weather ORDER BY average_traffic_volume DESC LIMIT 1) AS highest,
    ROUND(MAX(average_traffic_volume), 1) AS highest_average,
    (SELECT weather_main FROM by_weather ORDER BY average_traffic_volume LIMIT 1) AS lowest,
    ROUND(MIN(average_traffic_volume), 1) AS lowest_average,
    ROUND(MAX(average_traffic_volume) - MIN(average_traffic_volume), 1) AS difference
FROM by_weather;

-- Query 5. The scatter's points: one per day, x = average of the day's temperature
-- rows (the visual's "Average of Temperature (C)"), y = average traffic per hour.
-- Correlation across days and the number of days plotted (Task 4.2 D).
WITH day_temp AS (
    SELECT substr(date_time, 1, 10) AS day, AVG(temp - 273.15) AS temp_c
    FROM traffic
    WHERE temp > 0
    GROUP BY day
),
day_volume AS (
    SELECT substr(date_time, 1, 10) AS day, AVG(traffic_volume) AS volume
    FROM (SELECT DISTINCT date_time, traffic_volume FROM traffic)
    GROUP BY day
),
daily AS (
    SELECT v.day, v.volume, t.temp_c
    FROM day_volume AS v
    LEFT JOIN day_temp AS t ON t.day = v.day
),
valid AS (
    SELECT temp_c, volume FROM daily WHERE temp_c IS NOT NULL
),
means AS (
    SELECT COUNT(*) AS n, AVG(temp_c) AS mt, AVG(volume) AS mv FROM valid
)
SELECT
    (SELECT COUNT(*) FROM daily) AS days_plotted,
    ROUND(SUM((temp_c - mt) * (volume - mv)) / sqrt(SUM((temp_c - mt) * (temp_c - mt)) * SUM((volume - mv) * (volume - mv))), 3) AS r_daily,
    ROUND(MIN(temp_c), 1) AS coldest_day_c,
    ROUND(MAX(temp_c), 1) AS warmest_day_c
FROM valid, means;

-- Query 6. Daily average traffic by temperature band, to read the temperature range
-- with higher traffic (Task 4.2 D).
WITH day_temp AS (
    SELECT substr(date_time, 1, 10) AS day, AVG(temp - 273.15) AS temp_c
    FROM traffic
    WHERE temp > 0
    GROUP BY day
),
day_volume AS (
    SELECT substr(date_time, 1, 10) AS day, AVG(traffic_volume) AS volume
    FROM (SELECT DISTINCT date_time, traffic_volume FROM traffic)
    GROUP BY day
),
daily AS (
    SELECT v.day, v.volume, t.temp_c
    FROM day_volume AS v
    LEFT JOIN day_temp AS t ON t.day = v.day
)
SELECT
    printf('%d to %d', CAST(10 * floor(temp_c / 10) AS INTEGER), CAST(10 * floor(temp_c / 10) AS INTEGER) + 10) AS temperature_band_c,
    COUNT(*) AS days,
    ROUND(AVG(volume), 1) AS average_daily_traffic
FROM daily
WHERE temp_c IS NOT NULL
GROUP BY floor(temp_c / 10)
ORDER BY floor(temp_c / 10);

-- Query 7. Outlying days: the five days with the lowest average traffic per hour,
-- with their hours recorded and temperature (Task 4.2 D and the dip in 4.2 A).
WITH day_temp AS (
    SELECT substr(date_time, 1, 10) AS day, AVG(temp - 273.15) AS temp_c
    FROM traffic
    WHERE temp > 0
    GROUP BY day
),
day_volume AS (
    SELECT substr(date_time, 1, 10) AS day, COUNT(*) AS hours, AVG(traffic_volume) AS volume
    FROM (SELECT DISTINCT date_time, traffic_volume FROM traffic)
    GROUP BY day
),
daily AS (
    SELECT v.day, v.hours, v.volume, t.temp_c
    FROM day_volume AS v
    LEFT JOIN day_temp AS t ON t.day = v.day
)
SELECT
    day,
    substr('SunMonTueWedThuFriSat', 1 + 3 * CAST(strftime('%w', day) AS INTEGER), 3) AS weekday,
    hours,
    ROUND(temp_c, 1) AS temp_c,
    ROUND(volume, 1) AS average_traffic_volume
FROM daily
ORDER BY volume
LIMIT 5;
