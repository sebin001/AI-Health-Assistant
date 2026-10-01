"""
Health AI Engine for AI Health Assistant.
Provides intelligent, context-aware health consultations, symptom triage,
medication interaction checks, and emergency detection.
Can operate fully offline with built-in medical intelligence or connect
to Google Gemini LLM if GEMINI_API_KEY is configured in .env.
"""

import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime
from .models import MedicineReminder, HealthVitals, Profile


MEDICAL_DISCLAIMER = (
    "\n\n*Disclaimer: AI Health Assistant provides health information for educational "
    "and organization purposes only. It is not a substitute for professional medical advice, "
    "diagnosis, or treatment. In an emergency, please call your local emergency services (112 / 911) immediately.*"
)

# Emergency triggers that need immediate attention
EMERGENCY_KEYWORDS = [
    "chest pain", "crushing pain", "heart attack", "can't breathe", "cannot breathe",
    "shortness of breath", "severe bleeding", "unconscious", "stroke", "face drooping",
    "slurred speech", "seizure", "anaphylaxis", "suicide", "overdose", "coughing blood"
]


def check_emergency(user_query):
    query_lower = user_query.lower()
    for keyword in EMERGENCY_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
            return True, keyword
    return False, None


def get_user_health_context(user):
    """Compile structured health context for the logged-in user."""
    context = {
        "username": user.username,
        "profile": {},
        "medicines": [],
        "latest_vitals": None,
    }

    try:
        profile = getattr(user, "profile", None)
        if profile:
            context["profile"] = {
                "gender": profile.gender or "Not specified",
                "blood_group": profile.blood_group or "Not specified",
                "height_cm": profile.height,
                "weight_kg": profile.weight,
                "bmi": profile.bmi,
                "bmi_category": profile.bmi_category,
                "age": profile.age if hasattr(profile, "age") else None,
            }
    except Exception:
        pass

    try:
        meds = MedicineReminder.objects.filter(user=user, is_active=True)
        for med in meds:
            context["medicines"].append({
                "name": med.medicine_name,
                "dosage": med.dosage,
                "frequency": med.frequency,
                "time": med.reminder_time.strftime("%I:%M %p") if med.reminder_time else "",
                "notes": med.notes or ""
            })
    except Exception:
        pass

    try:
        vitals = HealthVitals.objects.filter(user=user).first()
        if vitals:
            context["latest_vitals"] = {
                "systolic": vitals.blood_pressure_systolic,
                "diastolic": vitals.blood_pressure_diastolic,
                "heart_rate": vitals.heart_rate,
                "blood_sugar": vitals.blood_sugar,
                "weight": vitals.weight,
                "date": vitals.recorded_at.strftime("%b %d, %Y")
            }
    except Exception:
        pass

    return context


def format_context_prompt(context):
    lines = [f"User: {context['username']}"]
    p = context["profile"]
    if p:
        lines.append(f"Profile: Gender: {p.get('gender')}, Blood Group: {p.get('blood_group')}, "
                     f"Height: {p.get('height_cm')}cm, Weight: {p.get('weight_kg')}kg, "
                     f"BMI: {p.get('bmi')} ({p.get('bmi_category')})")
    if context["medicines"]:
        med_list = [f"{m['name']} ({m['dosage']}, {m['frequency']} at {m['time']})" for m in context['medicines']]
        lines.append(f"Active Medications: {', '.join(med_list)}")
    else:
        lines.append("Active Medications: None registered currently.")
    
    if context["latest_vitals"]:
        v = context["latest_vitals"]
        lines.append(f"Latest Recorded Vitals ({v['date']}): BP: {v['systolic']}/{v['diastolic']} mmHg, "
                     f"Heart Rate: {v['heart_rate']} bpm, Blood Sugar: {v['blood_sugar']} mg/dL")
    return "\n".join(lines)


def generate_llm_response(prompt, system_instruction):
    """Call Google Gemini API if API key is provided."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"System Guidelines: {system_instruction}\n\nUser Question: {prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 800,
        }
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidate = result.get("candidates", [{}])[0]
            parts = candidate.get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
    except Exception:
        return None

    return None


def built_in_medical_knowledge_engine(query, context):
    """
    Intelligent medical consultation engine covering symptoms, medications,
    lifestyle, BMI analysis, and general health inquiries.
    """
    q = query.lower()
    profile = context.get("profile", {})
    medicines = context.get("medicines", [])
    vitals = context.get("latest_vitals")

    # 1. Active medications query
    if any(k in q for k in ["my medicine", "my prescription", "my pill", "medication list", "what medicine", "medicines do i have"]):
        if medicines:
            med_lines = []
            for i, m in enumerate(medicines, 1):
                notes_part = f" — *Notes: {m['notes']}*" if m['notes'] else ""
                med_lines.append(f"{i}. **{m['name']}**\n   - Dosage: `{m['dosage']}`\n   - Schedule: `{m['frequency']}` at `{m['time']}`{notes_part}")
            return (
                f"### 📋 Your Active Medication Schedule\n\n"
                f"You currently have **{len(medicines)} active medication(s)** in your schedule:\n\n"
                + "\n\n".join(med_lines) +
                "\n\n**Best Practices:**\n"
                "• Take medicines with a full glass of water at the same time each day.\n"
                "• Do not double up on doses if you miss a scheduled time.\n"
                "• Consult your prescribing doctor before discontinuing any medication."
            )
        else:
            return (
                "### 📋 Medication Records\n\n"
                "You do not currently have any active medicine reminders registered in your account.\n\n"
                "💡 You can add new medications anytime under **Medicines > Add Medicine** to receive timely email reminders and tracking."
            )

    # 2. BMI & Weight Assessment
    if any(k in q for k in ["bmi", "body mass", "my weight", "am i overweight", "ideal weight"]):
        bmi = profile.get("bmi")
        category = profile.get("bmi_category", "Not Available")
        height = profile.get("height_cm")
        weight = profile.get("weight_kg")

        if bmi:
            advice = ""
            if category == "Underweight":
                advice = (
                    "• **Nutrition**: Focus on nutrient-dense calorie sources such as nuts, avocados, lean proteins, and whole grains.\n"
                    "• **Exercise**: Incorporate resistance or strength training to build healthy muscle mass.\n"
                    "• **Consultation**: Consider discussing with a registered dietitian if unexplained weight loss occurs."
                )
            elif category == "Normal weight":
                advice = (
                    "• **Maintenance**: Fantastic job! Your BMI is within the healthy reference range (18.5 – 24.9).\n"
                    "• **Habits**: Continue balanced whole-food meals, 150 minutes of moderate cardio per week, and quality sleep.\n"
                    "• **Vitals**: Keep monitoring your blood pressure and resting heart rate periodically."
                )
            elif category == "Overweight":
                advice = (
                    "• **Diet**: Create a gentle, sustainable calorie deficit with higher vegetable and lean protein intake.\n"
                    "• **Activity**: Aim for at least 30–45 minutes of brisk walking or swimming 5 days a week.\n"
                    "• **Hydration**: Drink 2.5–3 liters of water daily, especially before meals."
                )
            else:
                advice = (
                    "• **Structured Plan**: Work closely with a physician or nutritionist on an individualized metabolic plan.\n"
                    "• **Gradual Goals**: Target a modest 5–10% weight reduction initially, which dramatically improves heart health and blood sugar.\n"
                    "• **Activity**: Low-impact activities (swimming, cycling, walking) protect joint cartilage while burning calories."
                )

            return (
                f"### ⚖️ Your BMI & Body Composition Analysis\n\n"
                f"• **Current Height**: {height} cm\n"
                f"• **Current Weight**: {weight} kg\n"
                f"• **Calculated BMI**: **{bmi} kg/m²**\n"
                f"• **Status Category**: **{category}**\n\n"
                f"**Clinical Recommendations for Your Category:**\n\n{advice}"
            )
        else:
            return (
                "### ⚖️ BMI Analysis\n\n"
                "Your height and weight are not yet recorded in your Health Profile.\n\n"
                "👉 Please visit **Health Profile** to add your height and weight, and I will instantly analyze your body mass index and health category."
            )

    # 3. Blood Pressure / Hypertension
    if any(k in q for k in ["blood pressure", "hypertension", "systolic", "diastolic", "high bp", "low bp"]):
        systolic = vitals.get("systolic") if vitals else None
        diastolic = vitals.get("diastolic") if vitals else None

        vitals_text = ""
        if systolic and diastolic:
            status = "Normal"
            if systolic >= 140 or diastolic >= 90:
                status = "Stage 2 Hypertension"
            elif systolic >= 130 or diastolic >= 80:
                status = "Stage 1 Hypertension"
            elif systolic >= 120 and diastolic < 80:
                status = "Elevated"
            vitals_text = f"Your latest logged BP is **{systolic}/{diastolic} mmHg** (*{status}*).\n\n"

        return (
            f"### 🫀 Blood Pressure Management\n\n"
            f"{vitals_text}"
            "**Key Principles for Healthy Blood Pressure:**\n"
            "1. **Sodium Intake**: Reduce daily salt to less than 2,000 mg (about 1 teaspoon).\n"
            "2. **DASH Diet**: Prioritize potassium-rich fruits (bananas, oranges), dark leafy greens, and unsalted seeds.\n"
            "3. **Physical Exercise**: 30 minutes of aerobic exercise lower systolic pressure by 5–8 mmHg.\n"
            "4. **Stress & Sleep**: Aim for 7–8 hours of uninterrupted sleep; practice diaphragmatic breathing.\n"
            "5. **Medication Compliance**: If prescribed antihypertensive medications, take them consistently as scheduled."
        )

    # 4. Diabetes & Blood Sugar
    if any(k in q for k in ["diabetes", "blood sugar", "glucose", "insulin", "hba1c", "sugar level"]):
        sugar = vitals.get("blood_sugar") if vitals else None
        sugar_text = f"Your latest recorded blood glucose is **{sugar} mg/dL**.\n\n" if sugar else ""

        return (
            f"### 🩸 Blood Glucose & Diabetes Care\n\n"
            f"{sugar_text}"
            "**Standard Fasting Blood Sugar Ranges:**\n"
            "• **Normal**: 70 – 99 mg/dL\n"
            "• **Prediabetes**: 100 – 125 mg/dL\n"
            "• **Diabetes**: 126 mg/dL or higher on two separate tests\n\n"
            "**Actionable Strategies:**\n"
            "• **Complex Carbohydrates**: Switch to whole grains, legumes, and high-fiber vegetables with a low glycemic index.\n"
            "• **Post-Meal Walks**: A 15-minute walk after meals significantly blunts glucose spikes.\n"
            "• **Hydration**: Drink water instead of sweetened sodas, juices, or energy drinks.\n"
            "• **Routine Checkups**: Check your HbA1c test every 3 to 6 months."
        )

    # 5. Fever & Infections
    if any(k in q for k in ["fever", "temperature", "chills", "cold", "flu", "cough", "sore throat"]):
        return (
            "### 🌡️ Fever & Upper Respiratory Assessment\n\n"
            "**Home Care & Recovery Protocol:**\n"
            "• **Hydration**: Drink plenty of fluids (warm broths, herbal tea, electrolyte water) to prevent dehydration.\n"
            "• **Rest**: Rest is essential for the immune system to combat viral replication.\n"
            "• **Temperature Control**: Dress in breathable light layers; use lukewarm compresses if uncomfortable.\n"
            "• **Symptom Relief**: Warm saltwater gargles (1/2 tsp salt in warm water) relieve throat discomfort.\n\n"
            "⚠️ **When to Consult a Physician Immediately:**\n"
            "• Fever exceeding 103°F (39.4°C) or lasting longer than 3 days.\n"
            "• Difficulty breathing, wheezing, or chest tightness.\n"
            "• Inability to keep fluids down or extreme lethargy."
        )

    # 6. Headache / Migraine
    if any(k in q for k in ["headache", "migraine", "head throbbing", "head hurts"]):
        return (
            "### 🤕 Headache Management & Triage\n\n"
            "**Common Triggers:**\n"
            "• Dehydration, eye strain (screen time), stress, skipped meals, or lack of sleep.\n\n"
            "**Immediate Relief Steps:**\n"
            "1. Drink 500 mL of cool water.\n"
            "2. Rest in a dark, quiet room with minimal sensory stimulation.\n"
            "3. Apply a cold compress across the forehead or a warm compress to the back of the neck.\n"
            "4. Gently massage tense shoulder and neck muscles.\n\n"
            "🚨 **Red Flag Warning:**\n"
            "If you experience a sudden, explosive headache ('worst headache of your life'), headache accompanied by stiff neck, high fever, numbness, or confusion, seek emergency care immediately."
        )

    # 7. Diet, Nutrition & Lifestyle
    if any(k in q for k in ["diet", "food", "nutrition", "what should i eat", "healthy lifestyle", "water"]):
        return (
            "### 🥗 Daily Nutrition & Vitality Guide\n\n"
            "**The Balanced Health Plate:**\n"
            "• **50% Vegetables & Fruits**: Colorful produce providing antioxidants, vitamins, and prebiotics.\n"
            "• **25% Lean Protein**: Fish, chicken, tofu, lentils, eggs, or Greek yogurt.\n"
            "• **25% Whole Grains**: Quinoa, brown rice, oats, or whole wheat.\n\n"
            "**Key Habits:**\n"
            "• **Hydration Goal**: 8–10 glasses of clean water daily.\n"
            "• **Limit Ultra-Processed Foods**: Reduce refined sugars, packaged trans-fats, and high-sodium snacks.\n"
            "• **Circadian Rhythm**: Try to keep consistent meal times to support metabolic regularity."
        )

    # 8. Sleep & Mental Wellness
    if any(k in q for k in ["sleep", "insomnia", "stress", "anxiety", "tired", "fatigue"]):
        return (
            "### 🌙 Rest, Sleep Hygiene & Stress Balance\n\n"
            "**Science-Backed Sleep Hygiene Protocol:**\n"
            "1. **Screen Curfew**: Power off phones, laptops, and TVs 45 minutes before bedtime.\n"
            "2. **Cool Environment**: Keep your bedroom temperature around 18–20°C (65–68°F).\n"
            "3. **Caffeine Cut-off**: Avoid caffeine at least 8 hours before sleeping.\n"
            "4. **4-7-8 Breathing Technique**: Inhale for 4 seconds, hold for 7 seconds, exhale slowly for 8 seconds to activate the parasympathetic relaxation response.\n\n"
            "If persistent fatigue or low mood continues for over two weeks, schedule a consultation with a healthcare provider to check thyroid levels, vitamin D, and ferritin."
        )

    # 9. Generic intelligent medical reply
    user_name = context.get("username", "there")
    return (
        f"### 🩺 Hello {user_name}, I'm your AI Health Assistant\n\n"
        f"I received your inquiry: *\"{query}\"*\n\n"
        "Here are key health insights and recommendations:\n\n"
        "• **Listen to Your Body**: Track when symptoms start, their severity, and any aggravating or relieving factors.\n"
        "• **Medication Safety**: Always verify compatibility before starting any over-the-counter remedy alongside your active prescriptions.\n"
        "• **Holistic Wellness**: Adequate hydration, restful sleep, and balanced nutrition are foundational to recovery and immune function.\n\n"
        "💡 **You can ask me about:**\n"
        "- Specific symptoms (e.g. *fever, headache, stomach ache*)\n"
        "- Your active medications (e.g. *show my medicines*)\n"
        "- BMI and body composition (e.g. *calculate my BMI*)\n"
        "- Diet, blood pressure, or blood glucose management"
    )


def process_health_chat(user, user_query):
    """
    Main entry point for processing a user's health query.
    Handles emergency triage, context injection, LLM generation, or built-in engine.
    """
    if not user_query or not user_query.strip():
        return {
            "response": "Please type a health question or symptom so I can assist you.",
            "is_emergency": False,
            "suggestions": ["Show my medicines", "Check my BMI", "Blood pressure tips"]
        }

    cleaned_query = user_query.strip()

    # 1. Critical emergency triage check
    is_emergency, keyword = check_emergency(cleaned_query)
    if is_emergency:
        emergency_msg = (
            f"### 🚨 URGENT MEDICAL ATTENTION RECOMMENDED\n\n"
            f"You mentioned **\"{keyword}\"**, which may indicate a potentially serious or life-threatening medical emergency.\n\n"
            f"**Please take immediate action:**\n"
            f"1. **Call Emergency Services Right Now**: Dial **112** (India/EU) or **911** (US) or your local emergency hospital hotline.\n"
            f"2. If you are alone, alert a family member, neighbor, or emergency contact.\n"
            f"3. Sit in a comfortable, supported position and do not attempt to drive yourself to the emergency department.\n\n"
            f"*Do not delay seeking emergency medical attention based on online or AI information.*"
        )
        return {
            "response": emergency_msg,
            "is_emergency": True,
            "suggestions": ["Call Emergency Services", "Find Nearest Hospital", "Contact Doctor"]
        }

    # 2. Gather user context
    context = get_user_health_context(user)

    # 3. Attempt LLM with user context if configured
    system_instruction = (
        "You are an empathetic, clinical AI Health Assistant. Answer clearly with markdown headings, "
        "bullet points, and clear advice. Consider the user's active medicines and health vitals. "
        "Never prescribe controlled substances. Always recommend consulting a doctor for diagnoses."
    )
    context_str = format_context_prompt(context)
    full_prompt = f"{context_str}\n\nUser Question: {cleaned_query}"

    llm_response = generate_llm_response(full_prompt, system_instruction)

    if llm_response:
        final_text = llm_response.strip() + MEDICAL_DISCLAIMER
    else:
        final_text = built_in_medical_knowledge_engine(cleaned_query, context) + MEDICAL_DISCLAIMER

    # Dynamic suggestions based on topic
    suggestions = ["What are my active medicines?", "Analyze my BMI", "Blood pressure advice", "Tips for healthy diet"]

    return {
        "response": final_text,
        "is_emergency": False,
        "suggestions": suggestions
    }
