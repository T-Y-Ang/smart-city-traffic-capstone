# Part 3 — Machine Learning and MLOps

## Overview

This part of the Smart City Traffic Capstone extends the engineered traffic dataset from Part 2 into supervised learning, unsupervised learning, neural
networks, explainability, experiment tracking, travel recommendations, deployment, monitoring, and responsible AI analysis.

The project uses historical traffic and weather observations from a single traffic corridor. All train/test evaluations use a chronological split where
appropriate to better reflect prediction on later observations.

## Important Proxy-Label Disclaimer

A real accident-outcome dataset was not available for this project.

The classification task therefore uses an engineered `high_risk` proxy. An observation is labelled high risk when High or Severe congestion occurs
together with adverse weather conditions.

This proxy is used only to demonstrate a machine-learning classification workflow. It must not be interpreted as an actual accident probability,
validated accident-risk model, or safety-critical prediction system.

## Project Structure

```text
part3_machine_learning/
├── 1_notebooks/
├── 2_models/
│   ├── linear_regression.joblib
│   ├── logistic_regression_classifier.joblib
│   ├── random_forest_classifier.joblib
│   ├── random_forest_regressor.joblib
│   └── traffic_volume_neural_network.keras
├── 3_mlflow/
│   ├── mlflow.db
│   └── register_model.py
├── 4_deployment/
│   └── app.py
├── 5_recommendation_system/
├── 6_monitoring/
│   └── monitor_model.py
├── logs/
├── reports/
│   └── responsible_ai_report.md
├── results/
├── common.py
├── task1_supervised.py
├── task2_unsupervised.py
├── task3_neural_network.py
├── task4_mlflow.py
├── task5_recommendation.py
└── task7_responsible_ai.py
```

The Part 3 scripts use the engineered dataset generated in Part 2:

```text
part2_python/data/engineered_traffic_data.csv
```

## Common Model Features

The supervised models use a common feature set containing:

- cyclical hour features
- cyclical day-of-week features
- weekend and peak-hour indicators
- month and year
- holiday indicator
- temperature, rainfall, snowfall, and cloud coverage
- one-hot encoded weather conditions

Traffic volume and congestion category are excluded from the classification input features to avoid direct leakage from the engineered proxy definition.

## Task 1 — Supervised Learning

Two classification algorithms and two regression algorithms were evaluated.

### Classification

Target: engineered `high_risk` proxy.

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.9506 | 0.7658 | 0.9875 | 0.8626 | 0.9923 |
| Random Forest | 0.9832 | 0.9234 | 0.9741 | 0.9481 | 0.9976 |

These metrics measure prediction of the engineered proxy label, not prediction
of real accidents.

### Regression

Target: `traffic_volume`.

| Model | MAE | R² |
|---|---:|---:|
| Linear Regression | 720.19 | 0.7634 |
| Random Forest | 249.16 | 0.9567 |

The Random Forest achieved the strongest regression performance of the tested models.

Run:

```bash
python part3_machine_learning/task1_supervised.py
```

## Task 2 — Unsupervised Learning and Association Rules

K-means clustering was evaluated for `k = 2` through `k = 6`. Among the tested values, `k = 6` produced the highest silhouette score of approximately 0.3433.

The resulting clusters represented combinations of traffic volume, temperature, rainfall, and cloud coverage.

Association-rule mining was also applied after discretising time of day, day type, congestion, and weather conditions.

One of the strongest interpretable rules was:

```text
Weekend + Night -> Low congestion
```

with approximately:

```text
Confidence = 89.63%
Lift       = 3.59
```

This indicates an association in the historical dataset and should not be interpreted as a causal relationship.

Run:

```bash
python part3_machine_learning/task2_unsupervised.py
```

## Task 3 — Neural Network and Explainability

A feed-forward neural network was trained to predict traffic volume using the same general feature set as the conventional regression models.

Test performance:

```text
MAE = 512.83
R²  = 0.8653
```

The neural network improved on the Linear Regression baseline but did not outperform the Random Forest regressor on this structured tabular dataset.

SHAP explainability was applied to the comparable Random Forest regressor. A tree model was used for SHAP because it predicts the same target from the same
feature set while allowing efficient TreeSHAP analysis.

The five features with the highest mean absolute SHAP values were:

1. `hour_cos`
2. `hour_sin`
3. `day_of_week_sin`
4. `is_weekend`
5. `day_of_week_cos`

Mean absolute SHAP values measure the magnitude of feature influence and do not by themselves indicate the direction of an effect.

Run:

```bash
python part3_machine_learning/task3_neural_network.py
```

## Task 4 — MLflow Experiment Tracking

MLflow was selected as the advanced AI/MLOps component.

Five model results were recorded as experiment runs:

- Logistic Regression classifier
- Random Forest classifier
- Linear Regression
- Random Forest regressor
- Feed-forward Neural Network

The local MLflow backend is stored in:

```text
part3_machine_learning/3_mlflow/mlflow.db
```

To open the MLflow interface from the project root:

```bash
mlflow ui \
  --backend-store-uri "sqlite:////mnt/c/Users/USER/OneDrive/Documents/GitHub/NUS-AI-ML-smart-city-traffic-capstone-project/part3_machine_learning/3_mlflow/mlflow.db" \
  --port 5001
```

Then open:

```text
http://127.0.0.1:5001
```

### Model Registry and Versioning

Model versioning was demonstrated using the MLflow Model Registry under the
registered model name:

```text
traffic_volume_prediction_model
```

Two previously trained and evaluated regression models were registered as successive versions of the same traffic-volume prediction model:

| Version | Model | Role | MAE | R² |
|---|---|---|---:|---:|
| Version 1 | Linear Regression | Baseline | 720.19 | 0.7634 |
| Version 2 | Random Forest Regression | Improved candidate | 249.16 | 0.9567 |

Version 1 provides a simple and interpretable baseline. Version 2 represents a higher-performing model iteration, reducing MAE from 720.19 to 249.16
vehicles and increasing R² from 0.7634 to 0.9567 on the same chronological test set.

The earlier `traffic_volume_linear_regression` Version 1 registration is retained in the MLflow database as part of the project history.

The registration script uses the existing fitted model artifacts and does not retrain the models. Running the script again will create additional
registry versions, so it should only be rerun when intentionally creating new versions.
```

## Task 5 — Travel-Timing Recommendation

Because the dataset represents a single traffic corridor rather than a road network, the recommendation component suggests lower-traffic travel times
rather than alternative physical routes.

Historical patterns showed that the lowest-volume periods generally occurred overnight. In the generated recommendations, weekday low-traffic windows were
commonly around 01:00–03:00, while weekend recommendations were commonly around 02:00–04:00.

Recommendations are stratified by weekday/weekend and weather condition.

These are historical travel-timing recommendations and do not guarantee future traffic conditions.

Run:

```bash
python part3_machine_learning/task5_recommendation.py
```

## Task 6 — Deployment and Monitoring

### FastAPI Deployment Mock-up

A saved Logistic Regression classifier is served through FastAPI.

Start the API from the repository root:

```bash
uvicorn part3_machine_learning.4_deployment.app:app \
  --host 127.0.0.1 \
  --port 8000
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

The `/predict` endpoint returns an engineered high-risk proxy prediction and probability together with a warning that the output is not an actual accident
risk prediction.

### Model Monitoring

The monitoring demonstration uses the Linear Regression traffic-volume model. The chronological test period is divided into an earlier reference window and
a later monitoring window.

Observed MAE:

```text
Reference window MAE  = 723.72
Monitoring window MAE = 716.66
Change                = -0.98%
Status                = PASS - Normal
```

The demonstration alert threshold is a 20% increase in prediction error.

A PASS result means that prediction error did not materially worsen under this specific monitoring rule. It does not prove the absence of all forms of data or
feature drift.

Run:

```bash
python part3_machine_learning/6_monitoring/monitor_model.py
```

## Task 7 — Responsible and Sustainable AI

Responsible AI evaluation focuses on operational subgroups because the dataset does not contain demographic or protected-attribute information.

Selected Linear Regression subgroup MAEs were:

| Subgroup | MAE |
|---|---:|
| Weekday | 723.44 |
| Weekend | 712.16 |
| Normal weather | 689.69 |
| Adverse weather | 781.80 |
| Morning | 1059.78 |
| Afternoon | 491.47 |

Prediction error during adverse weather was approximately 13.4% higher than during normal weather. Performance also varied substantially by time of day.

The Responsible AI report discusses:

- sampling and geographic coverage limitations
- proxy-label limitations
- uneven operational performance
- human oversight and governance
- model monitoring
- computational and sustainability trade-offs

Run:

```bash
python part3_machine_learning/task7_responsible_ai.py
```

The generated report is stored at:

```text
part3_machine_learning/reports/responsible_ai_report.md
```

## Logging

Part 3 scripts use Python logging and save execution logs under:

```text
part3_machine_learning/logs/
```

The logs provide a record of model training, analysis, deployment, recommendation, monitoring, MLflow registration, and Responsible AI evaluation.

## Key Limitations

This project is a demonstration based on historical observations from a single traffic corridor. Results may not generalise to other roads, cities, time
periods, or future traffic regimes.

The classification target is an engineered proxy rather than an observed accident outcome. Any real safety-related application would require validated
accident data, domain review, external validation, appropriate governance, and continued monitoring.

Model performance should therefore be interpreted as evidence about this capstone workflow and dataset rather than evidence of production readiness.