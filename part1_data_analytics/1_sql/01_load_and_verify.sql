-- Smart City Traffic Capstone
-- Part 1: Load and verify the Metro Interstate Traffic Volume dataset

-- 1. Verify the total number of rows
SELECT COUNT(*) AS total_rows
FROM Metro_Interstate_Traffic_Volume;

-- 2. Verify the table structure and column names
PRAGMA table_info(Metro_Interstate_Traffic_Volume);

-- 3. Preview the first 10 records
SELECT *
FROM Metro_Interstate_Traffic_Volume
LIMIT 10;