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
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "ML" / "datasets" / "diabetes.csv"
MODEL_DIR = BASE_DIR / "ML" / "trained_models"
RESULTS_DIR = BASE_DIR / "ML" / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("=" * 70)
print("DIABETES RISK PREDICTION - MODEL TRAINING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully.")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")


# ============================================================
# 3. VALIDATE DATASET
# ============================================================

required_columns = [
    "Pregnancies",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
    "Outcome",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset is missing required columns: {missing_columns}"
    )

print("\nDataset columns verified.")


# ============================================================
# 4. REPLACE INVALID ZERO MEASUREMENTS
# ============================================================

zero_as_missing_columns = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
]

print("\nHandling physiologically invalid zero measurements...")

for column in zero_as_missing_columns:

    zero_count = (df[column] == 0).sum()

    print(
        f"{column}: "
        f"{zero_count} zero values -> treated as missing"
    )

    # Use numpy.nan instead of pandas.NA.
    # scikit-learn handles numpy.nan correctly.
    df[column] = df[column].replace(
        0,
        np.nan
    )


# ============================================================
# 5. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(
    columns=["Outcome"]
)

y = df["Outcome"]


print("\nFeatures:")
for feature in X.columns:
    print(f" - {feature}")


print("\nTarget distribution:")
print(y.value_counts())


# ============================================================
# 6. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nData split:")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")


# ============================================================
# 7. PREPROCESSING
# ============================================================

numeric_features = list(X.columns)

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
# 8. DEFINE ML MODELS
# ============================================================

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=2000,
        random_state=42,
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    ),
}


# ============================================================
# 9. TRAIN MODELS
# ============================================================

results = []

trained_pipelines = {}

print("\n" + "=" * 70)
print("MODEL TRAINING")
print("=" * 70)


for model_name, model in models.items():

    print(f"\nTraining: {model_name}")

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

    y_probability = pipeline.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        y_pred,
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        y_probability,
    )

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Class 0",
                "Class 1",
            ],
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
            "ROC_AUC": roc_auc,
        }
    )

    trained_pipelines[
        model_name
    ] = pipeline


# ============================================================
# 10. MODEL COMPARISON
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by="ROC_AUC",
    ascending=False,
)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 11. SELECT BEST MODEL
# ============================================================

best_model_name = results_df.iloc[0]["Model"]

best_pipeline = trained_pipelines[
    best_model_name
]

print("\n" + "=" * 70)
print(
    f"SELECTED MODEL: {best_model_name}"
)
print("=" * 70)


# ============================================================
# 12. FINAL PREDICTIONS
# ============================================================

y_pred_best = best_pipeline.predict(
    X_test
)


# ============================================================
# 13. CONFUSION MATRIX
# ============================================================

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
    xticklabels=[
        "Class 0",
        "Class 1",
    ],
    yticklabels=[
        "Class 0",
        "Class 1",
    ],
)

plt.title(
    f"Diabetes Model - Confusion Matrix\n"
    f"{best_model_name}"
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
    / "diabetes_confusion_matrix.png"
)

plt.savefig(
    confusion_matrix_path,
    dpi=150,
)

plt.close()


# ============================================================
# 14. SAVE MODEL RESULTS
# ============================================================

results_path = (
    RESULTS_DIR
    / "diabetes_model_results.csv"
)

results_df.to_csv(
    results_path,
    index=False,
)


# ============================================================
# 15. SAVE TRAINED PIPELINE
# ============================================================

model_path = (
    MODEL_DIR
    / "diabetes_risk_model.joblib"
)

joblib.dump(
    best_pipeline,
    model_path,
)


# ============================================================
# 16. TRAINING SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)

print(
    f"\nBest model: "
    f"{best_model_name}"
)

print(
    f"\nSaved trained model:"
)

print(
    model_path
)

print(
    f"\nSaved model comparison:"
)

print(
    results_path
)

print(
    f"\nSaved confusion matrix:"
)

print(
    confusion_matrix_path
)

print(
    "\nThe saved .joblib file contains:"
)

print(
    "1. Missing-value preprocessing"
)

print(
    "2. Feature scaling"
)

print(
    "3. Trained ML model"
)

print(
    "\nReady for independent prediction testing."
)

print(
    "=" * 70
)