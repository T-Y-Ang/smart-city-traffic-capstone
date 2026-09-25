from pathlib import Path
import logging

import pandas as pd

from common import prepare_part3_data


logger = logging.getLogger(__name__)


PART3_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PART3_DIR / "results"
LOGS_DIR = PART3_DIR / "logs"


def configure_logging():
    """Configure console and file logging for Task 5."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_file = LOGS_DIR / "task5_recommendation.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a"),
        ],
    )

    logger.info("Logging configured. Log file: %s", log_file)


def build_travel_recommendations(df):
    """Generate travel-timing recommendations from historical traffic patterns."""
    analysis_df = df.copy()

    # Create a simple weather category for recommendation purposes.
    analysis_df["recommendation_weather"] = "Normal"

    analysis_df.loc[
        analysis_df["is_low_visibility"] == 1,
        "recommendation_weather",
    ] = "Low Visibility"

    analysis_df.loc[
        analysis_df["is_severe_weather"] == 1,
        "recommendation_weather",
    ] = "Severe Weather"

    # Convert weekend indicator into a readable day type.
    analysis_df["day_type"] = analysis_df["is_weekend"].map(
        {
            False: "Weekday",
            True: "Weekend",
            0: "Weekday",
            1: "Weekend",
        }
    )

    recommendations = (
        analysis_df.groupby(
            [
                "day_type",
                "recommendation_weather",
                "hour",
            ],
            observed=True,
        )
        .agg(
            mean_traffic_volume=("traffic_volume", "mean"),
            median_traffic_volume=("traffic_volume", "median"),
            observations=("traffic_volume", "size"),
        )
        .reset_index()
    )

    # Rank hours within each day-type/weather combination.
    recommendations["traffic_rank"] = (
        recommendations.groupby(
            [
                "day_type",
                "recommendation_weather",
            ]
        )["mean_traffic_volume"]
        .rank(method="dense", ascending=True)
        .astype(int)
    )

    recommendations = recommendations.sort_values(
        [
            "day_type",
            "recommendation_weather",
            "traffic_rank",
        ]
    )

    output_path = RESULTS_DIR / "travel_timing_recommendations.csv"
    recommendations.to_csv(output_path, index=False)

    logger.info(
        "Saved travel-timing recommendation table to %s.",
        output_path,
    )

    return recommendations


def summarise_best_travel_windows(recommendations, top_n=3):
    """Extract the lowest-traffic travel windows for each context."""
    best_windows = (
        recommendations[
            recommendations["traffic_rank"] <= top_n
        ]
        .copy()
        .sort_values(
            [
                "day_type",
                "recommendation_weather",
                "traffic_rank",
            ]
        )
    )

    output_path = RESULTS_DIR / "best_travel_windows.csv"
    best_windows.to_csv(output_path, index=False)

    logger.info(
        "Saved best travel windows to %s.",
        output_path,
    )

    return best_windows


def create_plain_language_recommendations(best_windows):
    """Create plain-language travel-timing recommendations."""
    messages = []

    grouped = best_windows.groupby(
        ["day_type", "recommendation_weather"],
        sort=True,
    )

    for (day_type, weather), group in grouped:
        group = group.sort_values("traffic_rank")

        hours = [
            f"{int(hour):02d}:00"
            for hour in group["hour"]
        ]

        best_hour = group.iloc[0]

        message = (
            f"For {day_type.lower()} travel during "
            f"{weather.lower()} conditions, the historically lower-traffic "
            f"travel hours are {', '.join(hours)}. "
            f"The lowest mean traffic volume in this group occurred at "
            f"{int(best_hour['hour']):02d}:00 "
            f"(approximately {best_hour['mean_traffic_volume']:.0f} vehicles)."
        )

        messages.append(message)

    output_path = RESULTS_DIR / "travel_recommendations.txt"

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(
            "SMART CITY TRAFFIC — TRAVEL-TIMING RECOMMENDATIONS\n\n"
        )

        file.write(
            "These recommendations are based on historical traffic patterns "
            "for a single traffic corridor. They recommend travel timing, "
            "not alternative physical routes, and do not guarantee future "
            "traffic conditions.\n\n"
        )

        for message in messages:
            file.write(f"- {message}\n")

    logger.info(
        "Saved plain-language recommendations to %s.",
        output_path,
    )

    return messages


def main():
    """Run the travel-timing recommendation workflow."""
    configure_logging()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Task 5 travel-timing recommendation started.")

    df = prepare_part3_data()

    logger.info(
        "Prepared dataset with %d observations for recommendation analysis.",
        len(df),
    )

    recommendations = build_travel_recommendations(df)

    best_windows = summarise_best_travel_windows(
        recommendations,
        top_n=3,
    )

    messages = create_plain_language_recommendations(
        best_windows
    )

    logger.info(
        "Generated %d recommended travel windows.",
        len(best_windows),
    )

    logger.info(
        "Task 5 travel-timing recommendation completed successfully."
    )


if __name__ == "__main__":
    main()