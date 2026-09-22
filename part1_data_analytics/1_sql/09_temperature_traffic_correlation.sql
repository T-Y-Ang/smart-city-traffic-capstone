-- Smart City Traffic Capstone
-- Task 2.2: Correlation between temperature and traffic volume

-- 1. Examine the minimum and maximum hourly temperature values

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(temp) AS temp,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS hourly_observations,
    MIN(temp) AS minimum_temp_k,
    MAX(temp) AS maximum_temp_k
FROM hourly_data;
-- Hourly observations: 40575
-- Minimum hourly temperature: 0.0 K
-- Maximum hourly temperature: 310.07 K


-- 2. Count hourly observations with a temperature of 0 K

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(temp) AS temp,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS zero_kelvin_hours
FROM hourly_data
WHERE temp = 0;
-- 10 hourly observations with a temperature of 0 K


-- 3. Inspect hourly observations with a temperature of 0 K

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(temp) AS temp,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    date_time,
    temp,
    traffic_volume
FROM hourly_data
WHERE temp = 0
ORDER BY date_time;
-- 10 rows returned, on 31 January 2014 and 2 February 2014
-- traffic volumes vary normally, therefore the problem is specifically the temperature measurement, not necessarily the whole hourly observation


-- 4. Pearson correlation between temperature and traffic volume
-- using one observation per unique hour and excluding invalid 0 K temperatures

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(temp) AS temp,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

valid_data AS (
    SELECT
        date_time,
        temp,
        traffic_volume
    FROM hourly_data
    WHERE temp > 0
),

means AS (
    SELECT
        AVG(temp) AS mean_temp,
        AVG(traffic_volume) AS mean_traffic
    FROM valid_data
)

SELECT
    COUNT(*) AS observations,
    ROUND(
        SUM(
            (temp - mean_temp) *
            (traffic_volume - mean_traffic)
        )
        /
        SQRT(
            SUM(
                (temp - mean_temp) *
                (temp - mean_temp)
            )
            *
            SUM(
                (traffic_volume - mean_traffic) *
                (traffic_volume - mean_traffic)
            )
        ),
        3
    ) AS pearson_r
FROM valid_data, means;
-- Valid hourly observations: 40,565
-- Pearson correlation: 0.139


-- 5. Pearson correlation including the 0 K temperature observations
-- for comparison with the cleaned correlation

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(temp) AS temp,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

means AS (
    SELECT
        AVG(temp) AS mean_temp,
        AVG(traffic_volume) AS mean_traffic
    FROM hourly_data
)

SELECT
    COUNT(*) AS observations,
    ROUND(
        SUM(
            (temp - mean_temp) *
            (traffic_volume - mean_traffic)
        )
        /
        SQRT(
            SUM(
                (temp - mean_temp) *
                (temp - mean_temp)
            )
            *
            SUM(
                (traffic_volume - mean_traffic) *
                (traffic_volume - mean_traffic)
            )
        ),
        3
    ) AS pearson_r
FROM hourly_data, means;