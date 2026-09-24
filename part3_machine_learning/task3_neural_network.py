from pathlib import Path
import logging

import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

import joblib
import shap

from common import (
    COMMON_FEATURES,
    REGRESSION_TARGET,
    prepare_part3_data,
)


logger = logging.getLogger(__name__)


# Project paths
PART3_DIR = Path(__file__).resolve().parent
MODELS_DIR = PART3_DIR / "2_models"
RESULTS_DIR = PART3_DIR / "results"
FIGURES_DIR = PART3_DIR / "figures"
LOGS_DIR = PART3_DIR / "logs"


def ensure_output_directories():
    """Create output directories required by Task 3."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging():
    """Configure console and file logging for Task 3."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_file = LOGS_DIR / "task3_neural_network.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a"),
        ],
    )

    logger.info("Logging configured. Log file: %s", log_file)


def prepare_neural_network_data(df, test_size=0.20):
    """Create chronological train/test data and scale neural-network inputs."""
    df = df.sort_values("date_time").reset_index(drop=True)

    split_index = int(len(df) * (1 - test_size))

    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    X_train = train_df[COMMON_FEATURES].astype("float32")
    X_test = test_df[COMMON_FEATURES].astype("float32")

    y_train = train_df[REGRESSION_TARGET].astype("float32")
    y_test = test_df[REGRESSION_TARGET].astype("float32")

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train).astype("float32")
    X_test_scaled = scaler.transform(X_test).astype("float32")

    logger.info(
        "Chronological neural-network split: %d training rows, %d test rows.",
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

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def build_neural_network(input_dim):
    """Build a feed-forward neural network for traffic-volume regression."""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(1),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",
        metrics=["mae"],
    )

    logger.info(
        "Built neural network with input dimension %d, hidden layers 64 and 32.",
        input_dim,
    )

    return model


def train_neural_network(model, X_train, y_train):
    """Train the neural network with early stopping."""
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
    )

    history = model.fit(
        X_train,
        y_train,
        validation_split=0.20,
        epochs=30,
        batch_size=64,
        callbacks=[early_stopping],
        verbose=0,
        shuffle=False,
    )

    logger.info(
        "Neural-network training completed after %d epochs.",
        len(history.history["loss"]),
    )

    logger.info(
        "Final training MAE: %.2f; validation MAE: %.2f.",
        history.history["mae"][-1],
        history.history["val_mae"][-1],
    )

    return history


def evaluate_neural_network(model, X_test, y_test):
    """Evaluate the neural network on the chronological test set."""
    predictions = model.predict(
        X_test,
        verbose=0,
    ).reshape(-1)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    logger.info(
        "Neural-network test results: MAE=%.2f, R2=%.4f.",
        mae,
        r2,
    )

    results = pd.DataFrame(
        [
            {
                "model": "Feed-forward Neural Network",
                "MAE": mae,
                "R2": r2,
            }
        ]
    )

    results_path = RESULTS_DIR / "neural_network_results.csv"
    results.to_csv(results_path, index=False)

    logger.info(
        "Saved neural-network results to %s.",
        results_path,
    )

    return predictions, results


def save_neural_network(model):
    """Save the trained neural network."""
    model_path = MODELS_DIR / "traffic_volume_neural_network.keras"

    model.save(model_path)

    logger.info(
        "Saved neural-network model to %s.",
        model_path,
    )


def run_shap_explainability(df):
    """Explain the comparable Random Forest traffic-volume model using SHAP."""
    rf_path = MODELS_DIR / "random_forest_regressor.joblib"

    logger.info(
        "Loading comparable Random Forest regressor for SHAP explainability."
    )

    rf_model = joblib.load(rf_path)

    # Reproduce the chronological test split used in Task 1.
    df = df.sort_values("date_time").reset_index(drop=True)
    split_index = int(len(df) * 0.80)
    test_df = df.iloc[split_index:].copy()

    # Random Forest in Task 1 was trained on unscaled features.
    X_explain = test_df[COMMON_FEATURES].iloc[:200]

    logger.info(
        "Running SHAP TreeExplainer on %d test observations.",
        len(X_explain),
    )

    explainer = shap.TreeExplainer(rf_model)
    shap_values = explainer.shap_values(X_explain)

    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    importance_df = pd.DataFrame(
        {
            "feature": COMMON_FEATURES,
            "mean_abs_shap": mean_abs_shap,
        }
    ).sort_values(
        "mean_abs_shap",
        ascending=False,
    )

    output_path = RESULTS_DIR / "shap_feature_importance.csv"
    importance_df.to_csv(output_path, index=False)

    logger.info(
        "Saved SHAP feature importance to %s.",
        output_path,
    )

    logger.info(
        "Top five SHAP features: %s",
        importance_df.head(5)["feature"].tolist(),
    )

    return importance_df


def main():
    """Run the neural-network and explainability workflow."""
    configure_logging()
    ensure_output_directories()

    np.random.seed(42)
    tf.random.set_seed(42)

    logger.info("Task 3 neural-network pipeline started.")

    df = prepare_part3_data()

    logger.info(
        "Prepared Part 3 dataset with %d rows and %d columns.",
        len(df),
        len(df.columns),
    )

    logger.info(
        "TensorFlow GPU devices detected: %s",
        tf.config.list_physical_devices("GPU"),
    )
    
    X_train, X_test, y_train, y_test, scaler = prepare_neural_network_data(df)
    
    logger.info(
        "Neural-network input shape: train=%s, test=%s.",
        X_train.shape,
        X_test.shape,
    )

    model = build_neural_network(X_train.shape[1])

    history = train_neural_network(
        model,
        X_train,
        y_train,
    )

    predictions, results = evaluate_neural_network(
        model,
        X_test,
        y_test,
    )

    save_neural_network(model)

    shap_importance = run_shap_explainability(df)


if __name__ == "__main__":
    main()