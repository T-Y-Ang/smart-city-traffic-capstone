from pathlib import Path
import logging
import pandas as pd
import sys

# Set up project paths
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "pipeline.log"
DATA_FILE = (
    BASE_DIR.parent
    / "part1_data_analytics"
    / "data"
    / "Metro_Interstate_Traffic_Volume.csv"
)
OUTPUT_DIR = BASE_DIR / "data"
CLEANED_DATA_FILE = OUTPUT_DIR / "cleaned_traffic_data.csv"
HOURLY_DATA_FILE = OUTPUT_DIR / "hourly_traffic_data.csv"

# Configure logging
# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_data(file_path):
    """Load the traffic CSV file with error handling."""
    try:
        df = pd.read_csv(file_path)
        logger.info(
            "Dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )
        return df

    except FileNotFoundError:
        logger.error("Dataset not found: %s", file_path)
        raise

    except pd.errors.EmptyDataError:
        logger.error("Dataset is empty: %s", file_path)
        raise

    except Exception:
        logger.exception("Unexpected error while loading dataset.")
        raise


def validate_schema(df):
    """Check that all required columns are present in the dataset."""

    required_columns = {
        "holiday",
        "temp",
        "rain_1h",
        "snow_1h",
        "clouds_all",
        "weather_main",
        "weather_description",
        "date_time",
        "traffic_volume",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        logger.error(
            "Schema validation failed. Missing columns: %s",
            sorted(missing_columns)
        )
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    logger.info("Schema validation passed: all required columns are present.")

def parse_dates(df):
    """Convert date_time to datetime and check for invalid values."""

    df = df.copy()

    df["date_time"] = pd.to_datetime(
        df["date_time"],
        errors="coerce"
    )

    invalid_dates = df["date_time"].isna().sum()

    if invalid_dates > 0:
        logger.warning(
            "Found %d invalid date_time values.",
            invalid_dates
        )
    else:
        logger.info("Date validation passed: no invalid date_time values found.")

    return df

def standardize_categories(df):
    """Standardize categorical text values."""

    df = df.copy()

    categorical_columns = [
        "holiday",
        "weather_main",
        "weather_description",
    ]

    for column in categorical_columns:
        df[column] = df[column].astype("string").str.strip()

    # Non-holiday entries are already read by pandas as missing values.
    logger.info(
        "Holiday check completed: %d non-holiday entries are represented "
        "as missing values.",
        df["holiday"].isna().sum()
        )
        
    logger.info(
        "Categorical standardization completed for: %s.",
        ", ".join(categorical_columns)
    )

    return df


def remove_duplicates(df):
    """Remove exact duplicate rows while preserving valid repeated timestamps."""

    df = df.copy()

    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        df = df.drop_duplicates()

        logger.warning(
            "Dropped %d exact duplicate rows because they were duplicate records. "
            "%d rows remain.",
            duplicate_rows,
            len(df)
        )
    else:
        logger.info("Duplicate check completed: no exact duplicate rows found.")

    repeated_timestamps = df.duplicated(
        subset=["date_time"],
        keep=False
    ).sum()

    logger.info(
        "Repeated-timestamp check completed: %d rows belong to repeated "
        "timestamps and were retained because they may represent different "
        "weather conditions.",
        repeated_timestamps
    )

    return df


def clean_numeric_anomalies(df):
    """Detect and replace physically impossible numeric values."""

    df = df.copy()

    # Temperature must be above absolute zero.
    invalid_temp = df["temp"] <= 0
    invalid_temp_count = invalid_temp.sum()

    if invalid_temp_count > 0:
        df.loc[invalid_temp, "temp"] = pd.NA

        logger.warning(
            "Modified %d temperature values to missing because values "
            "at or below 0 K are physically invalid.",
            invalid_temp_count
        )
    else:
        logger.info(
            "Temperature validation completed: no physically invalid values found."
        )

    # Negative rainfall is physically invalid.
    invalid_rain_negative = df["rain_1h"] < 0
    invalid_rain_count = invalid_rain_negative.sum()

    if invalid_rain_count > 0:
        df.loc[invalid_rain_negative, "rain_1h"] = pd.NA

        logger.warning(
            "Modified %d negative rainfall values to missing because "
            "negative rainfall is physically invalid.",
            invalid_rain_count
        )
    else:
        logger.info(
            "Negative rainfall validation completed: no invalid values found."
        )

    # Negative snowfall is physically invalid.
    invalid_snow_negative = df["snow_1h"] < 0
    invalid_snow_count = invalid_snow_negative.sum()

    if invalid_snow_count > 0:
        df.loc[invalid_snow_negative, "snow_1h"] = pd.NA

        logger.warning(
            "Modified %d negative snowfall values to missing because "
            "negative snowfall is physically invalid.",
            invalid_snow_count
        )
    else:
        logger.info(
            "Negative snowfall validation completed: no invalid values found."
        )

    # Extremely high hourly rainfall is treated as an implausible sensor value.
    extreme_rain = df["rain_1h"] > 500
    extreme_rain_count = extreme_rain.sum()

    if extreme_rain_count > 0:
        df.loc[extreme_rain, "rain_1h"] = pd.NA

        logger.warning(
            "Modified %d rainfall values above 500 mm/hour to missing "
            "because they were considered implausible sensor values.",
            extreme_rain_count
        )
    else:
        logger.info(
            "Extreme rainfall validation completed: no values above "
            "500 mm/hour found."
        )

    return df


def impute_missing_values(df):
    """Impute missing numeric sensor values using appropriate medians."""

    df = df.copy()

    # Impute missing temperature values using the median
    # temperature for the corresponding month.
    missing_temp_count = df["temp"].isna().sum()

    if missing_temp_count > 0:
        for month in sorted(df["date_time"].dt.month.dropna().unique()):
            month_mask = df["date_time"].dt.month == month
            missing_temp_mask = month_mask & df["temp"].isna()

            monthly_missing_count = missing_temp_mask.sum()

            if monthly_missing_count > 0:
                monthly_median = df.loc[month_mask, "temp"].median()

                df.loc[missing_temp_mask, "temp"] = monthly_median

                logger.warning(
                    "Imputed %d missing temperature values for month %d "
                    "using monthly median %.2f K because temperature "
                    "varies seasonally.",
                    monthly_missing_count,
                    month,
                    monthly_median
                )
    else:
        logger.info(
            "Missing-value check for temp completed: "
            "no values required imputation."
        )

    # Impute rainfall and snowfall using their overall medians.
    for column in ["rain_1h", "snow_1h"]:
        missing_count = df[column].isna().sum()

        if missing_count > 0:
            median_value = df[column].median()
            df[column] = df[column].fillna(median_value)

            logger.warning(
                "Imputed %d missing values in %s using median %.2f "
                "because missing sensor values require replacement "
                "for downstream analysis.",
                missing_count,
                column,
                median_value
            )
        else:
            logger.info(
                "Missing-value check for %s completed: "
                "no values required imputation.",
                column
            )

    return df


def save_cleaned_data(cleaned_df):
    """Save the cleaned dataset for downstream analysis."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_df.to_csv(CLEANED_DATA_FILE, index=False)

    logger.info(
        "Saved cleaned dataset: %d rows, %d columns to %s.",
        cleaned_df.shape[0],
        cleaned_df.shape[1],
        CLEANED_DATA_FILE
    )


if __name__ == "__main__":
    try:
        logger.info("Traffic data cleaning pipeline started.")

        traffic_df = load_data(DATA_FILE)
        validate_schema(traffic_df)
        traffic_df = parse_dates(traffic_df)
        traffic_df = standardize_categories(traffic_df)
        traffic_df = remove_duplicates(traffic_df)
        traffic_df = clean_numeric_anomalies(traffic_df)
        traffic_df = impute_missing_values(traffic_df)

        save_cleaned_data(traffic_df)

        logger.info("Traffic data cleaning pipeline finished successfully.")

    except Exception:
        logger.error(
            "Traffic data pipeline failed because an unexpected error occurred.",
            exc_info=True
            )
        sys.exit(1)