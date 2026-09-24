from pathlib import Path
import logging

import mlflow
import pandas as pd


logger = logging.getLogger(__name__)


PART3_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PART3_DIR / "results"
MLFLOW_DIR = PART3_DIR / "3_mlflow"
LOGS_DIR = PART3_DIR / "logs"


def configure_logging():
    """Configure console and file logging for Task 4."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_file = LOGS_DIR / "task4_mlflow.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a"),
        ],
    )

    logger.info("Logging configured. Log file: %s", log_file)


def configure_mlflow():
    """Configure local MLflow experiment tracking with SQLite."""
    MLFLOW_DIR.mkdir(parents=True, exist_ok=True)

    database_path = MLFLOW_DIR / "mlflow.db"
    tracking_uri = f"sqlite:///{database_path.resolve()}"

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("smart_city_traffic_models")

    logger.info("MLflow tracking URI: %s", tracking_uri)
    logger.info("MLflow experiment: smart_city_traffic_models")


def log_classification_runs():
    """Log classification model results to MLflow."""
    results = pd.read_csv(RESULTS_DIR / "classification_results.csv")

    for _, row in results.iterrows():
        with mlflow.start_run(run_name=f"classification_{row['model']}"):
            mlflow.set_tag("problem_type", "classification")
            mlflow.set_tag("target", "high_risk_proxy")
            mlflow.set_tag("proxy_warning", "Demonstration proxy, not actual accident data")

            mlflow.log_param("model_type", row["model"])
            mlflow.log_param("feature_count", 24)
            mlflow.log_param("split_method", "chronological_80_20")

            mlflow.log_metric("accuracy", float(row["accuracy"]))
            mlflow.log_metric("precision", float(row["precision"]))
            mlflow.log_metric("recall", float(row["recall"]))
            mlflow.log_metric("f1", float(row["f1"]))
            mlflow.log_metric("roc_auc", float(row["roc_auc"]))

            logger.info("Logged classification run: %s.", row["model"])


def log_regression_runs():
    """Log regression model results to MLflow."""
    results = pd.read_csv(RESULTS_DIR / "regression_results.csv")

    for _, row in results.iterrows():
        with mlflow.start_run(run_name=f"regression_{row['model']}"):
            mlflow.set_tag("problem_type", "regression")
            mlflow.set_tag("target", "traffic_volume")

            mlflow.log_param("model_type", row["model"])
            mlflow.log_param("feature_count", 24)
            mlflow.log_param("split_method", "chronological_80_20")

            mlflow.log_metric("mae", float(row["mae"]))
            mlflow.log_metric("r2", float(row["r2"]))

            logger.info("Logged regression run: %s.", row["model"])


def log_neural_network_run():
    """Log neural-network results to MLflow."""
    results = pd.read_csv(RESULTS_DIR / "neural_network_results.csv")
    row = results.iloc[0]

    with mlflow.start_run(run_name="regression_Feed-forward_Neural_Network"):
        mlflow.set_tag("problem_type", "deep_learning_regression")
        mlflow.set_tag("target", "traffic_volume")

        mlflow.log_param("model_type", "Feed-forward Neural Network")
        mlflow.log_param("feature_count", 24)
        mlflow.log_param("hidden_layer_1", 64)
        mlflow.log_param("hidden_layer_2", 32)
        mlflow.log_param("optimizer", "Adam")
        mlflow.log_param("split_method", "chronological_80_20")

        mlflow.log_metric("mae", float(row["MAE"]))
        mlflow.log_metric("r2", float(row["R2"]))

        logger.info("Logged neural-network regression run.")


def main():
    """Log completed Part 3 model experiments to MLflow."""
    configure_logging()
    configure_mlflow()

    logger.info("Task 4 MLflow experiment tracking started.")

    log_classification_runs()
    log_regression_runs()
    log_neural_network_run()

    logger.info("Task 4 MLflow experiment tracking completed successfully.")


if __name__ == "__main__":
    main()