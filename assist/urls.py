from django.urls import path

from . import views


urlpatterns = [

    # =========================================================
    # HOME / AUTHENTICATION
    # =========================================================

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),


    # =========================================================
    # FACE ID
    # =========================================================

    path(
        "face/register/",
        views.face_register,
        name="face_register"
    ),

    path(
        "face/detect/",
        views.face_detect_api,
        name="face_detect_api"
    ),

    path(
        "face/save/",
        views.face_save_api,
        name="face_save_api"
    ),

    path(
        "login/face/",
        views.face_login_api,
        name="face_login_api"
    ),


    # =========================================================
    # PROFILE
    # =========================================================

    path(
        "health-profile/",
        views.health_profile,
        name="health_profile"
    ),


    # =========================================================
    # MEDICINES
    # =========================================================

    path(
        "medicine/add/",
        views.medicine_add,
        name="medicine_add"
    ),

    path(
        "medicines/",
        views.medicine_list,
        name="medicine_list"
    ),

    path(
        "medicine/<int:medicine_id>/edit/",
        views.medicine_edit,
        name="medicine_edit"
    ),

    path(
        "medicine/<int:medicine_id>/delete/",
        views.medicine_delete,
        name="medicine_delete"
    ),

    path(
        "medicine/<int:medicine_id>/toggle-status/",
        views.medicine_toggle_status,
        name="medicine_toggle_status"
    ),

    path(
        "medicine/alarm-check/",
        views.medicine_alarm_check,
        name="medicine_alarm_check"
    ),

    path(
        "medicine/<int:medicine_id>/log-intake/",
        views.log_medicine_intake_api,
        name="log_medicine_intake_api"
    ),


    # =========================================================
    # AI HEALTH ASSISTANT
    # =========================================================

    path(
        "assistant/",
        views.ai_assistant,
        name="ai_assistant"
    ),

    path(
        "assistant/chat/",
        views.ai_chat_api,
        name="ai_chat_api"
    ),

    path(
        "assistant/clear/",
        views.ai_clear_chat,
        name="ai_clear_chat"
    ),


    # =========================================================
    # HEALTH VITALS
    # =========================================================

    path(
        "vitals/log/",
        views.log_vitals_api,
        name="log_vitals_api"
    ),

    path(
        "health-vitals/",
        views.health_vitals_view,
        name="health_vitals"
    ),

    path(
        "health-vitals/<int:vitals_id>/edit/",
        views.health_vitals_edit,
        name="health_vitals_edit"
    ),

    path(
        "health-vitals/<int:vitals_id>/delete/",
        views.health_vitals_delete,
        name="health_vitals_delete"
    ),


    # =========================================================
    # APPOINTMENTS
    # =========================================================

    path(
        "appointments/available-slots/",
        views.doctor_available_slots_api,
        name="doctor_available_slots_api"
    ),

    path(
        "appointments/book/",
        views.book_appointment_api,
        name="book_appointment_api"
    ),

    path(
        "appointments/",
        views.appointments_view,
        name="appointments_view"
    ),

    path(
        "my-appointments/",
        views.my_appointments_view,
        name="my_appointments_view"
    ),

    path(
        "appointments/<int:appointment_id>/cancel/",
        views.cancel_appointment_api,
        name="cancel_appointment_api"
    ),


    # =========================================================
    # HEALTH RECORDS
    # =========================================================

    path(
        "health-records/",
        views.health_records_view,
        name="health_records"
    ),

    path(
        "health-records/add/",
        views.health_record_add,
        name="health_record_add"
    ),

    path(
        "health-records/<int:record_id>/edit/",
        views.health_record_edit,
        name="health_record_edit"
    ),

    path(
        "health-records/<int:record_id>/delete/",
        views.health_record_delete,
        name="health_record_delete"
    ),


    # =========================================================
    # USER ACTIVITY
    # =========================================================

    path(
        "activity/",
        views.user_activity_view,
        name="user_activity"
    ),


    # =========================================================
    # MEDICAL DOCUMENT AI
    # =========================================================

    path(
        "medical-document-ai/",
        views.medical_document_assessment_view,
        name="medical_document_assessment_view"
    ),

    path(
        "api/medical-document-assessment/",
        views.medical_document_assessment_api,
        name="medical_document_assessment_api"
    ),


    # =========================================================
    # BLOOD PRESSURE AI ASSESSMENT
    # =========================================================

    path(
        "api/bp-assessment/",
        views.bp_assessment_api,
        name="bp_assessment_api"
    ),

]