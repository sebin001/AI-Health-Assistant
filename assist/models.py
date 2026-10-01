from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone_number = models.CharField(
        max_length=15
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=20,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
            ("Prefer not to say", "Prefer not to say"),
        ],
        blank=True
    )

    height = models.FloatField(
        blank=True,
        null=True
    )

    weight = models.FloatField(
        blank=True,
        null=True
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def bmi(self):
        if self.height and self.weight and self.height > 0:
            height_in_meters = self.height / 100.0
            bmi_value = self.weight / (height_in_meters ** 2)
            return round(bmi_value, 1)
        return None

    @property
    def bmi_category(self):
        bmi_val = self.bmi
        if bmi_val is None:
            return "Not Available"
        if bmi_val < 18.5:
            return "Underweight"
        elif bmi_val < 25.0:
            return "Normal weight"
        elif bmi_val < 30.0:
            return "Overweight"
        else:
            return "Obese"

    def __str__(self):
        return self.user.username


class FaceEmbedding(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="face_embedding"
    )

    embedding = models.JSONField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Face ID - {self.user.username}"


class MedicineReminder(models.Model):

    FREQUENCY_CHOICES = [
        ("Once Daily", "Once Daily"),
        ("Twice Daily", "Twice Daily"),
        ("Three Times Daily", "Three Times Daily"),
        ("As Needed", "As Needed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medicine_reminders"
    )

    medicine_name = models.CharField(
        max_length=100
    )

    dosage = models.CharField(
        max_length=100
    )

    frequency = models.CharField(
        max_length=30,
        choices=FREQUENCY_CHOICES,
        default="Once Daily"
    )

    reminder_time = models.TimeField()

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True
    )

    email_reminder = models.BooleanField(
        default=True
    )

    notes = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    last_reminder_sent = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.medicine_name} - {self.user.username}"


class HealthVitals(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vitals"
    )

    blood_pressure_systolic = models.IntegerField(
        blank=True,
        null=True,
        help_text="Systolic (top number in mmHg)"
    )

    blood_pressure_diastolic = models.IntegerField(
        blank=True,
        null=True,
        help_text="Diastolic (bottom number in mmHg)"
    )

    heart_rate = models.IntegerField(
        blank=True,
        null=True,
        help_text="Beats per minute (BPM)"
    )

    blood_sugar = models.FloatField(
        blank=True,
        null=True,
        help_text="Blood glucose level (mg/dL)"
    )

    weight = models.FloatField(
        blank=True,
        null=True,
        help_text="Weight in kg"
    )

    notes = models.TextField(
        blank=True
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name_plural = "Health Vitals"

    def __str__(self):
        return f"Vitals for {self.user.username} on {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"


class MedicineLog(models.Model):

    STATUS_CHOICES = [
        ("TAKEN", "Taken"),
        ("SKIPPED", "Skipped"),
        ("SNOOZED", "Snoozed"),
    ]

    medicine = models.ForeignKey(
        MedicineReminder,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medicine_logs"
    )

    log_date = models.DateField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="TAKEN"
    )

    logged_at = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ["-logged_at"]
        unique_together = ("medicine", "log_date")

    def __str__(self):
        return f"{self.medicine.medicine_name} - {self.status} on {self.log_date}"


class AIChatMessage(models.Model):

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "AI Assistant"),
        ("system", "System"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_chat_messages"
    )

    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} [{self.role}]: {self.content[:30]}..."


class Hospital(models.Model):

    HOSPITAL_TYPES = [
        ("Government", "Government"),
        ("Private", "Private"),
        ("Clinic", "Clinic"),
        ("Specialty", "Specialty"),
    ]

    name = models.CharField(max_length=200)

    address = models.TextField()

    city = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    email = models.EmailField(blank=True)

    website = models.URLField(blank=True)

    hospital_type = models.CharField(
        max_length=20,
        choices=HOSPITAL_TYPES,
        default="Private"
    )

    emergency_available = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class Doctor(models.Model):

    name = models.CharField(max_length=200)

    specialization = models.CharField(
        max_length=150
    )

    qualification = models.CharField(
        max_length=200,
        blank=True
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="doctors"
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    location = models.CharField(
        max_length=200
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True
    )

    available_days = models.CharField(
        max_length=200,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} - {self.specialization}"

class DoctorAvailability(models.Model):

    DAYS_OF_WEEK = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="availability"
    )

    day_of_week = models.CharField(
        max_length=10,
        choices=DAYS_OF_WEEK
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    slot_duration = models.PositiveIntegerField(
        default=30,
        help_text="Appointment duration in minutes."
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.doctor.name} - "
            f"{self.day_of_week} "
            f"{self.start_time.strftime('%I:%M %p')} - "
            f"{self.end_time.strftime('%I:%M %p')}"
        )
class Appointment(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    patient_notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.patient.username} - "
            f"{self.doctor.name} - "
            f"{self.appointment_date} "
            f"{self.appointment_time.strftime('%I:%M %p')}"
        )

class HealthRecord(models.Model):

    RECORD_TYPE_CHOICES = [
        ("Diagnosis", "Diagnosis"),
        ("Prescription", "Prescription"),
        ("Lab Report", "Lab Report"),
        ("Medical Report", "Medical Report"),
        ("Hospital Visit", "Hospital Visit"),
        ("Surgery", "Surgery"),
        ("Vaccination", "Vaccination"),
        ("Other", "Other"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="health_records"
    )

    record_type = models.CharField(
        max_length=30,
        choices=RECORD_TYPE_CHOICES
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    diagnosis = models.CharField(
        max_length=300,
        blank=True
    )

    doctor_name = models.CharField(
        max_length=200,
        blank=True
    )

    hospital_name = models.CharField(
        max_length=200,
        blank=True
    )

    record_date = models.DateField()

    attachment = models.FileField(
        upload_to="health_records/",
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-record_date", "-created_at"]
        verbose_name = "Health Record"
        verbose_name_plural = "Health Records"

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.record_type} - "
            f"{self.title}"
        )

class UserActivity(models.Model):

    ACTIVITY_TYPE_CHOICES = [
        ("health_record_added", "Health Record Added"),
        ("health_record_updated", "Health Record Updated"),
        ("health_record_deleted", "Health Record Deleted"),
        ("medicine_added", "Medicine Added"),
        ("medicine_updated", "Medicine Updated"),
        ("medicine_deleted", "Medicine Deleted"),
        ("appointment_booked", "Appointment Booked"),
        ("appointment_cancelled", "Appointment Cancelled"),
        ("ai_chat", "AI Chat"),
        ("profile_updated", "Profile Updated"),
        ("vitals_added", "Health Vitals Added"),
        ("vitals_updated", "Health Vitals Updated"),
        ("vitals_deleted", "Health Vitals Deleted"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPE_CHOICES
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    health_record = models.ForeignKey(
        HealthRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.title}"
        )