# Task 2.1: Traffic Volume Descriptive Statistics

## Method

The dataset contains 48,204 rows but only 40,575 unique hourly timestamps. Diagnostic analysis showed that duplicated timestamps have the same traffic volume, although some duplicated timestamps contain different weather observations.

To avoid giving hours with multiple weather records additional weight, traffic volume was aggregated to one observation per unique `date_time`. This produced 40,575 hourly traffic observations for the descriptive statistics.

Population standard deviation and population variance were used because the analysis describes the complete set of hourly observations contained in the supplied dataset.

## Results

| Statistic | Value |
|---|---:|
| Number of hourly observations | 40,575 |
| Mean | 3,290.65 |
| Median | 3,427.00 |
| Population standard deviation | 1,984.75 |
| Population variance | 3,939,226.41 |
| Minimum | 0 |
| Maximum | 7,280 |
| Range | 7,280 |

## Interpretation

The mean hourly traffic volume is 3,290.65, while the median is 3,427. This means that a typical hourly traffic observation is around 3,300 to 3,400 vehicles. The median is slightly higher than the mean, indicating that lower-volume observations contribute to pulling the mean below the median.

The population standard deviation is 1,984.75 vehicles, which is large relative to the mean of 3,290.65. This indicates substantial variation in traffic volume between different hours in the dataset.

The population variance is 3,939,226.41. This also reflects the large variability in traffic volume, although variance is expressed in squared units and is therefore less directly interpretable than the standard deviation.

Traffic volume ranges from a minimum of 0 to a maximum of 7,280, producing a range of 7,280 vehicles. This wide range provides further evidence that traffic conditions vary considerably across the hourly observations.

Overall, the descriptive statistics indicate substantial variability in hourly traffic volume. Traffic conditions range from extremely low-volume periods to much busier periods, and the relatively large standard deviation shows that traffic volumes are widely dispersed around the mean.

## Data Handling Note

If all 48,204 CSV rows were treated as independent observations, hours represented by multiple weather records would receive additional weight even though their traffic volume is unchanged. Using one observation per unique hour avoids this unequal weighting.

The SQL diagnostic checks supporting this decision are recorded in `08_hourly_data_diagnostics.sql`, while the descriptive-statistics calculations are recorded in `07_traffic_descriptive_statistics.sql`.