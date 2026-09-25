from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PART2_DATA_PATH = PROJECT_ROOT / "part2_python" / "data" / "engineered_traffic_data.csv"


# Weather groups used to construct the proxy accident-risk label
LOW_VISIBILITY_WEATHER = [
    "weather_Fog",
    "weather_Mist",
    "weather_Haze",
    "weather_Smoke",
]

SEVERE_WEATHER = [
    "weather_Rain",
    "weather_Snow",
    "weather_Squall",
    "weather_Thunderstorm",
]


def load_engineered_data():
    """Load the engineered traffic dataset produced in Part 2."""
    logger.info("Loading Part 2 engineered traffic dataset from %s", PART2_DATA_PATH)

    df = pd.read_csv(PART2_DATA_PATH)

    logger.info(
        "Loaded engineered traffic dataset with %d rows and %d columns",
        len(df),
        len(df.columns),
    )

    return df


def add_part3_features(df):
    """
    Create the common features and proxy target required for Part 3.

    The high_risk variable is a demonstration proxy only and does not
    represent observed accident outcomes.
    """
    df = df.copy()

    # Convert timestamp to datetime
    df["date_time"] = pd.to_datetime(df["date_time"])

    # Weather indicators for proxy risk label
    df["is_low_visibility"] = (
        df[LOW_VISIBILITY_WEATHER].max(axis=1) > 0
    ).astype(int)

    df["is_severe_weather"] = (
        df[SEVERE_WEATHER].max(axis=1) > 0
    ).astype(int)

    df["is_adverse_weather"] = (
        (df["is_low_visibility"] == 1)
        | (df["is_severe_weather"] == 1)
    ).astype(int)

    # Proxy accident-risk target
    df["high_risk"] = (
        df["congestion_category"].isin(["High", "Severe"])
        & (df["is_adverse_weather"] == 1)
    ).astype(int)

    logger.info(
        "Created Part 3 high-risk proxy: %d positive observations (%.2f%%)",
        int(df["high_risk"].sum()),
        df["high_risk"].mean() * 100,
    )

    return df


def prepare_part3_data():
    """Load Part 2 data and add the shared Part 3 features."""
    df = load_engineered_data()
    df = add_part3_features(df)

    return df


# Common predictor set used for supervised learning.
#
# Traffic volume and congestion-derived variables are deliberately excluded
# because they would leak information into the high_risk proxy classifier.
COMMON_FEATURES = [
    # Time
    "hour_sin",
    "hour_cos",
    "day_of_week_sin",
    "day_of_week_cos",
    "is_weekend",
    "is_peak_hour",
    "month",
    "year",

    # Holiday
    "is_holiday",

    # Weather measurements
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",

    # Weather encodings
    "weather_Clear",
    "weather_Clouds",
    "weather_Drizzle",
    "weather_Fog",
    "weather_Haze",
    "weather_Mist",
    "weather_Rain",
    "weather_Smoke",
    "weather_Snow",
    "weather_Squall",
    "weather_Thunderstorm",
]


CLASSIFICATION_TARGET = "high_risk"
REGRESSION_TARGET = "traffic_volume"