# Responsible and Sustainable AI Report

## Scope

This capstone uses historical traffic and weather data from a single traffic corridor. The dataset does not contain demographic or protected-attribute
information. Therefore, this evaluation does not claim to measure demographic fairness. Instead, it examines whether model performance is uneven across
operational conditions represented in the dataset.

## Sampling and Coverage Limitations

The findings are limited to the geographic corridor, time period, traffic patterns, and weather conditions represented by the source dataset. Performance
should not be assumed to generalise to other roads, cities, transport systems, or future traffic regimes without further validation.

Some weather and traffic conditions occur less frequently than others. Models may therefore have less evidence from which to learn uncommon conditions.

## Proxy Label Limitation

The classification task uses an engineered high-risk proxy based on congestion and adverse weather because a real accident-outcome dataset was not available.
The proxy is intended only to demonstrate a machine-learning classification workflow. It must not be interpreted as an actual probability of an accident
or used as a safety-critical accident prediction system.

## Uneven Model Performance

The Linear Regression traffic-volume model was evaluated on the chronological test set across several operational subgroups.

- Weekday MAE: 723.44
- Weekend MAE: 712.16
- Normal-weather MAE: 689.69
- Adverse-weather MAE: 781.80
- Morning MAE: 1059.78
- Afternoon MAE: 491.47

Prediction error during adverse weather was approximately 13.4% higher than during normal weather. Error also varied
substantially by time of day, with the morning period producing a considerably higher MAE than the afternoon period. This indicates that aggregate model
performance can conceal weaker performance under particular operating conditions.

These differences should be monitored before operational use. Decisions should not rely solely on a single overall performance metric.

## Governance and Human Oversight

Model outputs should be treated as decision-support information rather than automatic instructions. Deployment should include documented model versions,
input and prediction logging, performance monitoring, and thresholds for human review when performance deteriorates.

The high-risk classification proxy requires particular caution because its target is engineered rather than observed. Any future safety-related deployment
would require a validated accident dataset, appropriate domain review, and independent evaluation.

## Sustainability

Model complexity should be matched to operational need. In this project, the Random Forest regressor achieved the strongest conventional regression
performance, with an MAE of 249.16 vehicles and an R-squared value of 0.9567, compared with an MAE of 720.19 and R-squared value of 0.7634 for Linear
Regression. However, this improvement came with substantially greater storage requirements. The Linear Regression model occupied approximately 2.6 KB,
whereas the Random Forest regressor initially occupied approximately 281 MB. The feed-forward neural network occupied approximately 69 KB and also required
additional training infrastructure.

For repository and deployment purposes, lossless Joblib serialization compression reduced the stored Random Forest file from approximately 281 MB to
52 MB. Predictions from the compressed and uncompressed files were verified to be identical on a test sample. This reduced storage requirements without
changing the fitted model, and should be distinguished from model-optimisation techniques such as quantisation or pruning.

These results illustrate a practical sustainability and deployment trade-off. The most accurate model is not necessarily the least resource-intensive model.
A production system should therefore consider predictive performance together with model size, training and inference requirements, maintainability, hardware
requirements and energy consumption. Simpler models may remain appropriate where their lower resource requirements outweigh the additional predictive
accuracy offered by a more complex model.

## Conclusion

Responsible deployment requires attention to data coverage, proxy-label limitations, uneven performance across operating conditions, model monitoring,
human oversight, and computational cost. The models in this capstone are demonstration systems and should be validated on representative operational
data before real-world decision making.
