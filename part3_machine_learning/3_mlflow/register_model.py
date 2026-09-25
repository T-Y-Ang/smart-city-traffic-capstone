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


MODEL_PATH = (
    PART3_DIR
    / "2_models"
    / "linear_regression.joblib"
)

MLFLOW_DIR = PART3_DIR / "3_mlflow"
LOGS_DIR = PART3_DIR / "logs"

REGISTERED_MODEL_NAME = "traffic_volume_linear_regression"


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


def register_model():
    """Log and register the saved traffic-volume regression model."""
    model = joblib.load(MODEL_PATH)

    with mlflow.start_run(
        run_name="registered_Linear_Regression_v1"
    ) as run:
        mlflow.set_tag("problem_type", "regression")
        mlflow.set_tag("target", "traffic_volume")
        mlflow.set_tag(
            "purpose",
            "MLOps model versioning demonstration",
        )

        mlflow.log_param("model_type", "Linear Regression")
        mlflow.log_param("feature_count", len(COMMON_FEATURES))
        mlflow.log_param("split_method", "chronological_80_20")

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=REGISTERED_MODEL_NAME,
        )

        logger.info(
            "Registered model %s from run %s.",
            REGISTERED_MODEL_NAME,
            run.info.run_id,
        )

        logger.info(
            "Logged model URI: %s",
            model_info.model_uri,
        )


def main():
    """Register the model in MLflow."""
    configure_logging()
    configure_mlflow()

    logger.info("Model registration started.")

    register_model()

    logger.info("Model registration completed successfully.")


if __name__ == "__main__":
    main()
