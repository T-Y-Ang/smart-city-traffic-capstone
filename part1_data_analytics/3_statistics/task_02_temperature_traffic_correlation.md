# Task 2.2: Correlation Between Temperature and Traffic Volume

## Method

The correlation analysis used one observation per unique hourly timestamp, consistent with the approach used for the descriptive statistics.

The original dataset contains 48,204 rows but 40,575 unique hourly timestamps. Where multiple rows occurred for the same timestamp, temperature was averaged to obtain one temperature value for that hour. Traffic volume was also aggregated by hour; duplicated timestamps were previously verified to contain the same traffic volume.

An initial data-quality check identified 10 hourly observations with a temperature of 0 K. Since 0 K is not a physically plausible ambient temperature, these observations were excluded from the primary temperature-traffic correlation analysis. This left 40,565 valid hourly observations.

Pearson's correlation coefficient was used to measure the direction and strength of the linear relationship between temperature and traffic volume.

## Results

| Measure | Value |
|---|---:|
| Valid hourly observations | 40,565 |
| Pearson correlation coefficient (r) | 0.139 |
| R-squared (R²) | 0.019 |

## Interpretation

The Pearson correlation coefficient between temperature and traffic volume is 0.139. The positive value indicates that higher temperatures tend to be associated with higher traffic volumes.

However, the correlation is weak because the coefficient is relatively close to zero. Temperature therefore has only a weak linear association with traffic volume in this dataset.

The R-squared value is 0.019, meaning that approximately 1.9% of the variation in hourly traffic volume is associated with the simple linear relationship with temperature. This indicates that temperature alone provides very limited information about variation in traffic volume.

## Sensitivity Analysis

As a sensitivity check, the Pearson correlation was recalculated without excluding the 10 observations containing temperatures of 0 K.

| Analysis | Observations | Pearson r |
|---|---:|---:|
| Excluding 0 K temperatures | 40,565 | 0.139 |
| Including 0 K temperatures | 40,575 | 0.137 |

Including the invalid 0 K temperature observations changes the correlation coefficient only slightly, from 0.139 to 0.137. Therefore, the overall interpretation remains the same: there is a weak positive linear relationship between temperature and traffic volume.

The 0 K observations were nevertheless excluded from the primary analysis because they do not represent physically plausible ambient temperatures.


## Why Correlation Does Not Imply Causation

The initial analysis found a weak positive correlation between temperature and traffic volume (Pearson r = 0.139). This indicates that higher temperatures are associated with slightly higher traffic volumes in the dataset. However, this correlation alone does not demonstrate that higher temperatures cause traffic volume to increase.

One possible explanation for the observed correlation is that temperature and traffic volume are both influenced by time of day. Temperature generally follows a daily cycle, while traffic volume also varies substantially throughout the day because of commuting and other travel patterns. Therefore, part of the observed correlation could arise because both variables change with time of day rather than because temperature directly affects traffic.

To investigate this possibility, the correlation was recalculated after accounting for the typical temperature and traffic patterns associated with each hour of the day. This reduced the correlation from 0.139 to 0.090. 

Seasonal variation was then considered as an additional potential confounding factor. Temperature varies considerably across the year, while traffic patterns may also differ between different periods of the year. The analysis was therefore repeated after accounting for both month and hour of day. The correlation decreased further to 0.035.

| Analysis | Observations | Pearson r |
|---|---:|---:|
| Original hourly correlation | 40,565 | 0.139 |
| Accounting for hour-of-day patterns | 40,565 | 0.090 |
| Accounting for month and hour-of-day patterns | 40,565 | 0.035 |

The progressive reduction in the correlation from 0.139 to 0.090 and finally to 0.035 provides evidence that temporal patterns account for a substantial part of the original association between temperature and traffic volume. After both month and hour-of-day patterns are accounted for, the remaining linear relationship is very small.

This analysis illustrates why the original correlation should not be interpreted as evidence that warmer temperatures directly cause increased traffic. A  correlation can arise because two variables are influenced by other factors. In this case, time of day and seasonal patterns are important potential confounding factors because they are associated with both temperature and traffic behaviour.

Furthermore, other factors not accounted for in this analysis may influence traffic volume, including working schedules, weekends, holidays, other weather conditions, and special events. Correlation also does not establish the direction of causation or exclude these alternative explanations. Demonstrating that temperature itself causes a change in traffic volume would require an analysis or study design that more fully controls for these potential confounding factors.

## Supporting SQL

The calculations and data-quality checks for this analysis are recorded in `09_temperature_traffic_correlation.sql`.