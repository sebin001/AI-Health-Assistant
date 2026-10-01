import re


def extract_medical_information(text):
    if not text or not text.strip():
        raise ValueError("Medical document text is empty.")

    result = {
        "age": None,
        "blood_pressure": None,
        "systolic": None,
        "diastolic": None,
        "blood_glucose": None,
        "heart_rate": None,
        "diagnoses": [],
        "medicines": [],
    }

    original_text = text.strip()

    # Normalize spaces while preserving line structure.
    clean_text = re.sub(
        r"[ \t]+",
        " ",
        original_text
    )

    # ---------------------------------------------------------
    # AGE
    # ---------------------------------------------------------

    age_match = re.search(
        r"\bage\s*(?:[:|\-])?\s*(\d{1,3})"
        r"\s*(?:years?|yrs?)?\b",
        clean_text,
        re.IGNORECASE
    )

    if age_match:
        result["age"] = int(age_match.group(1))

    # ---------------------------------------------------------
    # BLOOD PRESSURE
    # Supports:
    # Blood Pressure: 140/90
    # Blood Pressure | 140/90 mmHg
    # BP: 140/90
    # ---------------------------------------------------------

    bp_match = re.search(
        r"\b(?:blood\s*pressure|bp)"
        r"\s*(?:[:|\-])?\s*"
        r"(\d{2,3})\s*/\s*(\d{2,3})"
        r"\s*(?:mm\s*hg)?",
        clean_text,
        re.IGNORECASE
    )

    if bp_match:
        result["systolic"] = int(bp_match.group(1))
        result["diastolic"] = int(bp_match.group(2))

        result["blood_pressure"] = (
            f"{result['systolic']}/{result['diastolic']}"
        )

    # ---------------------------------------------------------
    # BLOOD GLUCOSE
    # Supports:
    # Blood Glucose: 140
    # Blood Glucose | 140 mg/dL
    # Blood Sugar: 140
    # Glucose | 140
    # ---------------------------------------------------------

    glucose_match = re.search(
        r"\b(?:blood\s*glucose|blood\s*sugar|glucose)"
        r"\s*(?:[:|\-])?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*(?:mg\s*/?\s*dL)?",
        clean_text,
        re.IGNORECASE
    )

    if glucose_match:
        result["blood_glucose"] = float(
            glucose_match.group(1)
        )

    # ---------------------------------------------------------
    # HEART RATE
    # Supports:
    # Heart Rate: 72 bpm
    # Heart Rate | 72 bpm
    # Pulse: 72
    # ---------------------------------------------------------

    heart_rate_match = re.search(
        r"\b(?:heart\s*rate|pulse)"
        r"\s*(?:[:|\-])?\s*"
        r"(\d{2,3})"
        r"\s*(?:bpm|beats?\s*/?\s*min)?",
        clean_text,
        re.IGNORECASE
    )

    if heart_rate_match:
        result["heart_rate"] = int(
            heart_rate_match.group(1)
        )

    # ---------------------------------------------------------
    # DIAGNOSES AND MEDICINES
    # ---------------------------------------------------------

    diagnosis_lines = []
    medicine_lines = []

    current_section = None

    for line in original_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Normalize table separators.
        normalized_line = re.sub(
            r"\s*\|\s*",
            " | ",
            line
        )

        # Diagnosis section
        if re.match(
            r"^diagnos(?:is|es)"
            r"\s*(?:[:|\-])?\s*$",
            line,
            re.IGNORECASE
        ):
            current_section = "diagnosis"
            continue

        # Medicine section
        if re.match(
            r"^(?:medicines?|medications?|prescriptions?)"
            r"\s*(?:[:|\-])?\s*$",
            line,
            re.IGNORECASE
        ):
            current_section = "medicine"
            continue

        # Stop section parsing when another known field starts.
        if re.match(
            r"^(?:blood\s*pressure|bp|blood\s*glucose|"
            r"blood\s*sugar|glucose|heart\s*rate|pulse|"
            r"age|temperature|weight)"
            r"\s*(?:[:|\-])?",
            line,
            re.IGNORECASE
        ):
            current_section = None
            continue

        if current_section == "diagnosis":
            diagnosis_lines.append(line)

        elif current_section == "medicine":
            medicine_lines.append(line)

    # ---------------------------------------------------------
    # DIAGNOSES
    # ---------------------------------------------------------

    for line in diagnosis_lines:

        parts = re.split(
            r"[,;|]+",
            line
        )

        for item in parts:

            item = item.strip()

            if item:
                result["diagnoses"].append(item)

    result["diagnoses"] = list(
        dict.fromkeys(result["diagnoses"])
    )

    # ---------------------------------------------------------
    # MEDICINES
    # ---------------------------------------------------------

    for line in medicine_lines:

        parts = re.split(
            r"[,;|]+",
            line
        )

        for item in parts:

            item = item.strip()

            if item:
                result["medicines"].append(item)

    result["medicines"] = list(
        dict.fromkeys(result["medicines"])
    )

    return result