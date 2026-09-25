from pathlib import Path
import logging
import sys

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


PART3_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PART3_DIR))

from common import COMMON_FEATURES


logger = logging.getLogger(__name__)


MODEL_PATH = (
    PART3_DIR
    / "2_models"
    / "logistic_regression_classifier.joblib"
)

LOGS_DIR = PART3_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOGS_DIR / "deployment_api.log",
            mode="a",
        ),
    ],
)


logger.info("Loading classification model from %s.", MODEL_PATH)

model = joblib.load(MODEL_PATH)


app = FastAPI(
    title="Smart City Traffic Risk Proxy API",
    description=(
        "Demonstration API for the capstone high-risk traffic proxy. "
        "This is not an actual accident-risk prediction system."
    ),
    version="1.0",
)


class TrafficFeatures(BaseModel):
    hour_sin: float
    hour_cos: float
    day_of_week_sin: float
    day_of_week_cos: float
    is_weekend: int
    is_peak_hour: int
    month: int
    year: int
    is_holiday: int
    temp: float
    rain_1h: float
    snow_1h: float
    clouds_all: float
    weather_Clear: int
    weather_Clouds: int
    weather_Drizzle: int
    weather_Fog: int
    weather_Haze: int
    weather_Mist: int
    weather_Rain: int
    weather_Smoke: int
    weather_Snow: int
    weather_Squall: int
    weather_Thunderstorm: int


@app.get("/")
def root():
    """Return API status and proxy warning."""
    return {
        "status": "running",
        "model": "Logistic Regression",
        "target": "high_risk_proxy",
        "warning": (
            "Demonstration proxy only; "
            "not an actual accident-risk prediction."
        ),
    }


@app.post("/predict")
def predict(features: TrafficFeatures):
    """Predict the demonstration high-risk traffic proxy."""
    input_df = pd.DataFrame(
        [[getattr(features, feature) for feature in COMMON_FEATURES]],
        columns=COMMON_FEATURES,
    )

    probability = float(model.predict_proba(input_df)[0, 1])
    prediction = int(probability >= 0.5)

    logger.info(
        "Prediction generated: class=%d, probability=%.4f.",
        prediction,
        probability,
    )

    return {
        "high_risk_proxy_prediction": prediction,
        "high_risk_proxy_probability": round(probability, 4),
        "warning": (
            "Demonstration proxy only; "
            "not an actual accident-risk prediction."
        ),
    }