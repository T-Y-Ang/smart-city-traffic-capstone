from pathlib import Path
import logging
import sys

import joblib
import mlflow
import mlflow.sklearn


PART3_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PART3_DIR.parent
sys.path.append(str(PART3_DIR))

from common import COMMON_FEATURES


logger = logging.getLogger(__name__)


MODELS_DIR = PART3_DIR / "2_models"
MLFLOW_DIR = PART3_DIR / "3_mlflow"
LOGS_DIR = PART3_DIR / "logs"

REGISTERED_MODEL_NAME = "traffic_volume_prediction_model"

MODEL_VERSIONS = [
    {
        "model_path": MODELS_DIR / "linear_regression.joblib",
        "model_type": "Linear Regression",
        "version_role": "baseline",
        "mae": 720.188853,
        "r2": 0.763402,
    },
    {
        "model_path": MODELS_DIR / "random_forest_regressor.joblib",
        "model_type": "Random Forest Regression",
        "version_role": "improved_candidate",
        "mae": 249.162382,
        "r2": 0.956672,
    },
]


def configure_logging():
    """Configure console and file logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                LOGS_DIR / "model_registration.log",
                mode="a",
            ),
        ],
    )


def configure_mlflow():
    """Connect to the existing local MLflow SQLite backend."""
    database_path = MLFLOW_DIR / "mlflow.db"
    tracking_uri = f"sqlite:///{database_path.resolve()}"

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("smart_city_traffic_models")

    logger.info("MLflow tracking URI: %s", tracking_uri)


def register_model_version(model_config):
    """Log and register one existing fitted regression model."""
    model = joblib.load(model_config["model_path"])

    run_name = (
        f"versioned_{model_config['model_type'].replace(' ', '_')}"
    )

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.set_tag("problem_type", "regression")
        mlflow.set_tag("target", "traffic_volume")
        mlflow.set_tag(
            "purpose",
            "MLOps model versioning demonstration",
        )
        mlflow.set_tag(
            "version_role",
            model_config["version_role"],
        )

        mlflow.log_param(
            "model_type",
            model_config["model_type"],
        )
        mlflow.log_param(
            "feature_count",
            len(COMMON_FEATURES),
        )
        mlflow.log_param(
            "split_method",
            "chronological_80_20",
        )

        mlflow.log_metric("mae", model_config["mae"])
        mlflow.log_metric("r2", model_config["r2"])

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=REGISTERED_MODEL_NAME,
        )

        logger.info(
            "Registered %s as part of %s from run %s.",
            model_config["model_type"],
            REGISTERED_MODEL_NAME,
            run.info.run_id,
        )

        logger.info(
            "Performance: MAE %.2f, R2 %.4f.",
            model_config["mae"],
            model_config["r2"],
        )

        logger.info(
            "Logged model URI: %s",
            model_info.model_uri,
        )


def main():
    """Register successive traffic-volume model versions in MLflow."""
    configure_logging()
    configure_mlflow()

    logger.info("Model versioning registration started.")

    for model_config in MODEL_VERSIONS:
        register_model_version(model_config)

    logger.info(
        "Model versioning registration completed successfully."
    )


if __name__ == "__main__":
    main()