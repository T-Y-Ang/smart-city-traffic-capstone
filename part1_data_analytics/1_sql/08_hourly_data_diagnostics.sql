-- Smart City Traffic Capstone
-- Diagnostic checks for selecting one observation per unique hour

-- 1. Compare total rows with unique hourly timestamps
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT date_time) AS unique_hours,
    COUNT(*) - COUNT(DISTINCT date_time) AS extra_rows
FROM Metro_Interstate_Traffic_Volume;

-- 2. Check whether duplicated timestamps contain
-- different traffic-volume values
SELECT
    date_time,
    COUNT(*) AS rows_at_hour,
    COUNT(DISTINCT traffic_volume) AS distinct_traffic_volumes,
    MIN(traffic_volume) AS min_traffic_volume,
    MAX(traffic_volume) AS max_traffic_volume
FROM Metro_Interstate_Traffic_Volume
GROUP BY date_time
HAVING COUNT(*) > 1
   AND COUNT(DISTINCT traffic_volume) > 1
ORDER BY date_time;

-- 3. Count duplicated timestamps containing
-- different temperature values
SELECT
    COUNT(*) AS duplicated_hours_with_different_temperatures
FROM (
    SELECT date_time
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
    HAVING COUNT(*) > 1
       AND COUNT(DISTINCT temp) > 1
);

-- Total rows                                      48,204
-- Unique hours                                    40,575
-- Extra rows                                       7,629
-- Duplicated hours with conflicting traffic            0
-- Duplicated hours with differing temperatures        78