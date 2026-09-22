-- Smart City Traffic Capstone
-- Task 2.1: Descriptive statistics for traffic volume

-- 1. Mean traffic volume
SELECT
    ROUND(AVG(traffic_volume), 2) AS mean_traffic_volume
FROM Metro_Interstate_Traffic_Volume;
-- Mean traffic volume = 3259.82

-- 2. Median traffic volume
SELECT
    AVG(traffic_volume) AS median_traffic_volume
FROM (
    SELECT traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    ORDER BY traffic_volume
    LIMIT 2 - (SELECT COUNT(*) FROM Metro_Interstate_Traffic_Volume) % 2
    OFFSET (SELECT (COUNT(*) - 1) / 2 FROM Metro_Interstate_Traffic_Volume)
);
-- Median traffic volume = 3380.0

-- 3. Population standard deviation of traffic volume
WITH stats AS (
    SELECT
        AVG(traffic_volume) AS mean_traffic_volume
    FROM Metro_Interstate_Traffic_Volume
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
    ) AS standard_deviation
FROM Metro_Interstate_Traffic_Volume, stats;

-- Population standard deviation of traffic volume = 1986.84

-- 4. Population variance of traffic volume
WITH stats AS (
    SELECT
        AVG(traffic_volume) AS mean_traffic_volume
    FROM Metro_Interstate_Traffic_Volume
)
SELECT
    ROUND(
        AVG(
            (traffic_volume - mean_traffic_volume) *
            (traffic_volume - mean_traffic_volume)
        ),
        2
    ) AS variance
FROM Metro_Interstate_Traffic_Volume, stats;

-- Population variance = 396047533.3

-- 5. Range of traffic volume
SELECT
    MIN(traffic_volume) AS minimum_traffic_volume,
    MAX(traffic_volume) AS maximum_traffic_volume,
    MAX(traffic_volume) - MIN(traffic_volume) AS traffic_volume_range
FROM Metro_Interstate_Traffic_Volume;

-- Range of traffic volume
-- Minimum = 0
-- Maximum = 7280
-- Traffic volume range = 7280

-- Statistics of traffic
-- Mean = 3,259.82
-- Median = 3,380.00
-- Population standard deviation = 1,986.84
-- Population variance = 3,947,533.43
-- Minimum = 0
-- Maximum = 7,280
-- Range = 7,280