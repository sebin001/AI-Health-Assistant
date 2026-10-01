# ============================================================
# BLOOD PRESSURE ASSESSMENT SERVICE
# ============================================================

def assess_blood_pressure(systolic, diastolic):
    """
    Assess an adult blood-pressure reading.

    This is a category assessment, not a medical diagnosis.
    Categories follow American Heart Association adult
    blood-pressure categories.
    """

    # --------------------------------------------------------
    # Convert input
    # --------------------------------------------------------

    try:
        systolic = float(systolic)
        diastolic = float(diastolic)

    except (TypeError, ValueError):

        raise ValueError(
            "Blood pressure values must be numbers."
        )

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if systolic <= 0 or diastolic <= 0:

        raise ValueError(
            "Blood pressure values must be greater than zero."
        )

    if systolic <= diastolic:

        raise ValueError(
            "Systolic pressure should be greater "
            "than diastolic pressure."
        )

    # --------------------------------------------------------
    # AHA adult categories
    # --------------------------------------------------------

    if systolic > 180 or diastolic > 120:

        category = "Severe Hypertension"

        level = "severe"

        message = (
            "This blood-pressure reading is very high. "
            "Repeat the measurement and seek prompt "
            "medical attention, especially if symptoms "
            "such as chest pain, shortness of breath, "
            "weakness, vision changes, or difficulty "
            "speaking are present."
        )

    elif systolic >= 140 or diastolic >= 90:

        category = "Stage 2 Hypertension"

        level = "high"

        message = (
            "This reading falls in the Stage 2 "
            "high blood-pressure category."
        )

    elif systolic >= 130 or diastolic >= 80:

        category = "Stage 1 Hypertension"

        level = "high"

        message = (
            "This reading falls in the Stage 1 "
            "high blood-pressure category."
        )

    elif systolic >= 120 and diastolic < 80:

        category = "Elevated Blood Pressure"

        level = "elevated"

        message = (
            "This reading falls in the elevated "
            "blood-pressure category."
        )

    else:

        category = "Normal Blood Pressure"

        level = "normal"

        message = (
            "This reading falls in the normal "
            "blood-pressure category."
        )

    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {
        "systolic": systolic,
        "diastolic": diastolic,
        "category": category,
        "level": level,
        "message": message,
    }