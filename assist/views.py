from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone as django_timezone

import numpy as np

from .forms import (
    HealthVitalsForm,
    RegistrationForm,
    ProfileForm,
    MedicineReminderForm,
)

from .models import (
    Appointment,
    Doctor,
    DoctorAvailability,
    HealthRecord,
    Profile,
    FaceEmbedding,
    MedicineReminder,
    HealthVitals,
    MedicineLog,
    AIChatMessage,
    UserActivity,
)

from .face_engine import (
    detect_faces,
    get_face_embedding,
)

from datetime import datetime, date, timedelta
from django.views.decorators.http import require_POST
from django.db import transaction

from .bp_assessment import assess_blood_pressure
from .health_assessment import generate_health_assessment
from .document_ai import extract_medical_document_text
from .medical_extractor import extract_medical_information


# ============================================================
# HOME
# ============================================================

def home(request):

    return render(
        request,
        "assist/home.html"
    )


# ============================================================
# REGISTER
# ============================================================

def register(request):

    if request.method == "POST":

        form = RegistrationForm(
            request.POST
        )

        if form.is_valid():

            # ------------------------------------------------
            # CREATE USER
            # ------------------------------------------------

            user = form.save()

            # ------------------------------------------------
            # CREATE PROFILE
            # ------------------------------------------------

            Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data[
                    "phone_number"
                ]
            )

            # ------------------------------------------------
            # WELCOME EMAIL
            # ------------------------------------------------

            send_mail(

                subject=(
                    "Welcome to AI Health Assistant – "
                    "Your Health Journey Starts Here!"
                ),

                message=(

                    f"Hello {user.username},\n\n"

                    "🌿 WELCOME TO AI HEALTH ASSISTANT!\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                    "Your AI Health Assistant account has been "
                    "successfully created! 🎉\n\n"

                    "We are excited to have you with us. "
                    "AI Health Assistant is designed to help you "
                    "manage your health information and make your "
                    "health journey smarter, simpler, and more "
                    "organized.\n\n"

                    "✨ WHAT YOU CAN DO WITH AI HEALTH ASSISTANT\n\n"

                    "• Manage your personal health profile\n"
                    "• Keep track of your medicines and reminders\n"
                    "• Organize your health information\n"
                    "• Get AI-powered health assistance\n"
                    "• Manage appointments and health activities\n"
                    "• Use Face ID for convenient and secure login\n\n"

                    "💡 A FEW SIMPLE TIPS\n\n"

                    "1. Complete your health profile with accurate "
                    "information.\n"

                    "2. Keep your medicine information updated.\n"

                    "3. Check your reminders regularly.\n"

                    "4. Use the AI assistant to understand "
                    "health-related information more easily.\n"

                    "5. Keep your account secure and never share "
                    "your password.\n\n"

                    "❤️ YOUR HEALTH MATTERS\n\n"

                    "Small steps today can make a big difference "
                    "tomorrow. Stay informed, stay organized, and "
                    "take care of yourself.\n\n"

                    "Your journey toward smarter health management "
                    "starts here!\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

                    "AI HEALTH ASSISTANT\n"
                    "Smart. Simple. Healthier.\n"

                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

                    "Thank you for joining us.\n"
                    "We wish you a healthy and happy journey!\n\n"

                    "Best wishes,\n"
                    "AI Health Assistant Team"
                ),

                from_email=None,

                recipient_list=[
                    user.email
                ],

                fail_silently=False,
            )

            # ------------------------------------------------
            # STORE USER ID TEMPORARILY
            # FOR FACE ID REGISTRATION
            # ------------------------------------------------

            request.session[
                "face_registration_user_id"
            ] = user.id

            # ------------------------------------------------
            # REDIRECT TO FACE ID REGISTRATION
            # ------------------------------------------------

            return redirect(
                "face_register"
            )

    else:

        form = RegistrationForm()

    return render(
        request,
        "assist/register.html",
        {
            "form": form
        }
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # ------------------------------------------------
        # USERNAME VALIDATION
        # ------------------------------------------------

        if not username:

            messages.error(
                request,
                "Please enter your username."
            )

            return render(
                request,
                "assist/login.html"
            )

        # ------------------------------------------------
        # PASSWORD VALIDATION
        # ------------------------------------------------

        if not password:

            messages.error(
                request,
                "Please enter your password."
            )

            return render(
                request,
                "assist/login.html"
            )

        # ------------------------------------------------
        # AUTHENTICATE USER
        # ------------------------------------------------

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # ------------------------------------------------
        # SUCCESSFUL LOGIN
        # ------------------------------------------------

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "dashboard"
            )

        # ------------------------------------------------
        # FAILED LOGIN
        # ------------------------------------------------

        messages.error(
            request,
            "Incorrect username or password."
        )

    return render(
        request,
        "assist/login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    user = request.user

    # --------------------------------------------------------
    # ACTIVE MEDICINES
    # --------------------------------------------------------

    active_medicines = MedicineReminder.objects.filter(
        user=user,
        is_active=True
    ).order_by(
        "reminder_time"
    )

    medicine_count = active_medicines.count()

    # --------------------------------------------------------
    # MEDICINE REMINDERS
    # --------------------------------------------------------

    reminder_count = active_medicines.filter(
        reminder_time__isnull=False
    ).count()

    # --------------------------------------------------------
    # HEALTH RECORDS
    # --------------------------------------------------------

    health_record_count = HealthRecord.objects.filter(
        user=user
    ).count()

    # --------------------------------------------------------
    # USER ACTIVITIES
    # --------------------------------------------------------

    activity_count = UserActivity.objects.filter(
        user=user
    ).count()

    recent_activities = UserActivity.objects.filter(
        user=user
    ).order_by(
        "-created_at"
    )[:5]

    # --------------------------------------------------------
    # TODAY'S MEDICINE LOGS
    # --------------------------------------------------------

    today = date.today()

    today_logs = {
        log.medicine_id: log.status
        for log in MedicineLog.objects.filter(
            user=user,
            log_date=today
        )
    }

    taken_count = sum(
        1
        for status in today_logs.values()
        if status == "TAKEN"
    )

    # --------------------------------------------------------
    # MEDICINE ADHERENCE
    # --------------------------------------------------------

    adherence_percentage = (
        round(
            taken_count / medicine_count * 100
        )
        if medicine_count > 0
        else 100
    )

    # --------------------------------------------------------
    # TODAY'S MEDICINE CHECKLIST
    # --------------------------------------------------------

    today_checklist = []

    for med in active_medicines:

        today_checklist.append({
            "medicine": med,
            "status": today_logs.get(
                med.id,
                "PENDING"
            )
        })

    # --------------------------------------------------------
    # LATEST HEALTH VITALS
    # --------------------------------------------------------

    latest_vitals = HealthVitals.objects.filter(
        user=user
    ).first()

    # --------------------------------------------------------
    # TOTAL VITALS
    # --------------------------------------------------------

    vitals_count = HealthVitals.objects.filter(
        user=user
    ).count()

    # --------------------------------------------------------
    # VITALS HISTORY
    # --------------------------------------------------------

    vitals_history = list(
        HealthVitals.objects.filter(
            user=user
        ).order_by(
            "-recorded_at"
        )[:7]
    )

    vitals_history.reverse()

    # --------------------------------------------------------
    # CHART DATA
    #
    # Keep None values so every chart list has the same
    # number of positions as chart_labels.
    # --------------------------------------------------------

    chart_labels = [
        v.recorded_at.strftime("%b %d")
        for v in vitals_history
    ]

    chart_systolic = [
        v.blood_pressure_systolic
        if v.blood_pressure_systolic is not None
        else None
        for v in vitals_history
    ]

    chart_diastolic = [
        v.blood_pressure_diastolic
        if v.blood_pressure_diastolic is not None
        else None
        for v in vitals_history
    ]

    chart_sugar = [
        v.blood_sugar
        if v.blood_sugar is not None
        else None
        for v in vitals_history
    ]

    chart_weights = [
        v.weight
        if v.weight is not None
        else None
        for v in vitals_history
    ]

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    profile = getattr(
        user,
        "profile",
        None
    )

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    return render(
        request,
        "assist/dashboard.html",
        {
            # Main statistics
            "medicine_count": medicine_count,
            "reminder_count": reminder_count,
            "health_record_count": health_record_count,
            "activity_count": activity_count,
            "vitals_count": vitals_count,

            # Recent activity
            "recent_activities": recent_activities,

            # Medicine data
            "today_taken_count": taken_count,
            "adherence_percentage": adherence_percentage,
            "today_checklist": today_checklist,

            # Health vitals
            "latest_vitals": latest_vitals,

            # Chart data
            "chart_labels": chart_labels,
            "chart_systolic": chart_systolic,
            "chart_diastolic": chart_diastolic,
            "chart_sugar": chart_sugar,
            "chart_weights": chart_weights,

            # Profile
            "profile": profile,
        }
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been successfully logged out."
    )

    return redirect(
        "login"
    )


# ============================================================
# FACE ID REGISTRATION PAGE
# ============================================================

def face_register(request):

    user_id = request.session.get(
        "face_registration_user_id"
    )

    if not user_id:

        messages.error(
            request,
            "Please create an account first."
        )

        return redirect(
            "register"
        )

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.pop(
            "face_registration_user_id",
            None
        )

        messages.error(
            request,
            "User account not found. Please register again."
        )

        return redirect(
            "register"
        )

    return render(
        request,
        "assist/face_register.html",
        {
            "face_user": user
        }
    )


# ============================================================
# FACE DETECTION API
# ============================================================

@csrf_protect
def face_detect_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    image_data = request.POST.get(
        "image"
    )

    if not image_data:

        return JsonResponse(
            {
                "success": False,
                "message": "No camera image received."
            },
            status=400
        )

    result = detect_faces(
        image_data
    )

    status_code = (
        200
        if result["success"]
        else 400
    )

    return JsonResponse(
        result,
        status=status_code
    )


# ============================================================
# FACE SAVE API
# ============================================================

@csrf_protect
def face_save_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    user_id = request.session.get(
        "face_registration_user_id"
    )

    if not user_id:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Registration session expired. "
                    "Please create your account again."
                )
            },
            status=400
        )

    try:

        user = User.objects.get(
            id=user_id
        )

    except User.DoesNotExist:

        request.session.pop(
            "face_registration_user_id",
            None
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "User account not found. "
                    "Please register again."
                )
            },
            status=400
        )

    image_data = request.POST.get(
        "image"
    )

    if not image_data:

        return JsonResponse(
            {
                "success": False,
                "message": "No camera image received."
            },
            status=400
        )

    result = get_face_embedding(
        image_data
    )

    if not result["success"]:

        return JsonResponse(
            result,
            status=400
        )

    embedding = result["embedding"]

    FaceEmbedding.objects.update_or_create(
        user=user,
        defaults={
            "embedding": embedding
        }
    )

    request.session.pop(
        "face_registration_user_id",
        None
    )

    messages.success(
        request,
        (
            "Face ID registration successful! "
            "Your account is ready. Please login."
        )
    )

    return JsonResponse(
        {
            "success": True,
            "message": (
                "Face ID registration successful! "
                "Your account is ready."
            )
        }
    )


# ============================================================
# FACE ID LOGIN API
# ============================================================

@csrf_protect
def face_login_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    image_data = request.POST.get(
        "image"
    )

    if not image_data:

        return JsonResponse(
            {
                "success": False,
                "message": "No camera image received."
            },
            status=400
        )

    result = get_face_embedding(
        image_data
    )

    if not result["success"]:

        return JsonResponse(
            result,
            status=400
        )

    captured_embedding = np.array(
        result["embedding"],
        dtype=np.float32
    )

    best_user = None
    best_similarity = -1.0

    face_records = FaceEmbedding.objects.select_related(
        "user"
    )

    for face_record in face_records:

        saved_embedding = np.array(
            face_record.embedding,
            dtype=np.float32
        )

        captured_norm = np.linalg.norm(
            captured_embedding
        )

        saved_norm = np.linalg.norm(
            saved_embedding
        )

        if captured_norm == 0 or saved_norm == 0:

            continue

        similarity = float(
            np.dot(
                captured_embedding,
                saved_embedding
            )
            /
            (
                captured_norm
                *
                saved_norm
            )
        )

        if similarity > best_similarity:

            best_similarity = similarity
            best_user = face_record.user

    FACE_MATCH_THRESHOLD = 0.45

    if (
        best_user is None
        or best_similarity < FACE_MATCH_THRESHOLD
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Face not recognized. "
                    "Please try again."
                ),
                "similarity": round(
                    best_similarity,
                    3
                )
            },
            status=401
        )

    login(
        request,
        best_user
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Face ID login successful.",
            "username": best_user.username,
            "similarity": round(
                best_similarity,
                3
            ),
            "redirect": "/dashboard/"
        }
    )


# ============================================================
# HEALTH PROFILE
# ============================================================

@login_required
def health_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone_number": ""
        }
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            UserActivity.objects.create(
                user=request.user,
                activity_type="profile_updated",
                title="Profile updated",
                description="Health profile was updated.",
            )

            messages.success(
                request,
                (
                    "Your health profile has been "
                    "updated successfully."
                )
            )

            return redirect(
                "health_profile"
            )

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "assist/health_profile.html",
        {
            "form": form,
            "profile": profile,
        }
    )


# ============================================================
# ADD MEDICINE REMINDER
# ============================================================

@login_required
def medicine_add(request):

    if request.method == "POST":

        form = MedicineReminderForm(request.POST)

        if form.is_valid():

            medicine = form.save(commit=False)
            medicine.user = request.user
            medicine.save()

            UserActivity.objects.create(
                user=request.user,
                activity_type="medicine_added",
                title="Medicine reminder added",
                description=(
                    f"Added medicine reminder: "
                    f"{medicine.medicine_name}"
                ),
            )

            messages.success(
                request,
                "Medicine reminder added successfully."
            )

            return redirect(
                "medicine_add"
            )

    else:

        form = MedicineReminderForm()

    return render(
        request,
        "assist/medicine_add.html",
        {
            "form": form
        }
    )


# ============================================================
# MY MEDICINES
# ============================================================

@login_required
def medicine_list(request):

    medicines = MedicineReminder.objects.filter(
        user=request.user
    ).order_by(
        "reminder_time"
    )

    return render(
        request,
        "assist/medicine_list.html",
        {
            "medicines": medicines
        }
    )


# ============================================================
# EDIT MEDICINE
# ============================================================

@login_required
def medicine_edit(request, medicine_id):

    medicine = get_object_or_404(
        MedicineReminder,
        id=medicine_id,
        user=request.user
    )

    if request.method == "POST":

        form = MedicineReminderForm(
            request.POST,
            instance=medicine
        )

        if form.is_valid():

            updated_medicine = form.save(
                commit=False
            )

            updated_medicine.user = request.user
            updated_medicine.save()

            UserActivity.objects.create(
                user=request.user,
                activity_type="medicine_updated",
                title="Medicine reminder updated",
                description=(
                    f"Updated medicine reminder: "
                    f"{updated_medicine.medicine_name}"
                ),
            )

            messages.success(
                request,
                "Medicine reminder updated successfully."
            )

            return redirect(
                "medicine_list"
            )

    else:

        form = MedicineReminderForm(
            instance=medicine
        )

    return render(
        request,
        "assist/medicine_edit.html",
        {
            "form": form,
            "medicine": medicine
        }
    )


# ============================================================
# DELETE MEDICINE
# ============================================================

@login_required
def medicine_delete(request, medicine_id):

    medicine = get_object_or_404(
        MedicineReminder,
        id=medicine_id,
        user=request.user
    )

    if request.method == "POST":

        medicine_name = medicine.medicine_name

        UserActivity.objects.create(
            user=request.user,
            activity_type="medicine_deleted",
            title="Medicine reminder deleted",
            description=(
                f"Deleted medicine reminder: "
                f"{medicine_name}"
            ),
        )

        medicine.delete()

        messages.success(
            request,
            f"{medicine_name} has been deleted successfully."
        )

        return redirect(
            "medicine_list"
        )

    return render(
        request,
        "assist/medicine_delete.html",
        {
            "medicine": medicine
        }
    )


# ============================================================
# TOGGLE MEDICINE REMINDER STATUS
# ============================================================

@login_required
def medicine_toggle_status(request, medicine_id):

    if request.method != "POST":

        return redirect(
            "medicine_list"
        )

    medicine = get_object_or_404(
        MedicineReminder,
        id=medicine_id,
        user=request.user
    )

    medicine.is_active = not medicine.is_active

    medicine.save(
        update_fields=[
            "is_active",
            "updated_at"
        ]
    )

    if medicine.is_active:

        messages.success(
            request,
            f"{medicine.medicine_name} reminder activated."
        )

    else:

        messages.warning(
            request,
            f"{medicine.medicine_name} reminder paused."
        )

    return redirect(
        "medicine_list"
    )


# ============================================================
# AI HEALTH ASSISTANT
# ============================================================

@login_required
def ai_assistant(request):

    chat_history = AIChatMessage.objects.filter(
        user=request.user
    ).order_by(
        "created_at"
    )[:40]

    return render(
        request,
        "assist/ai_assistant.html",
        {
            "chat_history": chat_history,
        }
    )


# ============================================================
# AI CHAT API
# ============================================================

@login_required
@csrf_protect
def ai_chat_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST required"
            },
            status=405
        )

    user_message = request.POST.get(
        "message",
        ""
    ).strip()

    if not user_message:

        return JsonResponse(
            {
                "success": False,
                "message": "Message is empty"
            },
            status=400
        )

    try:

        AIChatMessage.objects.create(
            user=request.user,
            role="user",
            content=user_message
        )

        from .ai_service import ask_ai

        ai_response = ask_ai(
            user_message
        )

        AIChatMessage.objects.create(
            user=request.user,
            role="assistant",
            content=ai_response
        )

        UserActivity.objects.create(
            user=request.user,
            activity_type="ai_chat",
            title="AI Health Assistant used",
            description="User interacted with the AI Health Assistant.",
        )

        return JsonResponse(
            {
                "success": True,
                "response": ai_response,
                "is_emergency": False,
                "suggestions": []
            }
        )

    except Exception as error:

        print(
            "AI CHAT ERROR:",
            error
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "AI service is temporarily unavailable. "
                    "Please try again."
                )
            },
            status=500
        )


# ============================================================
# BLOOD PRESSURE ASSESSMENT API
# ============================================================

@login_required
def bp_assessment_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "Only POST requests are allowed."
            },
            status=405
        )

    try:

        systolic = request.POST.get(
            "systolic"
        )

        diastolic = request.POST.get(
            "diastolic"
        )

        if systolic is None or diastolic is None:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Systolic and diastolic values "
                        "are required."
                    )
                },
                status=400
            )

        result = assess_blood_pressure(
            systolic=systolic,
            diastolic=diastolic
        )

        return JsonResponse(
            {
                "success": True,
                "result": result
            }
        )

    except ValueError as error:

        return JsonResponse(
            {
                "success": False,
                "message": str(error)
            },
            status=400
        )

    except Exception:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to assess blood pressure."
                )
            },
            status=500
        )


# ============================================================
# CLEAR AI CHAT
# ============================================================

@login_required
@csrf_protect
def ai_clear_chat(request):

    if request.method == "POST":

        AIChatMessage.objects.filter(
            user=request.user
        ).delete()

        return JsonResponse(
            {
                "success": True,
                "message": "Chat history cleared."
            }
        )

    return JsonResponse(
        {
            "success": False,
            "message": "POST required"
        },
        status=405
    )


# ============================================================
# HEALTH VITALS - ADD / LIST
# ============================================================

@login_required
def health_vitals_view(request):

    if request.method == "POST":

        form = HealthVitalsForm(
            request.POST
        )

        if form.is_valid():

            vitals = form.save(
                commit=False
            )

            vitals.user = request.user
            vitals.save()

            UserActivity.objects.create(
                user=request.user,
                activity_type="vitals_added",
                title="Health vitals recorded",
                description=(
                    "A new health-vitals reading "
                    "was recorded."
                ),
            )

            messages.success(
                request,
                "Health vitals recorded successfully."
            )

            return redirect(
                "health_vitals"
            )

    else:

        form = HealthVitalsForm()

    vitals = HealthVitals.objects.filter(
        user=request.user
    ).order_by(
        "-recorded_at"
    )

    return render(
        request,
        "assist/health_vitals.html",
        {
            "form": form,
            "vitals": vitals,
        },
    )


# ============================================================
# HEALTH VITALS - EDIT
# ============================================================

@login_required
def health_vitals_edit(request, vitals_id):

    vitals = get_object_or_404(
        HealthVitals,
        id=vitals_id,
        user=request.user
    )

    if request.method == "POST":

        form = HealthVitalsForm(
            request.POST,
            instance=vitals
        )

        if form.is_valid():

            form.save()

            UserActivity.objects.create(
                user=request.user,
                activity_type="vitals_updated",
                title="Health vitals updated",
                description=(
                    "An existing health-vitals "
                    "reading was updated."
                ),
            )

            messages.success(
                request,
                "Health vitals updated successfully."
            )

            return redirect(
                "health_vitals"
            )

    else:

        form = HealthVitalsForm(
            instance=vitals
        )

    return render(
        request,
        "assist/health_vitals_edit.html",
        {
            "form": form,
            "vitals": vitals,
        },
    )


# ============================================================
# HEALTH VITALS - DELETE
# ============================================================

@login_required
def health_vitals_delete(request, vitals_id):

    vitals = get_object_or_404(
        HealthVitals,
        id=vitals_id,
        user=request.user
    )

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    UserActivity.objects.create(
        user=request.user,
        activity_type="vitals_deleted",
        title="Health vitals deleted",
        description=(
            "A health-vitals reading was deleted."
        ),
    )

    vitals.delete()

    return JsonResponse(
        {
            "success": True,
            "message": (
                "Health vitals deleted successfully."
            )
        }
    )


# ============================================================
# HEALTH VITALS API
# ============================================================

@login_required
@csrf_protect
def log_vitals_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST required"
            },
            status=405
        )

    try:

        systolic = request.POST.get(
            "systolic"
        )

        diastolic = request.POST.get(
            "diastolic"
        )

        heart_rate = request.POST.get(
            "heart_rate"
        )

        blood_sugar = request.POST.get(
            "blood_sugar"
        )

        weight = request.POST.get(
            "weight"
        )

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

        # ------------------------------------------------
        # CREATE VITALS
        # ------------------------------------------------

        vitals = HealthVitals(
            user=request.user,
            notes=notes
        )

        if systolic:

            vitals.blood_pressure_systolic = int(
                systolic
            )

        if diastolic:

            vitals.blood_pressure_diastolic = int(
                diastolic
            )

        if heart_rate:

            vitals.heart_rate = int(
                heart_rate
            )

        if blood_sugar:

            vitals.blood_sugar = float(
                blood_sugar
            )

        if weight:

            vitals.weight = float(
                weight
            )

        vitals.save()

        # ------------------------------------------------
        # UPDATE PROFILE WEIGHT
        # ------------------------------------------------

        if (
            weight
            and hasattr(
                request.user,
                "profile"
            )
        ):

            request.user.profile.weight = float(
                weight
            )

            request.user.profile.save(
                update_fields=[
                    "weight",
                    "updated_at"
                ]
            )

        # ------------------------------------------------
        # ACTIVITY
        # ------------------------------------------------

        UserActivity.objects.create(
            user=request.user,
            activity_type="vitals_added",
            title="Health vitals recorded",
            description=(
                "Health vitals were recorded "
                "through the vitals API."
            ),
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Vitals logged successfully."
            }
        )

    except Exception as error:

        return JsonResponse(
            {
                "success": False,
                "message": str(error)
            },
            status=400
        )


# ============================================================
# MEDICINE INTAKE API
# ============================================================

@login_required
@csrf_protect
def log_medicine_intake_api(
    request,
    medicine_id
):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST required"
            },
            status=405
        )

    try:

        medicine = MedicineReminder.objects.get(
            id=medicine_id,
            user=request.user
        )

        status = request.POST.get(
            "status",
            "TAKEN"
        ).upper()

        if status not in [
            "TAKEN",
            "SKIPPED",
            "SNOOZED"
        ]:

            status = "TAKEN"

        today = date.today()

        log, created = MedicineLog.objects.update_or_create(

            medicine=medicine,

            log_date=today,

            defaults={
                "user": request.user,
                "status": status
            }

        )

        return JsonResponse(
            {
                "success": True,
                "status": log.status,
                "medicine_name": medicine.medicine_name,
                "message": (
                    f"{medicine.medicine_name} "
                    f"marked as "
                    f"{log.status.lower()}."
                )
            }
        )

    except MedicineReminder.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "Medicine not found"
            },
            status=404
        )


# ============================================================
# MEDICINE ALARM CHECK
# ============================================================

@login_required
def medicine_alarm_check(request):

    now = django_timezone.localtime()

    today = now.date()

    medicines = MedicineReminder.objects.filter(
        user=request.user,
        is_active=True,
        start_date__lte=today
    )

    due_medicines = []

    for medicine in medicines:

        if (
            medicine.end_date
            and medicine.end_date < today
        ):

            continue

        reminder_time = medicine.reminder_time

        if (
            reminder_time.hour == now.hour
            and reminder_time.minute == now.minute
        ):

            due_medicines.append(
                {
                    "id": medicine.id,
                    "medicine_name": medicine.medicine_name,
                    "dosage": medicine.dosage,
                    "time": reminder_time.strftime(
                        "%I:%M %p"
                    ),
                }
            )

    return JsonResponse(
        {
            "success": True,
            "medicines": due_medicines,
        }
    )


# ============================================================
# APPOINTMENT HELPERS
# ============================================================

def parse_selected_date(value):

    if not value:

        raise ValueError(
            "Date is required."
        )

    try:

        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    except ValueError as exc:

        raise ValueError(
            "Invalid date format."
        ) from exc


def generate_appointment_slots(
    doctor,
    appointment_date
):

    day_name = appointment_date.strftime(
        "%A"
    )

    availability = DoctorAvailability.objects.filter(
        doctor=doctor,
        day_of_week=day_name,
        is_available=True
    ).first()

    if not availability:

        return []

    start_datetime = datetime.combine(
        appointment_date,
        availability.start_time
    )

    end_datetime = datetime.combine(
        appointment_date,
        availability.end_time
    )

    slot_duration = timedelta(
        minutes=availability.slot_duration
    )

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            status__in=[
                "Pending",
                "Confirmed"
            ]
        ).values_list(
            "appointment_time",
            flat=True
        )
    )

    available_slots = []

    current_datetime = start_datetime

    while (
        current_datetime + slot_duration
        <= end_datetime
    ):

        slot_time = current_datetime.time()

        if slot_time not in booked_times:

            available_slots.append(
                slot_time
            )

        current_datetime += slot_duration

    return available_slots


# ============================================================
# DOCTOR AVAILABLE SLOTS
# ============================================================

@login_required
def doctor_available_slots_api(request):

    doctor_id = request.GET.get(
        "doctor_id"
    )

    appointment_date = request.GET.get(
        "date"
    )

    if not doctor_id or not appointment_date:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Doctor and date are required."
                )
            },
            status=400
        )

    try:

        doctor = Doctor.objects.get(
            id=doctor_id,
            is_active=True
        )

    except Doctor.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "Doctor not found."
            },
            status=404
        )

    try:

        selected_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid date format."
            },
            status=400
        )

    slots = generate_appointment_slots(
        doctor,
        selected_date
    )

    formatted_slots = [
        {
            "value": slot.strftime(
                "%H:%M"
            ),
            "label": slot.strftime(
                "%I:%M %p"
            )
        }
        for slot in slots
    ]

    return JsonResponse(
        {
            "success": True,
            "doctor": doctor.name,
            "date": selected_date.isoformat(),
            "slots": formatted_slots
        }
    )


# ============================================================
# BOOK APPOINTMENT
# ============================================================

@login_required
@require_POST
def book_appointment_api(request):

    doctor_id = request.POST.get(
        "doctor_id"
    )

    appointment_date = request.POST.get(
        "date"
    )

    appointment_time = request.POST.get(
        "time"
    )

    patient_notes = request.POST.get(
        "patient_notes",
        ""
    ).strip()

    if (
        not doctor_id
        or not appointment_date
        or not appointment_time
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Doctor, date and appointment "
                    "time are required."
                )
            },
            status=400
        )

    try:

        doctor = Doctor.objects.get(
            id=doctor_id,
            is_active=True
        )

    except Doctor.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "Doctor not found."
            },
            status=404
        )

    try:

        selected_date = parse_selected_date(
            appointment_date
        )

    except ValueError:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid appointment date."
            },
            status=400
        )

    if (
        selected_date
        < django_timezone.now().date()
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "You cannot book an appointment "
                    "for a past date."
                )
            },
            status=400
        )

    try:

        selected_time = datetime.strptime(
            appointment_time,
            "%H:%M"
        ).time()

    except ValueError:

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid appointment time."
            },
            status=400
        )

    available_slots = generate_appointment_slots(
        doctor,
        selected_date
    )

    if selected_time not in available_slots:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "This appointment slot is "
                    "no longer available."
                )
            },
            status=409
        )

    with transaction.atomic():

        already_booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date,
            appointment_time=selected_time,
            status__in=[
                "Pending",
                "Confirmed"
            ]
        ).exists()

        if already_booked:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "This appointment slot "
                        "has already been booked."
                    )
                },
                status=409
            )

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            appointment_date=selected_date,
            appointment_time=selected_time,
            status="Pending",
            patient_notes=patient_notes
        )

    # --------------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------------

    UserActivity.objects.create(
        user=request.user,
        activity_type="appointment_booked",
        title="Appointment booked",
        description=(
            f"Appointment booked with "
            f"{doctor.name} on "
            f"{selected_date.strftime('%d %B %Y')} "
            f"at "
            f"{selected_time.strftime('%I:%M %p')}."
        ),
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment": {
                "id": appointment.id,
                "doctor": doctor.name,
                "specialization": doctor.specialization,
                "hospital": doctor.hospital.name,
                "date": appointment.appointment_date.isoformat(),
                "time": appointment.appointment_time.strftime(
                    "%I:%M %p"
                ),
                "status": appointment.status
            }
        }
    )


# ============================================================
# CANCEL APPOINTMENT
# ============================================================

@login_required
@require_POST
def cancel_appointment_api(
    request,
    appointment_id
):

    try:

        appointment = (
            Appointment.objects
            .select_related(
                "doctor",
                "doctor__hospital"
            )
            .get(
                id=appointment_id,
                patient=request.user
            )
        )

    except Appointment.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "Appointment not found."
            },
            status=404
        )

    if appointment.status not in [
        "Pending",
        "Confirmed"
    ]:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "This appointment cannot be cancelled "
                    "because it is already "
                    f"{appointment.status.lower()}."
                )
            },
            status=400
        )

    appointment.status = "Cancelled"

    appointment.save(
        update_fields=[
            "status",
            "updated_at"
        ]
    )

    # --------------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------------

    UserActivity.objects.create(
        user=request.user,
        activity_type="appointment_cancelled",
        title="Appointment cancelled",
        description=(
            f"Appointment with "
            f"{appointment.doctor.name} was cancelled."
        ),
    )

    return JsonResponse(
        {
            "success": True,
            "message": (
                "Appointment cancelled successfully."
            ),
            "appointment": {
                "id": appointment.id,
                "doctor": appointment.doctor.name,
                "date": appointment.appointment_date.isoformat(),
                "time": appointment.appointment_time.strftime(
                    "%I:%M %p"
                ),
                "status": appointment.status
            }
        }
    )


# ============================================================
# APPOINTMENTS PAGE
# ============================================================

@login_required
def appointments_view(request):

    doctors = Doctor.objects.filter(
        is_active=True
    ).select_related(
        "hospital"
    ).order_by(
        "name"
    )

    return render(
        request,
        "assist/appointments.html",
        {
            "doctors": doctors,
        }
    )


# ============================================================
# MY APPOINTMENTS
# ============================================================

@login_required
def my_appointments_view(request):

    appointments = (
        Appointment.objects
        .filter(
            patient=request.user
        )
        .select_related(
            "doctor",
            "doctor__hospital"
        )
        .order_by(
            "-appointment_date",
            "-appointment_time"
        )
    )

    return render(
        request,
        "assist/my_appointments.html",
        {
            "appointments": appointments,
        }
    )


# ============================================================
# HEALTH RECORDS
# ============================================================

@login_required
def health_records_view(request):

    records = HealthRecord.objects.filter(
        user=request.user
    )

    return render(
        request,
        "assist/health_records.html",
        {
            "records": records,
        }
    )


# ============================================================
# ADD HEALTH RECORD
# ============================================================

@login_required
def health_record_add(request):

    if request.method == "POST":

        record = HealthRecord.objects.create(
            user=request.user,
            record_type=request.POST.get(
                "record_type"
            ),
            title=request.POST.get(
                "title"
            ),
            description=request.POST.get(
                "description",
                ""
            ),
            diagnosis=request.POST.get(
                "diagnosis",
                ""
            ),
            doctor_name=request.POST.get(
                "doctor_name",
                ""
            ),
            hospital_name=request.POST.get(
                "hospital_name",
                ""
            ),
            record_date=request.POST.get(
                "record_date"
            ),
            notes=request.POST.get(
                "notes",
                ""
            ),
            attachment=request.FILES.get(
                "attachment"
            ),
        )

        UserActivity.objects.create(
            user=request.user,
            activity_type="health_record_added",
            title="Health record added",
            description=(
                f"Added health record: "
                f"{record.title}"
            ),
            health_record=record,
        )

        return redirect(
            "health_records"
        )

    return redirect(
        "health_records"
    )


# ============================================================
# EDIT HEALTH RECORD
# ============================================================

@login_required
def health_record_edit(
    request,
    record_id
):

    record = get_object_or_404(
        HealthRecord,
        id=record_id,
        user=request.user
    )

    if request.method == "POST":

        record.title = request.POST.get(
            "title"
        )

        record.record_type = request.POST.get(
            "record_type"
        )

        record.record_date = request.POST.get(
            "record_date"
        )

        record.doctor_name = request.POST.get(
            "doctor_name",
            ""
        )

        record.hospital_name = request.POST.get(
            "hospital_name",
            ""
        )

        record.diagnosis = request.POST.get(
            "diagnosis",
            ""
        )

        record.description = request.POST.get(
            "description",
            ""
        )

        record.notes = request.POST.get(
            "notes",
            ""
        )

        new_attachment = request.FILES.get(
            "attachment"
        )

        if new_attachment:

            record.attachment = new_attachment

        record.save()

        UserActivity.objects.create(
            user=request.user,
            activity_type="health_record_updated",
            title="Health record updated",
            description=(
                f"Updated health record: "
                f"{record.title}"
            ),
            health_record=record,
        )

        return redirect(
            "health_records"
        )

    return redirect(
        "health_records"
    )


# ============================================================
# DELETE HEALTH RECORD
# ============================================================

@login_required
def health_record_delete(
    request,
    record_id
):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Invalid request method."
                )
            },
            status=405
        )

    record = get_object_or_404(
        HealthRecord,
        id=record_id,
        user=request.user
    )

    record_title = record.title

    UserActivity.objects.create(
        user=request.user,
        activity_type="health_record_deleted",
        title="Health record deleted",
        description=(
            f"Deleted health record: "
            f"{record_title}"
        ),
        health_record=record,
    )

    if record.attachment:

        record.attachment.delete(
            save=False
        )

    record.delete()

    return JsonResponse(
        {
            "success": True,
            "message": (
                "Health record deleted successfully."
            )
        }
    )


# ============================================================
# USER ACTIVITY
# ============================================================

@login_required
def user_activity_view(request):

    activities = UserActivity.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )

    health_count = UserActivity.objects.filter(
        user=request.user,
        activity_type__in=[
            "health_record_added",
            "health_record_updated",
            "health_record_deleted",
            "vitals_added",
            "vitals_updated",
            "vitals_deleted",
        ]
    ).count()

    medicine_count = UserActivity.objects.filter(
        user=request.user,
        activity_type__in=[
            "medicine_added",
            "medicine_updated",
            "medicine_deleted",
        ]
    ).count()

    appointment_count = UserActivity.objects.filter(
        user=request.user,
        activity_type__in=[
            "appointment_booked",
            "appointment_cancelled",
        ]
    ).count()

    return render(
        request,
        "assist/user_activity.html",
        {
            "activities": activities,
            "health_count": health_count,
            "medicine_count": medicine_count,
            "appointment_count": appointment_count,
        }
    )


# ============================================================
# MEDICAL DOCUMENT ASSESSMENT API
# ============================================================

@login_required
def medical_document_assessment_api(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Only POST requests are allowed."
                ),
            },
            status=405,
        )

    uploaded_file = request.FILES.get(
        "document"
    )

    if not uploaded_file:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please upload a medical document."
                ),
            },
            status=400,
        )

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    file_name = uploaded_file.name.lower()

    if not any(
        file_name.endswith(extension)
        for extension in allowed_extensions
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unsupported document type. "
                    "Supported formats: PDF, DOCX, TXT."
                ),
            },
            status=400,
        )

    try:

        import tempfile
        from pathlib import Path

        extension = Path(
            uploaded_file.name
        ).suffix.lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temporary_file:

            for chunk in uploaded_file.chunks():

                temporary_file.write(
                    chunk
                )

            temporary_path = (
                temporary_file.name
            )

        try:

            text = extract_medical_document_text(
                temporary_path
            )

            medical_info = extract_medical_information(
                text
            )

            assessment = generate_health_assessment(
                medical_info
            )

        finally:

            Path(
                temporary_path
            ).unlink(
                missing_ok=True
            )

        return JsonResponse(
            {
                "success": True,
                "medical_information": medical_info,
                "assessment": assessment,
            }
        )

    except ValueError as error:

        return JsonResponse(
            {
                "success": False,
                "message": str(error),
            },
            status=400,
        )

    except Exception as error:

        print(
            "MEDICAL DOCUMENT AI ERROR:",
            error
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to process the "
                    "medical document."
                ),
            },
            status=500,
        )


# ============================================================
# MEDICAL DOCUMENT ASSESSMENT PAGE
# ============================================================

@login_required
def medical_document_assessment_view(request):

    return render(
        request,
        "assist/medical_document_ai.html"
    )