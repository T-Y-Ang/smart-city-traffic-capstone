from pathlib import Path
import logging

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from common import (
    CLASSIFICATION_TARGET,
    COMMON_FEATURES,
    REGRESSION_TARGET,
    prepare_part3_data,
)


logger = logging.getLogger(__name__)


# Project paths
PART3_DIR = Path(__file__).resolve().parent
MODELS_DIR = PART3_DIR / "2_models"
RESULTS_DIR = PART3_DIR / "results"
LOGS_DIR = PART3_DIR / "logs"


def ensure_output_directories():
    """Create output directories required by the supervised-learning task."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging():
    """Configure console and file logging for Task 1."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_file = LOGS_DIR / "task1_supervised.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a"),
        ],
    )

    logger.info("Logging configured. Log file: %s", log_file)


def chronological_train_test_split(df, test_size=0.20):
    """Split the dataset chronologically into training and test sets."""
    df = df.sort_values("date_time").reset_index(drop=True)

    split_index = int(len(df) * (1 - test_size))

    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    logger.info(
        "Chronological split created: %d training rows and %d test rows.",
        len(train_df),
        len(test_df),
    )

    logger.info(
        "Training period: %s to %s.",
        train_df["date_time"].min(),
        train_df["date_time"].max(),
    )

    logger.info(
        "Test period: %s to %s.",
        test_df["date_time"].min(),
        test_df["date_time"].max(),
    )

    return train_df, test_df


def train_classification_models(train_df, test_df):
    """Train and evaluate models for the high-risk proxy classification task."""
    X_train = train_df[COMMON_FEATURES]
    X_test = test_df[COMMON_FEATURES]

    y_train = train_df[CLASSIFICATION_TARGET]
    y_test = test_df[CLASSIFICATION_TARGET]

    models = {
        "Logistic Regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }

    results = []

    for model_name, model in models.items():
        logger.info("Training classification model: %s.", model_name)

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        metrics = {
            "problem": "classification",
            "model": model_name,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_prob),
        }

        results.append(metrics)

        logger.info(
            "%s results - Accuracy: %.4f, Precision: %.4f, "
            "Recall: %.4f, F1: %.4f, ROC AUC: %.4f.",
            model_name,
            metrics["accuracy"],
            metrics["precision"],
            metrics["recall"],
            metrics["f1"],
            metrics["roc_auc"],
        )

    return pd.DataFrame(results), models


def train_regression_models(train_df, test_df):
    """Train and evaluate models for traffic-volume prediction."""
    X_train = train_df[COMMON_FEATURES]
    X_test = test_df[COMMON_FEATURES]

    y_train = train_df[REGRESSION_TARGET]
    y_test = test_df[REGRESSION_TARGET]

    models = {
        "Linear Regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LinearRegression()),
            ]
        ),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
        ),
    }

    results = []

    for model_name, model in models.items():
        logger.info("Training regression model: %s.", model_name)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        metrics = {
            "problem": "regression",
            "model": model_name,
            "mae": mean_absolute_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
        }

        results.append(metrics)

        logger.info(
            "%s results - MAE: %.2f, R2: %.4f.",
            model_name,
            metrics["mae"],
            metrics["r2"],
        )

    return pd.DataFrame(results), models


def save_models(classification_models, regression_models):
    """Save trained supervised-learning models to disk."""
    model_files = {
        "logistic_regression_classifier.joblib":
            classification_models["Logistic Regression"],
        "random_forest_classifier.joblib":
            classification_models["Random Forest"],
        "linear_regression.joblib":
            regression_models["Linear Regression"],
        "random_forest_regressor.joblib":
            regression_models["Random Forest"],
    }

    for filename, model in model_files.items():
        model_path = MODELS_DIR / filename
        joblib.dump(model, model_path)
        logger.info("Saved trained model to %s.", model_path)


def main():
    """Run the supervised-learning workflow."""
    configure_logging()
    ensure_output_directories()

    logger.info("Task 1 supervised-learning pipeline started.")

    df = prepare_part3_data()

    logger.info(
        "Prepared Part 3 dataset with %d rows and %d columns.",
        len(df),
        len(df.columns),
    )

    train_df, test_df = chronological_train_test_split(df)
    
    logger.info(
        "High-risk proxy prevalence: training=%.2f%%, test=%.2f%%.",
        train_df[CLASSIFICATION_TARGET].mean() * 100,
        test_df[CLASSIFICATION_TARGET].mean() * 100,
    )

    classification_results, classification_models = train_classification_models(
        train_df,
        test_df,
    )

    print("\nClassification results")
    print("-" * 80)
    print(classification_results.to_string(index=False))

    regression_results, regression_models = train_regression_models(
        train_df,
        test_df,
    )

    save_models(
        classification_models,
        regression_models,
    )
    
    print("\nRegression results")
    print("-" * 80)
    print(regression_results.to_string(index=False))

    classification_results_path = RESULTS_DIR / "classification_results.csv"
    regression_results_path = RESULTS_DIR / "regression_results.csv"
    
    classification_results.to_csv(classification_results_path, index=False)
    regression_results.to_csv(regression_results_path, index=False)
    
    logger.info(
        "Classification results saved to %s.",
        classification_results_path,
    )
    logger.info(
        "Regression results saved to %s.",
        regression_results_path,
    )
    
    logger.info("Task 1 supervised-learning pipeline completed successfully.")


if __name__ == "__main__":
    main()


