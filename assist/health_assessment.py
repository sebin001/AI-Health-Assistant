from .bp_assessment import assess_blood_pressure
from .diabetes_document_ai import predict_diabetes_from_document
from .health_risk_document_ai import predict_health_risk_from_document


def generate_health_assessment(data):
    """
    Generate a combined health assessment from
    information extracted from a medical document.

    This summarizes documented information and ML-based
    risk assessments. It is not a medical diagnosis.
    """

    assessment = {
        "blood_pressure": None,
        "diabetes": None,
        "general_health_risk": None,
        "documented_diagnoses": data.get("diagnoses", []),
        "documented_medicines": data.get("medicines", []),
        "patient_information": {
            "age": data.get("age"),
            "blood_glucose": data.get("blood_glucose"),
            "heart_rate": data.get("heart_rate"),
        },
    }

    # ---------------------------------------------------------
    # 1. BLOOD PRESSURE ASSESSMENT
    # ---------------------------------------------------------

    systolic = data.get("systolic")
    diastolic = data.get("diastolic")

    if systolic is not None and diastolic is not None:
        try:
            assessment["blood_pressure"] = assess_blood_pressure(
                systolic=systolic,
                diastolic=diastolic,
            )
        except ValueError as error:
            assessment["blood_pressure"] = {
                "success": False,
                "message": str(error),
            }
    else:
        assessment["blood_pressure"] = {
            "success": False,
            "message": "Blood pressure values were not found in the document.",
        }

    # ---------------------------------------------------------
    # 2. DIABETES RISK ASSESSMENT
    # ---------------------------------------------------------

    diabetes_data = {
        "pregnancies": data.get("pregnancies"),
        "glucose": data.get("blood_glucose"),
        "blood_pressure": systolic,
        "skin_thickness": data.get("skin_thickness"),
        "insulin": data.get("insulin"),
        "bmi": data.get("bmi"),
        "diabetes_pedigree": data.get("diabetes_pedigree"),
        "age": data.get("age"),
    }

    assessment["diabetes"] = predict_diabetes_from_document(
        diabetes_data
    )

    # ---------------------------------------------------------
    # 3. GENERAL HEALTH RISK ASSESSMENT
    # ---------------------------------------------------------

    health_risk_data = {
        "age": data.get("age"),
        "sbp": systolic,
        "dbp": diastolic,
        "bs": data.get("blood_glucose"),
        "body_temp": data.get("body_temp"),
        "heart_rate": data.get("heart_rate"),
        "min_exercise": data.get("min_exercise"),
    }

    assessment["general_health_risk"] = (
        predict_health_risk_from_document(
            health_risk_data
        )
    )

    return assessment