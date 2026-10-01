from assist.ml_services import predict_diabetes_risk


DIABETES_REQUIRED_FIELDS = [
    "pregnancies",
    "glucose",
    "blood_pressure",
    "skin_thickness",
    "insulin",
    "bmi",
    "diabetes_pedigree",
    "age",
]


def check_diabetes_inputs(data):
    """
    Check whether all required diabetes prediction
    features are available from the medical document.
    """

    missing_fields = []

    for field in DIABETES_REQUIRED_FIELDS:
        value = data.get(field)

        if value is None or value == "":
            missing_fields.append(field)

    return {
        "ready": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


def predict_diabetes_from_document(data):
    """
    Run the diabetes ML model only when all required
    input features are available.
    """

    input_check = check_diabetes_inputs(data)

    if not input_check["ready"]:
        return {
            "success": False,
            "message": (
                "Diabetes risk assessment cannot be completed "
                "because some required health values are missing."
            ),
            "missing_fields": input_check["missing_fields"],
        }

    result = predict_diabetes_risk(
        pregnancies=data["pregnancies"],
        glucose=data["glucose"],
        blood_pressure=data["blood_pressure"],
        skin_thickness=data["skin_thickness"],
        insulin=data["insulin"],
        bmi=data["bmi"],
        diabetes_pedigree=data["diabetes_pedigree"],
        age=data["age"],
    )

    return {
        "success": True,
        "result": result,
        "missing_fields": [],
    }
