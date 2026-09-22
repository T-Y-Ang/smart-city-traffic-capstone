-- Smart City Traffic Capstone
-- Task 2.1: Descriptive statistics for traffic volume

-- 1. Mean traffic volume using one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS hourly_observations,
    ROUND(AVG(traffic_volume), 2) AS mean_traffic_volume
FROM hourly_data;

-- Hourly observations = 40,575
-- Mean traffic volume = 3,290.65


-- 2. Median traffic volume using one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    AVG(traffic_volume) AS median_traffic_volume
FROM (
    SELECT traffic_volume
    FROM hourly_data
    ORDER BY traffic_volume
    LIMIT 2 - (SELECT COUNT(*) FROM hourly_data) % 2
    OFFSET (SELECT (COUNT(*) - 1) / 2 FROM hourly_data)
);

-- Median traffic volume = 3,427.0


-- 3. Population standard deviation using one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

stats AS (
    SELECT
        AVG(traffic_volume) AS mean_traffic_volume
    FROM hourly_data
)

SELECT
    ROUND(
        SQRT(
            AVG(
                (traffic_volume - mean_traffic_volume) *
                (traffic_volume - mean_traffic_volume)
            )
        ),
        2
    ) AS population_standard_deviation
FROM hourly_data, stats;

-- Population standard deviation = 1,984.75


-- 4. Population variance using one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

stats AS (
    SELECT
        AVG(traffic_volume) AS mean_traffic_volume
    FROM hourly_data
)

SELECT
    ROUND(
        AVG(
            (traffic_volume - mean_traffic_volume) *
            (traffic_volume - mean_traffic_volume)
        ),
        2
    ) AS population_variance
FROM hourly_data, stats;

-- Population variance = 3,939,226.41


-- 5. Range of traffic volume using one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    MIN(traffic_volume) AS minimum_traffic_volume,
    MAX(traffic_volume) AS maximum_traffic_volume,
    MAX(traffic_volume) - MIN(traffic_volume) AS traffic_volume_range
FROM hourly_data;

-- Minimum = 0
-- Maximum = 7,280
-- Traffic volume range = 7,280


-- Final descriptive statistics
-- Number of unique hourly observations = 40,575
-- Mean = 3,290.65
-- Median = 3,427.00
-- Population standard deviation = 1,984.75
-- Population variance = 3,939,226.41
-- Minimum = 0
-- Maximum = 7,280
-- Range = 7,280