-- Smart City Traffic Capstone
-- Task 3: Probability and Congestion Analysis
-- Congestion is defined as traffic volume > 5,500 vehicles

-- 1. Calculate P(Congestion)
-- Use one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS total_hours,
    SUM(
        CASE
            WHEN traffic_volume > 5500 THEN 1
            ELSE 0
        END
    ) AS congested_hours,
    ROUND(
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        4
    ) AS probability_congestion
FROM hourly_data;
-- Total unique hours: 40,575
-- Congested hours (>5,500 vehicles): 6,107
-- P(Congestion): 0.1505 or 15.05%


-- 2. Inspect weather categories before defining clear weather

SELECT
    weather_main,
    COUNT(*) AS number_of_rows
FROM Metro_Interstate_Traffic_Volume
GROUP BY weather_main
ORDER BY weather_main;

-- 3. Calculate P(Clear Weather)
-- An hour is classified as clear if at least one record
-- for that timestamp has weather_main = 'Clear'

WITH hourly_weather AS (
    SELECT
        date_time,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS total_hours,
    SUM(is_clear) AS clear_weather_hours,
    ROUND(
        1.0 * SUM(is_clear) / COUNT(*),
        4
    ) AS probability_clear_weather
FROM hourly_weather;
-- Total unique hours: 40,575
-- Clear-weather hours: 13,371
-- P(Clear Weather) = 0.3295 or 32.95%


-- 4. Calculate P(Congestion AND Clear Weather)
-- Congestion: traffic volume > 5,500 vehicles
-- Clear weather: at least one record for the timestamp
-- has weather_main = 'Clear'

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS total_hours,
    SUM(
        CASE
            WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
            ELSE 0
        END
    ) AS congested_and_clear_hours,
    ROUND(
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        4
    ) AS probability_congestion_and_clear
FROM hourly_data;
-- Total unique hours: 40,575
-- Congested AND clear hours: 1,763
-- P(Congestion∩Clear) = 0.0435
-- Percentage: 4.35%


-- Therefore
-- P(Congestion) = 0.1505
-- P(Clear Weather) = 0.3295
-- P(Congestion∩Clear) = 0.0435

-- 3.2 Conditional probability

-- 5. Calculate P(Congestion | Clear Weather)
-- Conditional probability of congestion given clear weather

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    SUM(is_clear) AS clear_weather_hours,
    SUM(
        CASE
            WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
            ELSE 0
        END
    ) AS congested_and_clear_hours,
    ROUND(
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
                ELSE 0
            END
        ) / SUM(is_clear),
        4
    ) AS probability_congestion_given_clear
FROM hourly_data;
-- clear-weather hours: 13371
-- congested and clear hours: 1763
-- P(Congestion | Clear Weather) = 0.1319


-- 6. Calculate P(Clear Weather | Congestion)
-- Conditional probability of clear weather given congestion

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    SUM(
        CASE
            WHEN traffic_volume > 5500 THEN 1
            ELSE 0
        END
    ) AS congested_hours,
    SUM(
        CASE
            WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
            ELSE 0
        END
    ) AS congested_and_clear_hours,
    ROUND(
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
                ELSE 0
            END
        )
        /
        SUM(
            CASE
                WHEN traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ),
        4
    ) AS probability_clear_given_congestion
FROM hourly_data;
-- Congested hours: 6107
-- Congested and clear hours: 1763
-- P(Clear Weather | Congestion) = 0.2887


-- 7. Check whether congestion and clear weather are independent
-- If independent, P(Congestion AND Clear) = P(Congestion) * P(Clear)

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

probabilities AS (
    SELECT
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ) / COUNT(*) AS p_congestion,

        1.0 * SUM(is_clear)
            / COUNT(*) AS p_clear,

        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500 AND is_clear = 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*) AS p_congestion_and_clear

    FROM hourly_data
)

SELECT
    ROUND(p_congestion, 4) AS p_congestion,
    ROUND(p_clear, 4) AS p_clear,
    ROUND(p_congestion_and_clear, 4) AS p_congestion_and_clear,
    ROUND(p_congestion * p_clear, 4) AS p_congestion_times_p_clear
FROM probabilities;
-- P(Congestion) = 0.1505
-- P(Clear) = 0.3295
-- P(Congestion AND Clear) = 0.0435
-- P(Congestion) * P(Clear) = 0.0496
-- Therefore, since P(Congestion AND Clear) is not equal to P(Congestion) * P(Clear), congestion and clear weather are not statistically independent


-- 8. Calculate P(High Temperature | Congestion)
-- High temperature is defined as temperature > 292 K
-- Uses one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        AVG(temp) AS temp
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    SUM(
        CASE
            WHEN traffic_volume > 5500 THEN 1
            ELSE 0
        END
    ) AS congested_hours,

    SUM(
        CASE
            WHEN traffic_volume > 5500
                 AND temp > 292 THEN 1
            ELSE 0
        END
    ) AS congested_and_high_temp_hours,

    ROUND(
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500
                     AND temp > 292 THEN 1
                ELSE 0
            END
        )
        /
        SUM(
            CASE
                WHEN traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ),
        4
    ) AS probability_high_temp_given_congestion

FROM hourly_data;
-- Congested hours: 6,107
-- Congested AND high-temperature hours: 1,699
-- P(High Temperature∣Congestion) = 0.2782


-- 9. Count congested and non-congested hours in clear versus cloudy weather
-- Clear weather: weather_main = 'Clear'
-- Cloudy weather: weather_main = 'Clouds'
-- Uses one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear,
        MAX(
            CASE
                WHEN weather_main = 'Clouds' THEN 1
                ELSE 0
            END
        ) AS is_cloudy
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    SUM(
        CASE
            WHEN is_clear = 1 AND traffic_volume > 5500 THEN 1
            ELSE 0
        END
    ) AS clear_congested,

    SUM(
        CASE
            WHEN is_clear = 1 AND traffic_volume <= 5500 THEN 1
            ELSE 0
        END
    ) AS clear_not_congested,

    SUM(
        CASE
            WHEN is_cloudy = 1 AND traffic_volume > 5500 THEN 1
            ELSE 0
        END
    ) AS cloudy_congested,

    SUM(
        CASE
            WHEN is_cloudy = 1 AND traffic_volume <= 5500 THEN 1
            ELSE 0
        END
    ) AS cloudy_not_congested

FROM hourly_data;
-- Clear and congested: 1,763
-- Clear and not congested: 11,608
-- Cloudy and congested: 2,587
-- Cloudy and not congested: 12,540


-- 10. Calculate the odds ratio of congestion in clear versus cloudy weather
-- Odds ratio =
-- (clear congested / clear not congested)
-- /
-- (cloudy congested / cloudy not congested)

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear,
        MAX(
            CASE
                WHEN weather_main = 'Clouds' THEN 1
                ELSE 0
            END
        ) AS is_cloudy
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

counts AS (
    SELECT
        SUM(
            CASE
                WHEN is_clear = 1 AND traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ) AS clear_congested,

        SUM(
            CASE
                WHEN is_clear = 1 AND traffic_volume <= 5500 THEN 1
                ELSE 0
            END
        ) AS clear_not_congested,

        SUM(
            CASE
                WHEN is_cloudy = 1 AND traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ) AS cloudy_congested,

        SUM(
            CASE
                WHEN is_cloudy = 1 AND traffic_volume <= 5500 THEN 1
                ELSE 0
            END
        ) AS cloudy_not_congested
    FROM hourly_data
)

SELECT
    ROUND(
        1.0 * clear_congested / clear_not_congested,
        4
    ) AS odds_congestion_clear,

    ROUND(
        1.0 * cloudy_congested / cloudy_not_congested,
        4
    ) AS odds_congestion_cloudy,

    ROUND(
        (1.0 * clear_congested / clear_not_congested)
        /
        (1.0 * cloudy_congested / cloudy_not_congested),
        4
    ) AS odds_ratio_clear_vs_cloudy

FROM counts;
-- Odds of congestion in clear weather: 0.1519
-- Odds of congestion in cloudy weather: 0.2063
-- Odds ratio: Clear vs Cloudy: 0.7362
-- Therefore, the observed odds of congestion during clear weather are 26.4% (1 − 0.7362 = 0.2638) lower than during cloudy weather


-- 11. Check whether clear and cloudy weather occur at different times of day
-- Night is defined as 20:00-05:59
-- One observation per unique hour

WITH hourly_weather AS (
    SELECT
        date_time,
        CAST(strftime('%H', date_time) AS INTEGER) AS hour_of_day,

        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear,

        MAX(
            CASE
                WHEN weather_main = 'Clouds' THEN 1
                ELSE 0
            END
        ) AS is_cloudy

    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    SUM(is_clear) AS clear_hours,

    SUM(
        CASE
            WHEN is_clear = 1
                 AND (hour_of_day >= 20 OR hour_of_day < 6)
            THEN 1
            ELSE 0
        END
    ) AS clear_night_hours,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN is_clear = 1
                     AND (hour_of_day >= 20 OR hour_of_day < 6)
                THEN 1
                ELSE 0
            END
        ) / SUM(is_clear),
        1
    ) AS percent_clear_hours_at_night,

    SUM(is_cloudy) AS cloudy_hours,

    SUM(
        CASE
            WHEN is_cloudy = 1
                 AND (hour_of_day >= 20 OR hour_of_day < 6)
            THEN 1
            ELSE 0
        END
    ) AS cloudy_night_hours,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN is_cloudy = 1
                     AND (hour_of_day >= 20 OR hour_of_day < 6)
                THEN 1
                ELSE 0
            END
        ) / SUM(is_cloudy),
        1
    ) AS percent_cloudy_hours_at_night

FROM hourly_weather;
-- Clear hours: 13371
-- Clear hours at night: 6531
-- % of clear hours at night: 48.8%
-- Cloudy hours: 15127
-- Cloudy hours at night: 5263
-- % of cloudy hours at night: 34.8%


-- 12. Mantel-Haenszel odds ratio for congestion in clear versus cloudy weather, controlling for hour of day

WITH hourly_data AS (
    SELECT
        date_time,
        CAST(strftime('%H', date_time) AS INTEGER) AS hour_of_day,
        AVG(traffic_volume) AS traffic_volume,

        MAX(
            CASE
                WHEN weather_main = 'Clear' THEN 1
                ELSE 0
            END
        ) AS is_clear,

        MAX(
            CASE
                WHEN weather_main = 'Clouds' THEN 1
                ELSE 0
            END
        ) AS is_cloudy

    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
),

hour_counts AS (
    SELECT
        hour_of_day,

        SUM(
            CASE
                WHEN is_clear = 1 AND traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ) AS a,

        SUM(
            CASE
                WHEN is_clear = 1 AND traffic_volume <= 5500 THEN 1
                ELSE 0
            END
        ) AS b,

        SUM(
            CASE
                WHEN is_cloudy = 1 AND traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ) AS c,

        SUM(
            CASE
                WHEN is_cloudy = 1 AND traffic_volume <= 5500 THEN 1
                ELSE 0
            END
        ) AS d

    FROM hourly_data
    GROUP BY hour_of_day
),

mh_components AS (
    SELECT
        hour_of_day,
        a,
        b,
        c,
        d,
        a + b + c + d AS n,

        1.0 * a * d / (a + b + c + d) AS numerator_component,
        1.0 * b * c / (a + b + c + d) AS denominator_component

    FROM hour_counts
)

SELECT
    ROUND(
        SUM(numerator_component) /
        SUM(denominator_component),
        3
    ) AS mantel_haenszel_odds_ratio

FROM mh_components;
-- Mantel–Haenszel odds ratio: 1.006
-- Hour-adjusted odds ratio = 1.006: after comparing clear and cloudy conditions within the same hours of day, their odds of congestion are essentially the same.


-- 13. Compare the overall probability of high temperature
-- with P(High Temperature | Congestion)
-- High temperature is defined as temperature > 292 K
-- Uses one observation per unique hour

WITH hourly_data AS (
    SELECT
        date_time,
        AVG(traffic_volume) AS traffic_volume,
        AVG(temp) AS temp
    FROM Metro_Interstate_Traffic_Volume
    GROUP BY date_time
)

SELECT
    COUNT(*) AS total_hours,

    SUM(
        CASE
            WHEN temp > 292 THEN 1
            ELSE 0
        END
    ) AS high_temperature_hours,

    ROUND(
        1.0 * SUM(
            CASE
                WHEN temp > 292 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        4
    ) AS probability_high_temperature,

    SUM(
        CASE
            WHEN traffic_volume > 5500 THEN 1
            ELSE 0
        END
    ) AS congested_hours,

    SUM(
        CASE
            WHEN traffic_volume > 5500
                 AND temp > 292 THEN 1
            ELSE 0
        END
    ) AS congested_high_temperature_hours,

    ROUND(
        1.0 * SUM(
            CASE
                WHEN traffic_volume > 5500
                     AND temp > 292 THEN 1
                ELSE 0
            END
        )
        /
        SUM(
            CASE
                WHEN traffic_volume > 5500 THEN 1
                ELSE 0
            END
        ),
        4
    ) AS probability_high_temp_given_congestion

FROM hourly_data;
-- Total unique hours: 40,575
-- High-temperature hours (>292 K): 10,527
-- P(High Temperature): 0.2594 (25.94%)
-- Congested hours: 6,107
-- Congested + high-temperature hours: 1,699
-- P(High Temperature | Congestion): 0.2782 (27.82%)
-- high temperatures occurred in 25.94% of all hours, but in 27.82% of congested hours: 1.88% difference (small). No evidence that high temperature causes congestion