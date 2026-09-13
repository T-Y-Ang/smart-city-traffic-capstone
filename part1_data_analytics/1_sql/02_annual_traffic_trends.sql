-- Smart City Traffic Capstone
-- Part 1: Annual traffic trends from 2012 to 2017


-- 1. Total traffic volume by year
SELECT
    strftime('%Y', date_time) AS year,
    SUM(traffic_volume) AS total_traffic
FROM Metro_Interstate_Traffic_Volume
WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
GROUP BY year
ORDER BY year;


-- 2. Year-to-year absolute and percentage change
WITH yearly AS (
    SELECT
        CAST(strftime('%Y', date_time) AS INTEGER) AS year,
        SUM(traffic_volume) AS total_traffic
    FROM Metro_Interstate_Traffic_Volume
    WHERE strftime('%Y', date_time) BETWEEN '2012' AND '2017'
    GROUP BY year
)
SELECT
    year,
    total_traffic,
    total_traffic
        - LAG(total_traffic) OVER (ORDER BY year) AS change,
    ROUND(
        100.0 * (
            total_traffic
            - LAG(total_traffic) OVER (ORDER BY year)
        )
        / LAG(total_traffic) OVER (ORDER BY year),
        2
    ) AS percentage_change
FROM yearly
ORDER BY year;