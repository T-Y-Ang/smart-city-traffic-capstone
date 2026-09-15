-- Smart City Traffic Capstone
-- Check the amount of traffic data available for each year

SELECT
    strftime('%Y', date_time) AS year,
    COUNT(*) AS number_of_records,
    MIN(date_time) AS first_record,
    MAX(date_time) AS last_record
FROM Metro_Interstate_Traffic_Volume
GROUP BY year
ORDER BY year;