from pathlib import Path
import logging
import sys

import numpy as np
import pandas as pd



# --------------------------------------------------
# File paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "cleaned_traffic_data.csv"
OUTPUT_FILE = BASE_DIR / "data" / "engineered_traffic_data.csv"
LOG_FILE = BASE_DIR / "feature_engineering.log"


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger(__name__)

# Enable DEBUG logging only when --debug is supplied.
if "--debug" in sys.argv:
    logger.setLevel(logging.DEBUG)

def load_cleaned_data(file_path):
    """Load the cleaned traffic dataset produced by Task 1."""

    try:
        df = pd.read_csv(file_path, parse_dates=["date_time"])

        logger.info(
            "Cleaned dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        logger.debug(
            "Input dataset shape before feature engineering: %s.",
            df.shape
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Cleaned dataset not found: %s",
            file_path,
            exc_info=True
        )
        raise

    except Exception:
        logger.error(
            "Unexpected error while loading cleaned dataset.",
            exc_info=True
        )
        raise


def create_time_features(df):
    """Create time-based and cyclical features from date_time."""

    df = df.copy()

    # Record the starting shape for this feature-engineering step.
    logger.debug(
        "Shape before time feature engineering: %s.",
        df.shape
    )

    # Basic time-based features.
    df["hour"] = df["date_time"].dt.hour
    df["day_of_week"] = df["date_time"].dt.day_name()
    df["day_of_week_num"] = df["date_time"].dt.dayofweek
    df["month"] = df["date_time"].dt.month
    df["year"] = df["date_time"].dt.year

    # Weekend / weekday features.
    df["is_weekend"] = df["date_time"].dt.dayofweek >= 5
    df["day_type"] = df["is_weekend"].map(
        {True: "Weekend", False: "Weekday"}
    )

    # Peak / off-peak features.
    # Morning peak: 07:00-09:59
    # Evening peak: 16:00-18:59
    df["is_peak_hour"] = (
        df["hour"].between(7, 9)
        | df["hour"].between(16, 18)
    )

    df["traffic_period"] = df["is_peak_hour"].map(
        {True: "Peak", False: "Off-peak"}
    )

    # Cyclical encoding of hour.
    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )
    
    # Cyclical encoding of day of week.
    df["day_of_week_sin"] = np.sin(
        2 * np.pi * df["day_of_week_num"] / 7
    )
    
    df["day_of_week_cos"] = np.cos(
        2 * np.pi * df["day_of_week_num"] / 7
    )

    logger.debug(
    "Cyclical encodings created for hour using a 24-hour period "
    "and day of week using a 7-day period."
    )

    logger.info(
        "Time features created: hour, day_of_week, day_of_week_num, "
        "month, year, is_weekend, day_type, is_peak_hour, "
        "traffic_period, hour_sin, hour_cos, day_of_week_sin, "
        "day_of_week_cos."
    )

    logger.debug(
        "Shape after time feature engineering: %s.",
        df.shape
    )

    return df


def create_hourly_weather_features(df):
    """Create one row per timestamp while preserving weather conditions as flags."""

    df = df.copy()

    logger.debug(
        "Shape before hourly weather aggregation: %s.",
        df.shape
    )

    # Create binary indicator columns for each weather_main category.
    weather_flags = pd.get_dummies(
        df["weather_main"],
        prefix="weather",
        dtype=int
    )

    weather_columns = weather_flags.columns.tolist()

    df_with_weather = pd.concat(
        [df, weather_flags],
        axis=1
    )

    logger.debug(
        "Created %d weather indicator columns: %s.",
        len(weather_columns),
        weather_columns
    )

    # Aggregate weather indicators using max so that any weather condition
    # recorded during an hour is preserved in the hourly observation.
    aggregation_rules = {
        column: "max"
        for column in weather_columns
    }

    # Retain the first value for non-weather variables because repeated
    # timestamps represent the same traffic observation.
    non_weather_columns = [
        column
        for column in df.columns
        if column not in [
            "weather_main",
            "weather_description"
        ]
    ]

    for column in non_weather_columns:
        if column != "date_time":
            aggregation_rules[column] = "first"

    hourly_df = (
        df_with_weather
        .groupby("date_time", as_index=False)
        .agg(aggregation_rules)
    )

    rows_removed = len(df) - len(hourly_df)

    logger.info(
        "Hourly weather dataset created: %d rows from %d input rows.",
        len(hourly_df),
        len(df)
    )

    logger.debug(
        "Collapsed %d repeated-timestamp rows while preserving all "
        "weather_main categories as binary indicators.",
        rows_removed
    )

    logger.debug(
        "Shape after hourly weather aggregation: %s.",
        hourly_df.shape
    )

    return hourly_df


def create_holiday_feature(df):
    """Create a whole-day binary holiday indicator."""

    df = df.copy()

    # Identify calendar dates containing a recorded holiday.
    holiday_dates = (
        df.loc[df["holiday"].notna(), "date_time"]
        .dt.normalize()
        .unique()
    )

    # Mark every hourly observation on those dates as a holiday.
    df["is_holiday"] = (
        df["date_time"]
        .dt.normalize()
        .isin(holiday_dates)
        .astype(int)
    )

    logger.debug(
        "Identified %d unique holiday dates.",
        len(holiday_dates)
    )

    logger.debug(
        "Holiday indicator counts: %s.",
        df["is_holiday"].value_counts().to_dict()
    )

    logger.info(
        "Whole-day holiday indicator created from recorded holiday dates."
    )

    return df



def create_scaled_features(df):
    """Create standardized versions of continuous numerical features."""

    df = df.copy()

    columns_to_scale = [
        "temp",
        "clouds_all",
        "traffic_volume",
    ]

    for column in columns_to_scale:
        mean_value = df[column].mean()
        std_value = df[column].std()

        logger.debug(
            "Scaling %s using mean %.4f and standard deviation %.4f.",
            column,
            mean_value,
            std_value
        )

        if std_value == 0:
            logger.error(
                "Cannot scale %s because its standard deviation is zero.",
                column
            )
            raise ValueError(
                f"Cannot scale {column}: standard deviation is zero."
            )

        df[f"{column}_scaled"] = (
            (df[column] - mean_value) / std_value
        )

    logger.info(
        "Scaled continuous features created for: %s.",
        ", ".join(columns_to_scale)
    )

    logger.debug(
        "Shape after continuous-variable scaling: %s.",
        df.shape
    )

    return df


def create_congestion_category(df):
    """Create a data-driven congestion category using traffic-volume quartiles."""

    df = df.copy()

    q1 = df["traffic_volume"].quantile(0.25)
    q2 = df["traffic_volume"].quantile(0.50)
    q3 = df["traffic_volume"].quantile(0.75)

    logger.debug(
        "Congestion thresholds calculated from traffic volume: "
        "Q1 = %.2f, Q2 = %.2f, Q3 = %.2f.",
        q1,
        q2,
        q3
    )

    df["congestion_category"] = pd.cut(
        df["traffic_volume"],
        bins=[-np.inf, q1, q2, q3, np.inf],
        labels=["Low", "Medium", "High", "Severe"],
        include_lowest=True
    )

    category_counts = df["congestion_category"].value_counts()

    logger.debug(
        "Congestion category counts: %s.",
        category_counts.to_dict()
    )

    logger.info(
        "Data-driven congestion category created using the "
        "25th, 50th, and 75th percentiles of traffic volume."
    )

    return df


if __name__ == "__main__":
    try:
        logger.info("Feature engineering pipeline started.")

        traffic_df = load_cleaned_data(INPUT_FILE)

        logger.info(
            "Dataset shape before feature engineering: %d rows, %d columns.",
            traffic_df.shape[0],
            traffic_df.shape[1]
        )

        traffic_df = create_time_features(traffic_df)
        traffic_df = create_hourly_weather_features(traffic_df)
        traffic_df = create_holiday_feature(traffic_df)
        traffic_df = create_scaled_features(traffic_df)
        traffic_df = create_congestion_category(traffic_df)

        logger.info(
            "Dataset shape after feature engineering: %d rows, %d columns.",
            traffic_df.shape[0],
            traffic_df.shape[1]
        )

        traffic_df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        logger.info(
            "Engineered dataset saved successfully to %s.",
            OUTPUT_FILE
        )

        logger.info(
            "Feature engineering pipeline finished successfully."
        )

    except Exception:
        logger.error(
            "Feature engineering pipeline failed because an unexpected "
            "error occurred.",
            exc_info=True
        )
        sys.exit(1)


