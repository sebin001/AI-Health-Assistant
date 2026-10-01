from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# 1. PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ML"
    / "trained_models"
    / "health_risk_model.joblib"
)


# ============================================================
# 2. LOAD TRAINED MODEL PACKAGE
# ============================================================

print("=" * 70)
print("GENERAL HEALTH RISK - INDEPENDENT TEST")
print("=" * 70)

print("\nLoading trained model...")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found:\n{MODEL_PATH}"
    )

model_package = joblib.load(
    MODEL_PATH
)

model = model_package["model"]
label_encoder = model_package["label_encoder"]
features = model_package["features"]

print(
    "Trained model loaded successfully."
)


# ============================================================
# 3. NEW HEALTH DATA
# ============================================================

patient_data = {
    "age": 35,
    "SBP": 140,
    "DBP": 90,
    "BS": 7.5,
    "BodyTemp": 98.0,
    "HeartRate": 78,
    "MinExercise": 30,
}


# ============================================================
# 4. VALIDATE FEATURES
# ============================================================

missing_features = [
    feature
    for feature in features
    if feature not in patient_data
]

if missing_features:

    raise ValueError(
        "Missing required features: "
        f"{missing_features}"
    )


# ============================================================
# 5. CREATE DATAFRAME
# ============================================================

patient_df = pd.DataFrame(
    [patient_data],
    columns=features,
)


print("\nPatient health data:")

print(
    patient_df.to_string(
        index=False
    )
)


# ============================================================
# 6. MAKE PREDICTION
# ============================================================

prediction_encoded = model.predict(
    patient_df
)[0]

prediction_probability = model.predict_proba(
    patient_df
)[0]


# ============================================================
# 7. CONVERT PREDICTION TO LABEL
# ============================================================

prediction_label = (
    label_encoder
    .inverse_transform(
        [prediction_encoded]
    )[0]
)


# ============================================================
# 8. DISPLAY RESULT
# ============================================================

print(
    "\n"
    + "=" * 70
)

print(
    "PREDICTION RESULT"
)

print(
    "=" * 70
)

print(
    f"\nHealth risk assessment: "
    f"{prediction_label}"
)


# ============================================================
# 9. DISPLAY CLASS PROBABILITIES
# ============================================================

print(
    "\nModel probability by class:"
)

for class_name, probability in zip(
    label_encoder.classes_,
    prediction_probability,
):

    print(
        f" - {class_name}: "
        f"{probability * 100:.2f}%"
    )


print(
    "\nNote:"
)

print(
    "This is an ML-based health-risk "
    "assessment, not a medical diagnosis."
)

print(
    "\nPrediction test completed successfully."
)

print(
    "=" * 70
)