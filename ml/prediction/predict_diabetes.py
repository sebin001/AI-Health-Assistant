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
    / "diabetes_risk_model.joblib"
)


# ============================================================
# 2. LOAD TRAINED MODEL
# ============================================================

print("=" * 70)
print("DIABETES RISK PREDICTION - INDEPENDENT TEST")
print("=" * 70)

print("\nLoading trained model...")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Trained model not found:\n{MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

print("Trained model loaded successfully.")


# ============================================================
# 3. NEW PATIENT INPUT
# ============================================================

patient_data = {
    "Pregnancies": 2,
    "Glucose": 140,
    "BloodPressure": 80,
    "SkinThickness": 25,
    "Insulin": 100,
    "BMI": 30.5,
    "DiabetesPedigreeFunction": 0.50,
    "Age": 35,
}


# ============================================================
# 4. CONVERT INPUT TO DATAFRAME
# ============================================================

patient_df = pd.DataFrame(
    [patient_data]
)


print("\nPatient input:")
print(patient_df.to_string(index=False))


# ============================================================
# 5. PREDICTION
# ============================================================

prediction = model.predict(
    patient_df
)[0]

probability = model.predict_proba(
    patient_df
)[0][1]


# ============================================================
# 6. DISPLAY RESULT
# ============================================================

print("\n" + "=" * 70)
print("PREDICTION RESULT")
print("=" * 70)

if prediction == 1:
    result = "Higher diabetes risk"
else:
    result = "Lower diabetes risk"


print(f"\nRisk assessment: {result}")

print(
    f"Estimated model probability: "
    f"{probability * 100:.2f}%"
)

print("\nNote:")
print(
    "This is an ML-based risk assessment, "
    "not a medical diagnosis."
)

print("\nPrediction test completed successfully.")

print("=" * 70)