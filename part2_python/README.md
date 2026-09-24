# Part 2: Python Data Processing and Mini-Application

## Overview

This folder contains the Python component of the Smart City Traffic Capstone Project. The workflow cleans the raw Metro Interstate Traffic Volume dataset, performs feature engineering, generates traffic visualisations, and provides a command-line interface (CLI) for querying the processed data.

The scripts are designed to be run sequentially:

1. `pipeline.py` - clean and validate the raw dataset.
2. `feature_engineering.py` - create model-ready and analytical features.
3. `visualizations.py` - generate traffic visualisations.
4. `cli_app/traffic_cli.py` - query the processed dataset interactively from the command line.

## Environment and Dependencies

The Part 2 workflow was tested using:

- Python 3.13.13
- NumPy 2.5.2
- pandas 2.3.3
- Matplotlib 3.11.1

Install the required Python packages with:

```bash
pip install -r part2_python/requirements.txt
```

Commands in this README assume they are run from the repository root.

## 1. Data Cleaning Pipeline

Run:

```bash
python part2_python/pipeline.py
```

The script reads the raw Metro Interstate Traffic Volume CSV, validates the required schema and dates, standardises categorical fields, removes exact duplicate records, checks numerical anomalies, and imputes selected missing numerical values.

The raw dataset contains 48,204 rows and 9 columns. After removal of 17 exact duplicate rows, the cleaned dataset contains 48,187 rows and 9 columns.

Repeated timestamps are retained at this stage because they may represent different weather conditions.

Output:

```text
part2_python/data/cleaned_traffic_data.csv
```

## 2. Feature Engineering

Run:

```bash
python part2_python/feature_engineering.py
```

The feature-engineering stage creates time-based features including hour, day of week, month, year, weekend status, peak-hour status and traffic period. Both hour and day of week are represented using sine and cosine cyclical encodings.

Weather categories are converted into binary indicator variables. Repeated timestamps are then aggregated to one hourly observation while preserving the weather indicators associated with each timestamp.

A whole-day holiday indicator is created from the recorded holiday dates so that all hourly observations occurring on a holiday are identified as holiday observations.

Continuous variables including temperature, cloud coverage and traffic volume are standardised.

Traffic congestion is divided into four data-driven categories using traffic-volume quartiles:

- Low: traffic volume less than or equal to the 25th percentile (1,248.5).
- Medium: traffic volume above the 25th percentile and less than or equal to the 50th percentile (3,427.0).
- High: traffic volume above the 50th percentile and less than or equal to the 75th percentile (4,952.0).
- Severe: traffic volume above the 75th percentile.

The resulting engineered dataset contains 40,575 rows and 36 columns.

Output:

```text
part2_python/data/engineered_traffic_data.csv
```

### Debug Logging

Detailed feature-engineering calculations can be displayed by running:

```bash
python part2_python/feature_engineering.py --debug
```

This includes intermediate dataset shapes, weather indicators, scaling statistics and congestion thresholds.

## 3. Traffic Visualisations

Run:

```bash
python part2_python/visualizations.py
```

Four Matplotlib figures are generated:

- `hourly_profile_weekday_weekend.png` - average hourly traffic profiles for weekdays and weekends.
- `traffic_volume_distribution.png` - distribution of hourly traffic volume.
- `temperature_vs_traffic.png` - relationship between temperature and traffic volume.
- `congestion_by_hour.png` - congestion-category distribution by hour.

The figures are saved in:

```text
part2_python/figures/
```

Short interpretations of the figures are provided in:

```text
part2_python/task3_visualization_interpretations.md
```

## 4. Command-Line Mini-Application

Display the available commands with:

```bash
python part2_python/cli_app/traffic_cli.py --help
```

The CLI supports four traffic queries.

### Traffic Summary for a Date

```bash
python part2_python/cli_app/traffic_cli.py date 2017-06-15
```

### Highest-Traffic Periods

```bash
python part2_python/cli_app/traffic_cli.py high-traffic --top 5
```

### Weekday versus Weekend Comparison

```bash
python part2_python/cli_app/traffic_cli.py compare
```

### Recommend Lower-Traffic Travel Hours

```bash
python part2_python/cli_app/traffic_cli.py recommend --start 6 --end 22 --top 3
```

Invalid inputs are handled with clear user-facing error messages rather than raw Python tracebacks.

## Logging

Each executable script uses a module-specific logger created with:

```python
logging.getLogger(__name__)
```

Logging is written to both the console and a log file. Log records contain the timestamp, logging level, module/logger name and message.

Log files are:

- `part2_python/pipeline.log`
- `part2_python/feature_engineering.log`
- `part2_python/visualizations.log`
- `part2_python/cli_app/cli.log`

Logging levels are used as follows:

- **DEBUG** - detailed intermediate values used for troubleshooting, such as feature-engineering shapes, scaling statistics and congestion thresholds.
- **INFO** - normal workflow milestones such as successful loading, transformation and saving of data or figures.
- **WARNING** - unexpected but recoverable data-quality events, such as invalid sensor values, duplicate removal or numerical imputation.
- **ERROR** - failures or invalid inputs that prevent the requested operation from continuing as planned.

Internal processing status is recorded through logging rather than `print()`. `print()` is used only by the CLI for direct end-user output.

## Reproducing the Workflow

From the repository root, run the following commands in order:

```bash
python part2_python/pipeline.py
python part2_python/feature_engineering.py
python part2_python/visualizations.py
python part2_python/cli_app/traffic_cli.py --help
```

A successful run produces the cleaned dataset, engineered dataset, four figures and corresponding log files.

## Folder Contents

```text
part2_python/
├── cli_app/
│   ├── cli.log
│   └── traffic_cli.py
├── data/
│   ├── cleaned_traffic_data.csv
│   └── engineered_traffic_data.csv
├── figures/
│   ├── congestion_by_hour.png
│   ├── hourly_profile_weekday_weekend.png
│   ├── temperature_vs_traffic.png
│   └── traffic_volume_distribution.png
├── feature_engineering.log
├── feature_engineering.py
├── pipeline.log
├── pipeline.py
├── README.md
├── requirements.txt
├── task3_visualization_interpretations.md
├── visualizations.log
└── visualizations.py
```

## Key Findings

The processed data show clear differences between weekday and weekend traffic. Average weekday traffic volume is approximately 3,557 vehicles per hour compared with approximately 2,624 on weekends.

Weekday traffic reaches its highest average level at approximately 16:00, while the weekend peak occurs later, at approximately 13:00.

The relationship between temperature and traffic volume is weakly positive (Pearson correlation approximately 0.139), indicating that temperature alone explains little of the variation in traffic volume.

High-congestion observations are particularly concentrated in the afternoon commuting period, with approximately 70.1% of observations at 16:00 classified as High congestion under the quartile-based definition.

## Limitations

The congestion categories are relative thresholds derived from this dataset and should not be interpreted as official traffic-engineering congestion standards.

Repeated timestamps in the raw data may describe multiple weather conditions for the same hour. These are aggregated during feature engineering using binary weather indicators.

The CLI travel-hour recommendation is based on historical average traffic patterns in the dataset and is not a real-time routing or traffic prediction service.