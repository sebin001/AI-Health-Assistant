from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# DIABETES ML MODEL SERVICE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ML"
    / "trained_models"
    / "diabetes_risk_model.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

_model = None


def load_diabetes_model():
    """
    Load the trained diabetes risk model.

    The model is loaded only once and then reused.
    """

    global _model

    if _model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Diabetes model not found: {MODEL_PATH}"
            )

        _model = joblib.load(MODEL_PATH)

    return _model


# ============================================================
# DIABETES RISK PREDICTION
# ============================================================

def predict_diabetes_risk(
    pregnancies,
    glucose,
    blood_pressure,
    skin_thickness,
    insulin,
    bmi,
    diabetes_pedigree,
    age,
):
    """
    Predict diabetes risk using the trained Random Forest model.

    Returns:
        {
            "prediction": 0 or 1,
            "risk_level": str,
            "probability": float
        }
    """

    model = load_diabetes_model()

    # --------------------------------------------------------
    # Prepare input
    # --------------------------------------------------------

    patient_data = pd.DataFrame(
        [
            {
                "Pregnancies": pregnancies,
                "Glucose": glucose,
                "BloodPressure": blood_pressure,
                "SkinThickness": skin_thickness,
                "Insulin": insulin,
                "BMI": bmi,
                "DiabetesPedigreeFunction": diabetes_pedigree,
                "Age": age,
            }
        ]
    )

    # --------------------------------------------------------
    # Model prediction
    # --------------------------------------------------------

    prediction = int(
        model.predict(patient_data)[0]
    )

    probability = float(
        model.predict_proba(patient_data)[0][1]
    )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    if probability >= 0.70:

        risk_level = "Higher Risk"

    elif probability >= 0.40:

        risk_level = "Moderate Risk"

    else:

        risk_level = "Lower Risk"

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "prediction": prediction,
        "risk_level": risk_level,
        "probability": round(
            probability * 100,
            2
        ),
    }