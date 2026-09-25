from pathlib import Path
import logging
import sys

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error


PART3_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PART3_DIR))

from common import (
    COMMON_FEATURES,
    REGRESSION_TARGET,
    prepare_part3_data,
)


logger = logging.getLogger(__name__)


MODEL_PATH = (
    PART3_DIR
    / "2_models"
    / "linear_regression.joblib"
)

RESULTS_DIR = PART3_DIR / "results"
LOGS_DIR = PART3_DIR / "logs"


def configure_logging():
    """Configure console and file logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                LOGS_DIR / "model_monitoring.log",
                mode="a",
            ),
        ],
    )


def monitor_prediction_error(df):
    """Compare prediction error between earlier and later test windows."""
    df = df.sort_values("date_time").reset_index(drop=True)

    # Reproduce the chronological 80/20 split used during Task 1.
    split_index = int(len(df) * 0.80)
    test_df = df.iloc[split_index:].copy()

    # Divide the test period into an earlier reference window
    # and a later monitoring window.
    midpoint = len(test_df) // 2

    reference_df = test_df.iloc[:midpoint].copy()
    monitoring_df = test_df.iloc[midpoint:].copy()

    model = joblib.load(MODEL_PATH)

    reference_predictions = model.predict(
        reference_df[COMMON_FEATURES]
    )

    monitoring_predictions = model.predict(
        monitoring_df[COMMON_FEATURES]
    )

    reference_mae = mean_absolute_error(
        reference_df[REGRESSION_TARGET],
        reference_predictions,
    )

    monitoring_mae = mean_absolute_error(
        monitoring_df[REGRESSION_TARGET],
        monitoring_predictions,
    )

    mae_change_percent = (
        (monitoring_mae - reference_mae)
        / reference_mae
        * 100
    )

    # Demonstration monitoring threshold:
    # alert when MAE worsens by more than 20%.
    threshold_percent = 20.0

    if mae_change_percent > threshold_percent:
        status = "ALERT - Requires investigation"
    else:
        status = "PASS - Normal"

    monitoring_results = pd.DataFrame(
        [
            {
                "reference_start": reference_df["date_time"].min(),
                "reference_end": reference_df["date_time"].max(),
                "monitoring_start": monitoring_df["date_time"].min(),
                "monitoring_end": monitoring_df["date_time"].max(),
                "reference_observations": len(reference_df),
                "monitoring_observations": len(monitoring_df),
                "reference_mae": reference_mae,
                "monitoring_mae": monitoring_mae,
                "mae_change_percent": mae_change_percent,
                "alert_threshold_percent": threshold_percent,
                "status": status,
            }
        ]
    )

    output_path = RESULTS_DIR / "model_monitoring_results.csv"
    monitoring_results.to_csv(output_path, index=False)

    logger.info(
        "Reference MAE: %.2f | Monitoring MAE: %.2f | "
        "Change: %.2f%% | Status: %s",
        reference_mae,
        monitoring_mae,
        mae_change_percent,
        status,
    )

    logger.info(
        "Saved monitoring results to %s.",
        output_path,
    )

    return monitoring_results


def main():
    """Run prediction-error monitoring."""
    configure_logging()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Model monitoring started.")

    df = prepare_part3_data()

    logger.info(
        "Loaded %d observations for monitoring.",
        len(df),
    )

    monitoring_results = monitor_prediction_error(df)

    logger.info("Model monitoring completed successfully.")


if __name__ == "__main__":
    main()