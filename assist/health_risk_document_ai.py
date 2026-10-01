from .health_risk_service import predict_health_risk


HEALTH_RISK_REQUIRED_FIELDS = [
    "age",
    "sbp",
    "dbp",
    "bs",
    "body_temp",
    "heart_rate",
    "min_exercise",
]


def check_health_risk_inputs(data):
    """
    Check whether all required General Health Risk
    model features are available.
    """

    missing_fields = []

    for field in HEALTH_RISK_REQUIRED_FIELDS:
        value = data.get(field)

        if value is None or value == "":
            missing_fields.append(field)

    return {
        "ready": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


def predict_health_risk_from_document(data):
    """
    Run the General Health Risk ML model only when
    all required input features are available.
    """

    input_check = check_health_risk_inputs(data)

    if not input_check["ready"]:
        return {
            "success": False,
            "message": (
                "General health risk assessment cannot be completed "
                "because some required health values are missing."
            ),
            "missing_fields": input_check["missing_fields"],
        }

    result = predict_health_risk(
        age=data["age"],
        sbp=data["sbp"],
        dbp=data["dbp"],
        bs=data["bs"],
        body_temp=data["body_temp"],
        heart_rate=data["heart_rate"],
        min_exercise=data["min_exercise"],
    )

    return {
        "success": True,
        "result": result,
        "missing_fields": [],
    }