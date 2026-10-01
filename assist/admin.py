from django.contrib import admin

from .models import Hospital, Doctor, DoctorAvailability, Appointment



@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "city",
        "hospital_type",
        "emergency_available",
        "is_active",
    )

    list_filter = (
        "hospital_type",
        "emergency_available",
        "is_active",
        "city",
    )

    search_fields = (
        "name",
        "city",
        "phone",
        "email",
    )

    ordering = (
        "name",
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "specialization",
        "hospital",
        "location",
        "consultation_fee",
        "is_active",
    )

    list_filter = (
        "specialization",
        "hospital",
        "is_active",
    )

    search_fields = (
        "name",
        "specialization",
        "hospital__name",
        "location",
        "email",
    )

    ordering = (
        "name",
    )
@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):

    list_display = (
        "doctor",
        "day_of_week",
        "start_time",
        "end_time",
        "slot_duration",
        "is_available",
    )

    list_filter = (
        "day_of_week",
        "is_available",
        "doctor",
    )

    search_fields = (
        "doctor__name",
        "doctor__specialization",
    )

    ordering = (
        "doctor",
        "day_of_week",
        "start_time",
    )
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "patient",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "appointment_date",
        "doctor",
    )

    search_fields = (
        "patient__username",
        "patient__email",
        "doctor__name",
        "doctor__specialization",
    )

    ordering = (
        "-appointment_date",
        "appointment_time",
    )