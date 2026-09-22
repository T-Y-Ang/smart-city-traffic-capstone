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
-- Excluding invalid 0 K temperatures: 40,565 observations, Pearson correlation 0.139
-- Including 0 K temperatures: 40,575 observations, Pearson correlation 0.137
-- the invalid temperatures have only a very small numerical effect on the correlation


-- 6. Calculate Pearson correlation and R-squared
-- using valid hourly temperature observations

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
),

correlation AS (
    SELECT
        COUNT(*) AS observations,
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
        ) AS pearson_r
    FROM valid_data, means
)

SELECT
    observations,
    ROUND(pearson_r, 3) AS pearson_r,
    ROUND(pearson_r * pearson_r, 3) AS r_squared
FROM correlation;
-- observations: 40565
-- pearson_r: 0.139
-- r_squared: 0.019


-- 7. Pearson correlation after accounting for hour-of-day patterns
-- Compare deviations from the average for each hour of day

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
        strftime('%H', date_time) AS hour_of_day,
        temp,
        traffic_volume
    FROM hourly_data
    WHERE temp > 0
),

hour_means AS (
    SELECT
        hour_of_day,
        AVG(temp) AS hour_mean_temp,
        AVG(traffic_volume) AS hour_mean_traffic
    FROM valid_data
    GROUP BY hour_of_day
),

deviations AS (
    SELECT
        v.date_time,
        v.hour_of_day,
        v.temp - h.hour_mean_temp AS temp_deviation,
        v.traffic_volume - h.hour_mean_traffic AS traffic_deviation
    FROM valid_data AS v
    JOIN hour_means AS h
        ON v.hour_of_day = h.hour_of_day
),

means AS (
    SELECT
        AVG(temp_deviation) AS mean_temp_deviation,
        AVG(traffic_deviation) AS mean_traffic_deviation
    FROM deviations
)

SELECT
    COUNT(*) AS observations,
    ROUND(
        SUM(
            (temp_deviation - mean_temp_deviation) *
            (traffic_deviation - mean_traffic_deviation)
        )
        /
        SQRT(
            SUM(
                (temp_deviation - mean_temp_deviation) *
                (temp_deviation - mean_temp_deviation)
            )
            *
            SUM(
                (traffic_deviation - mean_traffic_deviation) *
                (traffic_deviation - mean_traffic_deviation)
            )
        ),
        3
    ) AS pearson_r_within_hour
FROM deviations, means;
-- Observations: 40,565
-- Original Pearson correlation: r = 0.139
-- After accounting for hour of day: r = 0.090


-- 8. Pearson correlation after accounting for month and hour-of-day patterns
-- Compare deviations from the average for each month and hour of day

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
        strftime('%m', date_time) AS month,
        strftime('%H', date_time) AS hour_of_day,
        temp,
        traffic_volume
    FROM hourly_data
    WHERE temp > 0
),

month_hour_means AS (
    SELECT
        month,
        hour_of_day,
        AVG(temp) AS month_hour_mean_temp,
        AVG(traffic_volume) AS month_hour_mean_traffic
    FROM valid_data
    GROUP BY
        month,
        hour_of_day
),

deviations AS (
    SELECT
        v.date_time,
        v.month,
        v.hour_of_day,
        v.temp - m.month_hour_mean_temp AS temp_deviation,
        v.traffic_volume - m.month_hour_mean_traffic AS traffic_deviation
    FROM valid_data AS v
    JOIN month_hour_means AS m
        ON v.month = m.month
        AND v.hour_of_day = m.hour_of_day
),

means AS (
    SELECT
        AVG(temp_deviation) AS mean_temp_deviation,
        AVG(traffic_deviation) AS mean_traffic_deviation
    FROM deviations
)

SELECT
    COUNT(*) AS observations,
    ROUND(
        SUM(
            (temp_deviation - mean_temp_deviation) *
            (traffic_deviation - mean_traffic_deviation)
        )
        /
        SQRT(
            SUM(
                (temp_deviation - mean_temp_deviation) *
                (temp_deviation - mean_temp_deviation)
            )
            *
            SUM(
                (traffic_deviation - mean_traffic_deviation) *
                (traffic_deviation - mean_traffic_deviation)
            )
        ),
        3
    ) AS pearson_r_within_month_and_hour
FROM deviations, means;
-- Observations: 40,565
-- Original hourly correlation: 0.139
-- Accounting for hour-of-day patterns: 0.090
-- Accounting for month + hour-of-day patterns: 0.035