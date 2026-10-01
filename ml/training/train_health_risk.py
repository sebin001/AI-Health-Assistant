from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    BASE_DIR
    / "ML"
    / "datasets"
    / "blood_pressure"
    / "BP.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "ML"
    / "trained_models"
)

RESULTS_DIR = (
    BASE_DIR
    / "ML"
    / "results"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("=" * 70)
print("GENERAL HEALTH RISK - MODEL TRAINING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(
    DATASET_PATH
)

print("Dataset loaded successfully.")

print(
    f"Rows: {df.shape[0]}"
)

print(
    f"Columns: {df.shape[1]}"
)


# ============================================================
# 3. VALIDATE DATASET
# ============================================================

required_columns = [
    "age",
    "SBP",
    "DBP",
    "BS",
    "BodyTemp",
    "HeartRate",
    "RiskLevel",
    "MinExercise",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "Dataset is missing required columns: "
        f"{missing_columns}"
    )

print("\nDataset columns verified.")


# ============================================================
# 4. CHECK MISSING VALUES
# ============================================================

print("\nMissing values:")

print(
    df[required_columns]
    .isnull()
    .sum()
)


# ============================================================
# 5. DISPLAY TARGET DISTRIBUTION
# ============================================================

print("\nRiskLevel distribution:")

print(
    df["RiskLevel"]
    .value_counts()
)


# ============================================================
# 6. SEPARATE FEATURES AND TARGET
# ============================================================

feature_columns = [
    "age",
    "SBP",
    "DBP",
    "BS",
    "BodyTemp",
    "HeartRate",
    "MinExercise",
]

X = df[
    feature_columns
].copy()

y = df[
    "RiskLevel"
].copy()


# ============================================================
# 7. NORMALIZE TARGET LABELS
# ============================================================

y = (
    y
    .astype(str)
    .str.strip()
    .str.lower()
)

print("\nTarget classes:")

print(
    sorted(
        y.unique()
    )
)


# ============================================================
# 8. ENCODE TARGET
# ============================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(
    y
)

print("\nTarget encoding:")

for index, label in enumerate(
    label_encoder.classes_
):

    print(
        f"{index} = {label}"
    )


# ============================================================
# 9. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y_encoded,
        test_size=0.20,
        random_state=42,
        stratify=y_encoded,
    )
)


print("\nData split:")

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples:  {len(X_test)}"
)


# ============================================================
# 10. PREPROCESSING
# ============================================================

numeric_features = list(
    X.columns
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",

            Pipeline(
                steps=[
                    (
                        "imputer",
                        SimpleImputer(
                            strategy="median"
                        ),
                    ),

                    (
                        "scaler",
                        StandardScaler(),
                    ),
                ]
            ),

            numeric_features,
        )
    ]
)


# ============================================================
# 11. DEFINE MODELS
# ============================================================

models = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=2000,
            random_state=42,
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        ),
}


# ============================================================
# 12. TRAIN MODELS
# ============================================================

results = []

trained_pipelines = {}

print(
    "\n"
    + "=" * 70
)

print(
    "MODEL TRAINING"
)

print(
    "=" * 70
)


for model_name, model in models.items():

    print(
        f"\nTraining: {model_name}"
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),

            (
                "model",
                model,
            ),
        ]
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    y_pred = pipeline.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        y_pred,
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    print(
        f"Accuracy:  {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1 Score:  {f1:.4f}"
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=(
                label_encoder.classes_
            ),
            zero_division=0,
        )
    )

    results.append(
        {
            "Model": model_name,
            "Accuracy": accuracy,
            "Precision": precision,
            "Recall": recall,
            "F1_Score": f1,
        }
    )

    trained_pipelines[
        model_name
    ] = pipeline


# ============================================================
# 13. MODEL COMPARISON
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by="F1_Score",
    ascending=False,
)

print(
    "\n"
    + "=" * 70
)

print(
    "MODEL COMPARISON"
)

print(
    "=" * 70
)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 14. SELECT BEST MODEL
# ============================================================

best_model_name = (
    results_df
    .iloc[0]["Model"]
)

best_pipeline = (
    trained_pipelines[
        best_model_name
    ]
)


print(
    "\n"
    + "=" * 70
)

print(
    f"SELECTED MODEL: "
    f"{best_model_name}"
)

print(
    "=" * 70
)


# ============================================================
# 15. CONFUSION MATRIX
# ============================================================

y_pred_best = (
    best_pipeline.predict(
        X_test
    )
)

cm = confusion_matrix(
    y_test,
    y_pred_best,
)

plt.figure(
    figsize=(7, 5)
)

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=(
        label_encoder.classes_
    ),
    yticklabels=(
        label_encoder.classes_
    ),
)

plt.title(
    "General Health Risk - Confusion Matrix"
)

plt.xlabel(
    "Predicted"
)

plt.ylabel(
    "Actual"
)

plt.tight_layout()


confusion_matrix_path = (
    RESULTS_DIR
    / "health_risk_confusion_matrix.png"
)

plt.savefig(
    confusion_matrix_path,
    dpi=150,
)

plt.close()


# ============================================================
# 16. SAVE MODEL RESULTS
# ============================================================

results_path = (
    RESULTS_DIR
    / "health_risk_model_results.csv"
)

results_df.to_csv(
    results_path,
    index=False,
)


# ============================================================
# 17. SAVE COMPLETE MODEL PACKAGE
# ============================================================

model_package = {

    "model": best_pipeline,

    "label_encoder": label_encoder,

    "features": feature_columns,

    "classes": list(
        label_encoder.classes_
    ),
}


model_path = (
    MODEL_DIR
    / "health_risk_model.joblib"
)

joblib.dump(
    model_package,
    model_path,
)


# ============================================================
# 18. TRAINING SUMMARY
# ============================================================

print(
    "\n"
    + "=" * 70
)

print(
    "TRAINING COMPLETE"
)

print(
    "=" * 70
)

print(
    f"\nBest model: "
    f"{best_model_name}"
)

print(
    "\nSaved trained model:"
)

print(
    model_path
)

print(
    "\nSaved model comparison:"
)

print(
    results_path
)

print(
    "\nSaved confusion matrix:"
)

print(
    confusion_matrix_path
)

print(
    "\nSaved classes:"
)

for class_name in label_encoder.classes_:

    print(
        f" - {class_name}"
    )

print(
    "\nReady for independent prediction testing."
)

print(
    "=" * 70
)