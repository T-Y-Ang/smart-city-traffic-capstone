from pathlib import Path
import logging

import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from mlxtend.frequent_patterns import apriori, association_rules

from common import prepare_part3_data


logger = logging.getLogger(__name__)


# Project paths
PART3_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PART3_DIR / "results"
FIGURES_DIR = PART3_DIR / "figures"
LOGS_DIR = PART3_DIR / "logs"

KMEANS_FEATURES = [
    "traffic_volume",
    "temp",
    "rain_1h",
    "clouds_all",
]

def ensure_output_directories():
    """Create output directories required by the unsupervised-learning task."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging():
    """Configure console and file logging for Task 2."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_file = LOGS_DIR / "task2_unsupervised.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a"),
        ],
    )

    logger.info("Logging configured. Log file: %s", log_file)


def evaluate_kmeans_clusters(df):
    """Evaluate candidate K-means cluster counts using silhouette score."""
    X = df[KMEANS_FEATURES].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    results = []

    for k in range(2, 7):
        logger.info("Evaluating K-means with k=%d.", k)

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )

        labels = model.fit_predict(X_scaled)

        score = silhouette_score(
            X_scaled,
            labels,
            sample_size=10000,
            random_state=42,
        )

        results.append(
            {
                "k": k,
                "silhouette_score": score,
            }
        )

        logger.info(
            "K-means k=%d - silhouette score: %.4f.",
            k,
            score,
        )

    return pd.DataFrame(results)


def fit_final_kmeans(df, n_clusters=6):
    """Fit the final K-means model and create interpretable cluster profiles."""
    X = df[KMEANS_FEATURES].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
    )

    clustered_df = df.copy()
    clustered_df["cluster"] = model.fit_predict(X_scaled)

    cluster_profiles = (
        clustered_df
        .groupby("cluster")
        .agg(
            observations=("cluster", "size"),
            mean_traffic_volume=("traffic_volume", "mean"),
            mean_temp=("temp", "mean"),
            mean_rain_1h=("rain_1h", "mean"),
            mean_clouds_all=("clouds_all", "mean"),
        )
        .reset_index()
    )

    cluster_profiles["percentage"] = (
        cluster_profiles["observations"] / len(clustered_df) * 100
    )

    logger.info(
        "Final K-means model fitted with %d clusters.",
        n_clusters,
    )

    return clustered_df, cluster_profiles, model, scaler


def create_association_transactions(df):
    """Create categorical transaction data for association-rule mining."""
    transactions = pd.DataFrame(index=df.index)

    # Discretize hour into broad time periods.
    transactions["Time"] = pd.cut(
        df["hour"],
        bins=[-1, 5, 11, 17, 23],
        labels=["Night", "Morning", "Afternoon", "Evening"],
    )

    # Separate weekday and weekend observations.
    transactions["DayType"] = df["is_weekend"].map(
        {
            False: "Weekday",
            True: "Weekend",
        }
    )

    # Use the Part 2 quartile-based congestion category.
    transactions["Congestion"] = df["congestion_category"]

    # Use broad weather groups created for Part 3.
    transactions["Weather"] = "Normal"
    transactions.loc[
        df["is_low_visibility"] == 1,
        "Weather",
    ] = "LowVisibility"
    transactions.loc[
        df["is_severe_weather"] == 1,
        "Weather",
    ] = "Severe"

    logger.info(
        "Created association-rule transaction data with %d rows.",
        len(transactions),
    )

    return transactions


def mine_association_rules(transactions):
    """Mine association rules from discretized traffic conditions."""
    encoded = pd.get_dummies(
        transactions,
        prefix=transactions.columns,
        prefix_sep="=",
        dtype=bool,
    )

    logger.info(
        "One-hot encoded transactions into %d binary items.",
        len(encoded.columns),
    )

    frequent_itemsets = apriori(
        encoded,
        min_support=0.05,
        use_colnames=True,
    )

    logger.info(
        "Apriori identified %d frequent itemsets.",
        len(frequent_itemsets),
    )

    rules = association_rules(
        frequent_itemsets,
        metric="lift",
        min_threshold=1.0,
    )

    rules = rules.sort_values(
        ["lift", "confidence", "support"],
        ascending=False,
    ).reset_index(drop=True)

    logger.info(
        "Generated %d association rules with lift >= 1.0.",
        len(rules),
    )

    return frequent_itemsets, rules


def save_association_results(frequent_itemsets, rules):
    """Save frequent itemsets and association rules as readable CSV files."""
    itemsets_output = frequent_itemsets.copy()
    rules_output = rules.copy()

    itemsets_output["itemsets"] = itemsets_output["itemsets"].apply(
        lambda items: ", ".join(sorted(items))
    )

    for column in ["antecedents", "consequents"]:
        rules_output[column] = rules_output[column].apply(
            lambda items: ", ".join(sorted(items))
        )

    itemsets_path = RESULTS_DIR / "frequent_itemsets.csv"
    rules_path = RESULTS_DIR / "association_rules.csv"

    itemsets_output.to_csv(itemsets_path, index=False)
    rules_output.to_csv(rules_path, index=False)

    logger.info("Frequent itemsets saved to %s.", itemsets_path)
    logger.info("Association rules saved to %s.", rules_path)


def main():
    """Run the unsupervised-learning workflow."""
    configure_logging()
    ensure_output_directories()

    logger.info("Task 2 unsupervised-learning pipeline started.")

    df = prepare_part3_data()

    logger.info(
        "Prepared Part 3 dataset with %d rows and %d columns.",
        len(df),
        len(df.columns),
    )

    kmeans_evaluation = evaluate_kmeans_clusters(df)


    print("\nK-means cluster evaluation")
    print("-" * 50)
    print(kmeans_evaluation.to_string(index=False))

    clustered_df, cluster_profiles, kmeans_model, kmeans_scaler = (
    fit_final_kmeans(df, n_clusters=6)
    )
    
    print("\nK-means cluster profiles")
    print("-" * 100)
    print(cluster_profiles.to_string(index=False))

    kmeans_evaluation_path = RESULTS_DIR / "kmeans_evaluation.csv"
    cluster_profiles_path = RESULTS_DIR / "kmeans_cluster_profiles.csv"
    
    kmeans_evaluation.to_csv(kmeans_evaluation_path, index=False)
    cluster_profiles.to_csv(cluster_profiles_path, index=False)
    
    logger.info(
        "K-means evaluation saved to %s.",
        kmeans_evaluation_path,
    )
    logger.info(
        "K-means cluster profiles saved to %s.",
        cluster_profiles_path,
    )

    transactions = create_association_transactions(df)
    
    logger.info(
        "Transaction categories:\n%s",
        transactions.nunique().to_string(),
    )
    
    print("\nAssociation-rule transaction preview")
    print("-" * 70)
    print(transactions.head(10).to_string(index=False))

    frequent_itemsets, association_rule_results = mine_association_rules(
        transactions
    )

    save_association_results(
        frequent_itemsets,
        association_rule_results,
    )
    
    print("\nTop association rules by lift")
    print("-" * 120)
    
    display_columns = [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
    ]
    
    print(
        association_rule_results[display_columns]
        .head(10)
        .to_string(index=False)
    )

    logger.info("Task 2 unsupervised-learning pipeline completed successfully.")


if __name__ == "__main__":
    main()