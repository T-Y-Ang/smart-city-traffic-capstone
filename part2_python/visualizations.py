from pathlib import Path
import logging
import sys

import matplotlib.pyplot as plt
import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "engineered_traffic_data.csv"
FIGURES_DIR = BASE_DIR / "figures"
LOG_FILE = BASE_DIR / "visualizations.log"


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


def plot_weekday_weekend_by_hour(df):
    """Plot average hourly traffic for weekdays and weekends."""

    hourly_profile = (
        df.groupby(["hour", "day_type"])["traffic_volume"]
        .mean()
        .unstack()
    )

    logger.debug(
        "Calculated weekday/weekend hourly traffic profile."
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    for day_type in hourly_profile.columns:
        ax.plot(
            hourly_profile.index,
            hourly_profile[day_type],
            marker="o",
            label=day_type
        )

    ax.set_title("Average Traffic Volume by Hour: Weekday vs Weekend")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Average Traffic Volume")
    ax.set_xticks(range(0, 24))
    ax.legend(title="Day Type")
    ax.grid(alpha=0.3)

    fig.tight_layout()

    output_path = (
        FIGURES_DIR / "hourly_profile_weekday_weekend.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info(
        "Figure saved successfully: %s",
        output_path
    )


def plot_traffic_distribution(df):
    """Plot the distribution of hourly traffic volume."""

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(
        df["traffic_volume"],
        bins=30,
        edgecolor="black",
        alpha=0.75
    )

    ax.set_title("Distribution of Hourly Traffic Volume")
    ax.set_xlabel("Traffic Volume")
    ax.set_ylabel("Frequency")
    ax.grid(
        axis="y",
        alpha=0.3
    )

    fig.tight_layout()

    output_path = (
        FIGURES_DIR / "traffic_volume_distribution.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info(
        "Figure saved successfully: %s",
        output_path
    )


def plot_temperature_vs_traffic(df):
    """Plot the relationship between temperature and traffic volume."""

    temperature_c = df["temp"] - 273.15

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(
        temperature_c,
        df["traffic_volume"],
        alpha=0.25,
        s=12
    )

    ax.set_title("Temperature vs Traffic Volume")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Traffic Volume")
    ax.grid(alpha=0.3)

    fig.tight_layout()

    output_path = (
        FIGURES_DIR / "temperature_vs_traffic.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info(
        "Figure saved successfully: %s",
        output_path
    )


def plot_congestion_by_hour(df):
    """Plot the percentage of congestion categories observed by hour."""

    congestion_by_hour = pd.crosstab(
        df["hour"],
        df["congestion_category"],
        normalize="index"
    ) * 100

    # Keep the congestion categories in a logical order.
    category_order = [
        category
        for category in ["Low", "Moderate", "High"]
        if category in congestion_by_hour.columns
    ]

    congestion_by_hour = congestion_by_hour[
        category_order
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    congestion_by_hour.plot(
        kind="bar",
        stacked=True,
        ax=ax
    )

    ax.set_title("Congestion Category Distribution by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Percentage of Observations (%)")
    ax.legend(
        title="Congestion Category",
        loc="upper left",
        bbox_to_anchor=(1.02, 1)
        )
    ax.grid(
        axis="y",
        alpha=0.3
    )

    fig.tight_layout()

    output_path = (
        FIGURES_DIR / "congestion_by_hour.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info(
        "Figure saved successfully: %s",
        output_path
    )


def load_engineered_data(file_path):
    """Load the engineered traffic dataset."""

    try:
        df = pd.read_csv(
            file_path,
            parse_dates=["date_time"]
        )

        logger.info(
            "Engineered dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Engineered dataset not found: %s",
            file_path
        )
        raise

    except Exception:
        logger.error(
            "Failed to load engineered dataset.",
            exc_info=True
        )
        raise


if __name__ == "__main__":

    try:
        logger.info("Traffic visualisation pipeline started.")

        FIGURES_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        df = load_engineered_data(INPUT_FILE)

        plot_weekday_weekend_by_hour(df)
        plot_traffic_distribution(df)
        plot_temperature_vs_traffic(df)
        plot_congestion_by_hour(df)

        logger.info(
            "Traffic visualisation pipeline finished successfully."
        )

    except Exception:
        logger.error(
            "Traffic visualisation pipeline failed.",
            exc_info=True
        )
        sys.exit(1)

