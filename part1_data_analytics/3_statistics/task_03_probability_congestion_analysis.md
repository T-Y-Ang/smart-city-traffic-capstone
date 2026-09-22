# Probability and Congestion Analysis

Congestion was defined as an hourly traffic volume greater than 5,500 vehicles. Because the dataset contains duplicate timestamps, the primary analysis used one observation per unique hour. Where multiple records shared the same timestamp, traffic volume was averaged. This prevents hours containing multiple weather records from being given greater weight simply because they appear more than once in the dataset.

## Basic Probabilities

The probability of congestion was:

- P(Congestion) = 0.1505

Therefore, approximately 15.05% of the unique hourly observations were classified as congested.

Clear weather was defined using the `weather_main` category `Clear`. An hour was classified as clear if at least one weather record for that timestamp had `weather_main = 'Clear'`.

The probability of clear weather was:

- P(Clear Weather) = 0.3295

Therefore, approximately 32.95% of the unique hourly observations were classified as having clear weather.

The joint probability of congestion and clear weather was:

- P(Congestion AND Clear Weather) = 0.0435

Therefore, approximately 4.35% of all unique hourly observations experienced both congestion and clear weather.

## What the Probability Analysis Suggests

The probability analysis initially suggests that weather conditions are associated with congestion. Across the 40,575 unique hourly observations, the probability of congestion was 0.1505 (15.05%), while the probability of clear weather was 0.3295 (32.95%). The joint probability of congestion and clear weather was 0.0435 (4.35%).

If congestion and clear weather were independent, the expected joint probability would be:

P(Congestion) × P(Clear Weather)
= 0.1505 × 0.3295
≈ 0.0496.

The observed joint probability of 0.0435 is lower than the expected value of approximately 0.0496. Similarly, P(Clear Weather | Congestion) was 0.2887 (28.87%), compared with the overall P(Clear Weather) of 0.3295 (32.95%). These results indicate that clear weather and congestion are not statistically independent in the unadjusted data.

The unadjusted odds ratio provides a similar result. The odds of congestion during clear weather were 0.1519, compared with 0.2063 during cloudy weather, producing an odds ratio of 0.7362. Thus, before accounting for other factors, congestion appeared less common during clear hours than during cloudy hours.

However, this apparent relationship is strongly influenced by the time of the day. Approximately 48.8% of clear-weather hours occurred between 20:00 and 05:59, compared with 34.8% of cloudy-weather hours. These are predominantly lower-traffic hours, so the different time-of-day distributions can make clear weather appear to be associated with less congestion.

After controlling for hour of day using a Mantel-Haenszel analysis, the odds ratio was 1.006. An odds ratio this close to 1 indicates that, when clear and cloudy observations are compared at the same hour of day, their odds of congestion are approximately equal. Therefore, the apparent association between clear weather and lower congestion in the unadjusted analysis is largely explained by the different times of day at which clear and cloudy conditions occur.

Temperature shows a similarly small association. High temperature was defined as greater than 292 K. High-temperature conditions occurred during 25.94% of all hourly observations, compared with 27.82% of congested hours, a difference of only 1.88 percentage points. High temperatures were therefore slightly more common during congested periods, but this does not establish that high temperature causes congestion.

This interpretation is consistent with the earlier correlation analysis. The Pearson correlation between temperature and traffic volume was initially 0.139, but decreased to 0.090 after accounting for hour of day and to 0.035 after accounting for both month and hour of day. Together, these results show the importance of temporal confounding: both weather and traffic vary according to time of day and season.

Overall, the analysis provides little evidence that clear versus cloudy weather itself has a substantial relationship with congestion once time of day is taken into account. Congestion appears to be much more strongly associated with temporal traffic patterns. The present comparison concerns clear and cloudy conditions only; other weather categories such as rain, snow, fog and thunderstorms have not been evaluated in this analysis and could have different relationships with congestion.