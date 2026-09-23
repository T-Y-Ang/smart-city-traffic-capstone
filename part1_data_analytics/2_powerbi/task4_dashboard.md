# Task 4: Power BI Traffic Intelligence Dashboard

Task 4 asks to prepare the traffic CSV in Power Query (data quality checks, Hour, temperature in
Celsius, Traffic Category), build visuals for daily and hourly traffic, weather impact, and
temperature against traffic, and add KPI cards and slicers.

## Files

| File | What it is |
|---|---|
| [`traffic_dashboard.pbix`](traffic_dashboard.pbix) | The Power BI Desktop report |
| [`power_query.m`](power_query.m) | The Power Query script inside the report, as text |
| [`measures.dax`](measures.dax) | The calculated columns and measures inside the report, as text |
| [`task4_dashboard_checks.sql`](task4_dashboard_checks.sql) | SQL that recomputes the dashboard figures from `traffic.db` |

The report reads the CSV from `\\wsl.localhost\Ubuntu-24.04\home\czy\metro-interstate\`. On
another machine, open **Transform data**, then **Data source settings**, and point the source at the
repository's `Metro_Interstate_Traffic_Volume.csv`.

## How the figures were checked

The dashboard was built in Power BI Desktop, and every number quoted below was recomputed in SQL.
The Results section is the unedited output of:

```bash
python3 part1_data_analytics/sql/run_sql.py part1_data_analytics/powerbi/task4_dashboard_checks.sql
```

The SQL follows the same rules as the DAX measures: traffic volume counts each hour once, and
temperature ignores physically impossible 0 K readings. The KPI cards showed 41K (40,575 hours),
3.29K, and 8.24; the hourly chart peaked at 16:00; and the weather chart ran from Clouds down to
Squall, all matching Queries 1 to 3.

## Results

### Query 1. Data quality figures for Task 4.1 and the KPI cards.

| rows_in_csv | columns_in_csv | holiday_none_rows | temp_zero_kelvin_rows | total_hours_analysed | average_traffic_volume | average_temperature_c |
|---:|---:|---:|---:|---:|---:|---:|
| 48204 | 9 | 48143 | 10 | 40575 | 3290.65 | 8.24 |

### Query 2. Average traffic by hour of day in 2017 (Task 4.2 B).

| hour | hours | average_traffic_volume |
|---:|---:|---:|
| 0 | 364 | 920.1 |
| 1 | 365 | 554.2 |
| 2 | 359 | 408.7 |
| 3 | 363 | 385.8 |
| 4 | 362 | 728.1 |
| 5 | 362 | 2161.8 |
| 6 | 362 | 4222.3 |
| 7 | 362 | 4819.5 |
| 8 | 361 | 4683.5 |
| 9 | 361 | 4475.7 |
| 10 | 363 | 4278.2 |
| 11 | 364 | 4575.0 |
| 12 | 364 | 4807.2 |
| 13 | 364 | 4810.7 |
| 14 | 365 | 5001.0 |
| 15 | 363 | 5333.4 |
| 16 | 363 | 5834.4 |
| 17 | 363 | 5484.4 |
| 18 | 364 | 4416.3 |
| 19 | 364 | 3421.5 |
| 20 | 364 | 2975.0 |
| 21 | 364 | 2796.6 |
| 22 | 364 | 2348.6 |
| 23 | 363 | 1577.2 |

### Query 3. Average traffic by weather condition, highest first (Task 4.2 C).

| weather_main | hours | average_traffic_volume |
|---|---:|---:|
| Clouds | 15127 | 3616.9 |
| Haze | 1359 | 3501.3 |
| Rain | 5563 | 3322.4 |
| Drizzle | 1792 | 3286.6 |
| Smoke | 20 | 3237.7 |
| Clear | 13371 | 3055.7 |
| Thunderstorm | 1010 | 3009.9 |
| Snow | 2795 | 3009.3 |
| Mist | 5940 | 2933.1 |
| Fog | 912 | 2703.7 |
| Squall | 4 | 2061.8 |

### Query 4. Highest and lowest weather condition and the difference (Task 4.2 C).

| highest | highest_average | lowest | lowest_average | difference |
|---|---:|---|---:|---:|
| Clouds | 3616.9 | Squall | 2061.8 | 1555.2 |

### Query 5. The scatter's points: one per day, x = average of the day's temperature rows (the visual's "Average of Temperature (C)"), y = average traffic per hour. Correlation across days and the number of days plotted (Task 4.2 D).

| days_plotted | r_daily | coldest_day_c | warmest_day_c |
|---:|---:|---:|---:|
| 1860 | 0.138 | -24.1 | 30.2 |

### Query 6. Daily average traffic by temperature band, to read the temperature range with higher traffic (Task 4.2 D).

| temperature_band_c | days | average_daily_traffic |
|---|---:|---:|
| -30 to -20 | 30 | 2934.0 |
| -20 to -10 | 136 | 3097.5 |
| -10 to 0 | 353 | 3187.3 |
| 0 to 10 | 425 | 3311.8 |
| 10 to 20 | 491 | 3366.1 |
| 20 to 30 | 424 | 3313.4 |
| 30 to 40 | 1 | 3162.0 |

### Query 7. Outlying days: the five days with the lowest average traffic per hour, with their hours recorded and temperature (Task 4.2 D and the dip in 4.2 A).

| day | weekday | hours | temp_c | average_traffic_volume |
|---|---|---:|---:|---:|
| 2016-07-23 | Sat | 24 | 22.8 | 277.3 |
| 2013-09-03 | Tue | 3 | 10.5 | 376.3 |
| 2013-01-29 | Tue | 1 | -0.8 | 434.0 |
| 2014-07-24 | Thu | 3 | 16.6 | 519.3 |
| 2014-08-08 | Fri | 2 | 19.8 | 682.0 |

## 4.1 Data quality and preparation

- **Rows and columns.** 48,204 rows and 9 columns in the CSV. Power Query adds Hour, Temperature (C),
  and Traffic Category, giving 12 columns.
- **Null or missing values.** The CSV has no empty cells. The `holiday` column writes ordinary days
  as the string `None` (48,143 rows); Power Query replaces it with null, so `holiday` is null on those
  48,143 rows and holds a holiday name on the other 61. Temperature (C) is null on 10 rows, the
  readings of 0 K, which are physically impossible and are left empty on purpose instead of showing
  -273.15 °C. Every other column is complete, and column quality showed 0% errors in all 12 columns.
- **Data types.** With type detection off, every column arrives as text. The script sets the types
  with the en-US culture, so decimals parse the same on any Windows regional format: `temp`,
  `rain_1h`, `snow_1h`, and Temperature (C) are decimal numbers; `clouds_all`, `traffic_volume`, and
  Hour are whole numbers; `date_time` is date/time; `holiday`, `weather_main`,
  `weather_description`, and Traffic Category are text.
- **Derived columns.** Hour is the hour of `date_time` (0 to 23). Temperature (C) is `temp` minus
  273.15. Traffic Category is Low below 4,500 vehicles, Medium from 4,500 to 5,500, and High above
  5,500.

## 4.2 Dashboard analysis

### A. Daily traffic trends, 2015 to 2017

The line chart plots the average traffic per hour for each day. It starts on 2015-06-11, where the
data resumes after a gap that covers the first five months of 2015. The deepest dip is 2016-07-23,
a Saturday averaging 277.3 vehicles per hour across all 24 hours, against 3,290.65 for the whole
dataset (Query 7); that day also holds the dataset's only two zero-volume hours, which points to a
recording fault or a road closure that the data cannot tell apart. Year-level comparisons are in
Task 1.2: over the months both years recorded well, 2017 averaged 7.1% more traffic than 2016.

### B. Hourly traffic patterns, 2017

Average traffic in 2017 is lowest at 03:00 (385.8 vehicles per hour) and climbs steeply from 05:00
to a morning peak at 07:00 (4,819.5). It eases to 4,278.2 at 10:00, rises through the afternoon to
the day's highest average at 16:00 (5,834.4), and falls to 1,577.2 by 23:00 (Query 2). The afternoon
peak is higher than the morning one.

### C. Weather impact

- **Highest average traffic:** Clouds, 3,616.9 vehicles per hour.
- **Lowest average traffic:** Squall, 2,061.8 vehicles per hour.
- **Difference:** 1,555.2 vehicles per hour (Query 4).

Squall covers only 4 hours and Smoke 20 (Query 3), so their averages rest on very few observations.
Among conditions with at least 900 hours, the lowest is Fog at 2,703.7, 913.2 below Clouds. These
averages also reflect when each condition tends to occur, not only the weather itself: Task 3
found that clear and cloudy hours are congested equally often once they are compared at the same
hour of day.

### D. Temperature and traffic

- **Visible relationship.** Only a weak one. The points form a broad cloud that rises slightly with
  temperature; across the 1,860 days plotted, the correlation is r = 0.138 (Query 5), close to the
  hourly r = 0.139 in Task 2, which fell to 0.035 once month and hour of day were held fixed.
- **Temperature range with higher traffic.** Days averaging 10 to 20 °C carry the most traffic
  (3,366.1 vehicles per hour), and days from 0 to 30 °C all average above 3,300. The coldest days,
  below -20 °C, average 2,934.0 (Query 6).
- **Notable outliers.** The points far below the cloud are 2016-07-23 (277.3, a full day) and days
  with only a few recorded hours, such as 2013-01-29 with 1 hour and 2014-08-08 with 2, whose
  averages describe a handful of hours rather than a day (Query 7). The warmest day averages 30.2
  °C and the coldest -24.1 °C. No point sits at -273 °C, because the 0 K readings are null.

## 4.3 KPI cards and filters

- **KPI cards:** Total Hours Analysed 40,575 (shown as 41K), Average Traffic Volume 3,290.65 (3.29K),
  and Average Temperature (C) 8.24.
- **Slicers:** Hour as a range slider (0 to 23), weather condition (`weather_main`) as a dropdown,
  and Traffic Category (High, Medium, Low). Every card and chart responds to them; the hourly and
  daily charts also keep their own year filters (2017, and 2015 to 2017).
