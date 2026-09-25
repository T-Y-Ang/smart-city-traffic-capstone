from pathlib import Path
import logging

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error

from common import (
    COMMON_FEATURES,
    REGRESSION_TARGET,
    prepare_part3_data,
)


logger = logging.getLogger(__name__)


PART3_DIR = Path(__file__).resolve().parent
MODELS_DIR = PART3_DIR / "2_models"
RESULTS_DIR = PART3_DIR / "results"
LOGS_DIR = PART3_DIR / "logs"
REPORTS_DIR = PART3_DIR / "reports"

MODEL_PATH = MODELS_DIR / "linear_regression.joblib"


def configure_logging():
    """Configure console and file logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                LOGS_DIR / "task7_responsible_ai.log",
                mode="a",
            ),
        ],
    )


def evaluate_subgroup_performance(df):
    """Evaluate regression error across operational subgroups."""
    df = df.sort_values("date_time").reset_index(drop=True)

    # Use the same chronological 80/20 split as the supervised models.
    split_index = int(len(df) * 0.80)
    test_df = df.iloc[split_index:].copy()

    model = joblib.load(MODEL_PATH)

    test_df["prediction"] = model.predict(
        test_df[COMMON_FEATURES]
    )

    test_df["absolute_error"] = (
        test_df[REGRESSION_TARGET] - test_df["prediction"]
    ).abs()

    # Human-readable operational groups.
    test_df["day_type"] = test_df["is_weekend"].map(
        {
            False: "Weekday",
            True: "Weekend",
            0: "Weekday",
            1: "Weekend",
        }
    )

    test_df["weather_group"] = "Normal"
    test_df.loc[
        test_df["is_adverse_weather"] == 1,
        "weather_group",
    ] = "Adverse Weather"

    test_df["time_period"] = pd.cut(
        test_df["hour"],
        bins=[-1, 5, 11, 17, 23],
        labels=[
            "Night",
            "Morning",
            "Afternoon",
            "Evening",
        ],
    )

    results = []

    for grouping_variable in [
        "day_type",
        "weather_group",
        "time_period",
    ]:
        for group_name, group_df in test_df.groupby(
            grouping_variable,
            observed=True,
        ):
            results.append(
                {
                    "grouping_variable": grouping_variable,
                    "group": str(group_name),
                    "observations": len(group_df),
                    "mae": mean_absolute_error(
                        group_df[REGRESSION_TARGET],
                        group_df["prediction"],
                    ),
                    "mean_actual_traffic": group_df[
                        REGRESSION_TARGET
                    ].mean(),
                    "mean_predicted_traffic": group_df[
                        "prediction"
                    ].mean(),
                }
            )

    results_df = pd.DataFrame(results)

    output_path = RESULTS_DIR / "responsible_ai_subgroup_metrics.csv"
    results_df.to_csv(output_path, index=False)

    logger.info(
        "Saved subgroup performance metrics to %s.",
        output_path,
    )

    return results_df


def create_responsible_ai_report(results_df):
    """Create a concise Responsible and Sustainable AI report."""

    def get_mae(variable, group):
        row = results_df[
            (results_df["grouping_variable"] == variable)
            & (results_df["group"] == group)
        ]
        return float(row.iloc[0]["mae"])

    weekday_mae = get_mae("day_type", "Weekday")
    weekend_mae = get_mae("day_type", "Weekend")
    adverse_mae = get_mae("weather_group", "Adverse Weather")
    normal_mae = get_mae("weather_group", "Normal")
    morning_mae = get_mae("time_period", "Morning")
    afternoon_mae = get_mae("time_period", "Afternoon")

    weather_difference = (
        (adverse_mae - normal_mae) / normal_mae * 100
    )

    report = f"""# Responsible and Sustainable AI Report

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

- Weekday MAE: {weekday_mae:.2f}
- Weekend MAE: {weekend_mae:.2f}
- Normal-weather MAE: {normal_mae:.2f}
- Adverse-weather MAE: {adverse_mae:.2f}
- Morning MAE: {morning_mae:.2f}
- Afternoon MAE: {afternoon_mae:.2f}

Prediction error during adverse weather was approximately {weather_difference:.1f}% higher than during normal weather. Error also varied
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
"""

    output_path = REPORTS_DIR / "responsible_ai_report.md"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report)

    logger.info(
        "Saved Responsible AI report to %s.",
        output_path,
    )


def main():
    """Run the Responsible AI evaluation."""
    configure_logging()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Responsible AI evaluation started.")

    df = prepare_part3_data()

    logger.info(
        "Loaded %d observations for Responsible AI evaluation.",
        len(df),
    )

    subgroup_results = evaluate_subgroup_performance(df)

    create_responsible_ai_report(subgroup_results)

    logger.info(
        "Calculated performance for %d operational subgroups.",
        len(subgroup_results),
    )

    logger.info("Responsible AI evaluation completed successfully.")


if __name__ == "__main__":
    main()