from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ML"
    / "trained_models"
    / "health_risk_model.joblib"
)

_model_package = None


def load_health_risk_model():
    global _model_package

    if _model_package is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Health risk model not found: {MODEL_PATH}"
            )

        _model_package = joblib.load(MODEL_PATH)

    return _model_package


def predict_health_risk(
    age,
    sbp,
    dbp,
    bs,
    body_temp,
    heart_rate,
    min_exercise,
):
    model_package = load_health_risk_model()

    model = model_package["model"]
    label_encoder = model_package["label_encoder"]
    features = model_package["features"]

    patient_data = {
        "age": age,
        "SBP": sbp,
        "DBP": dbp,
        "BS": bs,
        "BodyTemp": body_temp,
        "HeartRate": heart_rate,
        "MinExercise": min_exercise,
    }

    missing_features = [
        feature
        for feature in features
        if feature not in patient_data
        or patient_data[feature] is None
        or patient_data[feature] == ""
    ]

    if missing_features:
        raise ValueError(
            "Missing required features: "
            f"{missing_features}"
        )

    patient_df = pd.DataFrame(
        [patient_data],
        columns=features,
    )

    prediction_encoded = model.predict(
        patient_df
    )[0]

    prediction_probability = model.predict_proba(
        patient_df
    )[0]

    prediction_label = (
        label_encoder
        .inverse_transform(
            [prediction_encoded]
        )[0]
    )

    probabilities = {}

    for class_name, probability in zip(
        label_encoder.classes_,
        prediction_probability,
    ):
        probabilities[class_name] = round(
            float(probability) * 100,
            2,
        )

    return {
        "risk_level": prediction_label,
        "probabilities": probabilities,
    }