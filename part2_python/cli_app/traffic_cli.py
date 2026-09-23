from pathlib import Path
import argparse
import logging
import sys

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

CLI_DIR = Path(__file__).resolve().parent
PART2_DIR = CLI_DIR.parent

DATA_FILE = PART2_DIR / "data" / "engineered_traffic_data.csv"
LOG_FILE = CLI_DIR / "cli.log"


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


def load_data():
    """Load the processed traffic dataset."""

    try:
        df = pd.read_csv(
            DATA_FILE,
            parse_dates=["date_time"]
        )

        logger.info(
            "Processed dataset loaded successfully: %d rows, %d columns.",
            df.shape[0],
            df.shape[1]
        )

        return df

    except FileNotFoundError:
        logger.error(
            "Processed dataset not found: %s",
            DATA_FILE
        )

        print(
            "ERROR: Processed traffic dataset could not be found."
        )

        sys.exit(1)

    except Exception as error:
        logger.error(
            "Failed to load processed dataset: %s",
            error
        )

        print(
            "ERROR: The processed traffic dataset could not be loaded."
        )

        sys.exit(1)


def query_date(df, date_string):
    """Display traffic information for a specific date."""

    try:
        query_date_value = pd.to_datetime(
            date_string,
            format="%Y-%m-%d",
            errors="raise"
        )

    except ValueError:
        logger.error(
            "Invalid date supplied to date command: %s",
            date_string
        )

        print(
            "ERROR: Invalid date. Please use YYYY-MM-DD format."
        )

        return

    daily_data = df[
        df["date_time"].dt.date
        == query_date_value.date()
    ].copy()

    if daily_data.empty:
        logger.error(
            "No traffic data found for date: %s",
            date_string
        )

        print(
            f"ERROR: No traffic data found for {date_string}."
        )

        return

    daily_data = daily_data.sort_values("date_time")

    average_traffic = daily_data["traffic_volume"].mean()

    peak_row = daily_data.loc[
        daily_data["traffic_volume"].idxmax()
    ]

    print(f"\nTraffic summary for {date_string}")
    print("-" * 40)
    print(f"Number of hourly records: {len(daily_data)}")
    print(f"Average traffic volume: {average_traffic:.1f}")
    print(
        "Highest traffic volume: "
        f"{peak_row['traffic_volume']:.0f} "
        f"at {peak_row['date_time']:%H:%M}"
    )
    print(
        f"Congestion category at peak: "
        f"{peak_row['congestion_category']}"
    )


def identify_high_traffic(df, top_n=5):
    """Identify the hours with the highest average traffic volume."""

    hourly_traffic = (
        df.groupby("hour")["traffic_volume"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )

    print(f"\nTop {top_n} high-traffic periods")
    print("-" * 40)

    for hour, average_traffic in hourly_traffic.items():
        print(
            f"{int(hour):02d}:00 - "
            f"Average traffic volume: {average_traffic:.1f}"
        )


def compare_weekday_weekend(df):
    """Compare average weekday and weekend traffic volume."""

    comparison = (
        df.groupby("day_type")["traffic_volume"]
        .agg(["mean", "median", "count"])
    )

    print("\nWeekday vs Weekend Traffic Comparison")
    print("-" * 50)

    for day_type, row in comparison.iterrows():
        print(f"\n{day_type}")
        print(f"  Average traffic volume: {row['mean']:.1f}")
        print(f"  Median traffic volume:  {row['median']:.1f}")
        print(f"  Number of observations: {int(row['count'])}")

    if (
        "Weekday" in comparison.index
        and "Weekend" in comparison.index
    ):
        difference = (
            comparison.loc["Weekday", "mean"]
            - comparison.loc["Weekend", "mean"]
        )

        print("\nDifference in average traffic volume")
        print(f"  Weekday - Weekend: {difference:.1f}")


def recommend_travel_periods(df, start_hour=6, end_hour=22, top_n=3):
    """Recommend lower-traffic hours within a specified time range."""

    filtered_data = df[
        (df["hour"] >= start_hour)
        & (df["hour"] <= end_hour)
    ]

    hourly_traffic = (
        filtered_data.groupby("hour")["traffic_volume"]
        .mean()
        .sort_values()
        .head(top_n)
    )

    print(
        f"\nRecommended Travel Periods "
        f"({start_hour:02d}:00 to {end_hour:02d}:00)"
    )
    print("-" * 50)

    for hour, average_traffic in hourly_traffic.items():
        print(
            f"{int(hour):02d}:00 - "
            f"Average traffic volume: {average_traffic:.1f}"
        )


def build_parser():
    """Create and configure the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Smart City Traffic Analysis CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # --------------------------------------------------
    # Command 1: date
    # --------------------------------------------------

    date_parser = subparsers.add_parser(
        "date",
        help="Query traffic information for a specific date."
    )

    date_parser.add_argument(
        "date",
        help="Date in YYYY-MM-DD format."
    )

    # --------------------------------------------------
    # Command 2: high-traffic
    # --------------------------------------------------

    high_traffic_parser = subparsers.add_parser(
        "high-traffic",
        help="Identify hours with the highest average traffic."
    )

    high_traffic_parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of high-traffic periods to display (default: 5)."
    )

    # --------------------------------------------------
    # Command 3: compare
    # --------------------------------------------------

    subparsers.add_parser(
        "compare",
        help="Compare weekday and weekend traffic."
    )

    # --------------------------------------------------
    # Command 4: recommend
    # --------------------------------------------------

    recommend_parser = subparsers.add_parser(
        "recommend",
        help="Recommend lower-traffic travel periods."
    )

    recommend_parser.add_argument(
        "--start",
        type=int,
        default=6,
        help="Start hour from 0 to 23 (default: 6)."
    )

    recommend_parser.add_argument(
        "--end",
        type=int,
        default=22,
        help="End hour from 0 to 23 (default: 22)."
    )

    recommend_parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of recommended periods to display (default: 3)."
    )

    return parser


def main():
    """Run the Smart City Traffic Analysis CLI."""

    parser = build_parser()
    args = parser.parse_args()

    logger.info(
        "Command invoked: %s | arguments: %s",
        args.command,
        vars(args)
    )

    df = load_data()

    if args.command == "date":
        query_date(
            df,
            args.date
        )

    elif args.command == "high-traffic":

        if args.top <= 0:
            logger.error(
                "Invalid --top value for high-traffic: %s",
                args.top
            )

            print(
                "ERROR: --top must be greater than 0."
            )

            return

        identify_high_traffic(
            df,
            top_n=args.top
        )

    elif args.command == "compare":
        compare_weekday_weekend(df)

    elif args.command == "recommend":

        if not (
            0 <= args.start <= 23
            and 0 <= args.end <= 23
        ):
            logger.error(
                "Invalid hour range for recommend: "
                "start=%s, end=%s",
                args.start,
                args.end
            )

            print(
                "ERROR: --start and --end must be "
                "between 0 and 23."
            )

            return

        if args.start > args.end:
            logger.error(
                "Start hour is later than end hour: "
                "start=%s, end=%s",
                args.start,
                args.end
            )

            print(
                "ERROR: --start cannot be later than --end."
            )

            return

        if args.top <= 0:
            logger.error(
                "Invalid --top value for recommend: %s",
                args.top
            )

            print(
                "ERROR: --top must be greater than 0."
            )

            return

        recommend_travel_periods(
            df,
            start_hour=args.start,
            end_hour=args.end,
            top_n=args.top
        )


if __name__ == "__main__":
    main()

