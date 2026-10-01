from django import forms
from django.contrib.auth.models import User
from .models import Profile, MedicineReminder,HealthVitals


class RegistrationForm(forms.ModelForm):

    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your phone number",
                "class": "form-input",
                "type": "tel"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "form-input"
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password",
                "class": "form-input"
            }
        )
    )

    class Meta:
        model = User
        fields = ["username", "email"]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Enter your username",
                    "class": "form-input"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter your email",
                    "class": "form-input"
                }
            ),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already registered."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")

        phone = phone.replace(" ", "").replace("-", "")

        if not phone.isdigit():
            raise forms.ValidationError(
                "Please enter a valid phone number."
            )

        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError(
                "Phone number must contain 10 to 15 digits."
            )

        return phone

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error(
                    "confirm_password",
                    "Passwords do not match."
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:
            user.save()

        return user


# ================= PROFILE FORM =================

from .models import Profile


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            "phone_number",
            "profile_picture",
            "date_of_birth",
            "gender",
            "height",
            "weight",
            "blood_group",
        ]

        widgets = {

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter your phone number",
                    "type": "tel",
                }
            ),

          "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-input",
                    "accept": "image/*",
             }
             ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-input",
                    "type": "date",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),

            "height": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Height in cm",
                    "step": "0.1",
                    "min": "1",
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Weight in kg",
                    "step": "0.1",
                    "min": "1",
                }
            ),

            "blood_group": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Example: O+",
                }
            ),
        }


class MedicineReminderForm(forms.ModelForm):

    class Meta:
        model = MedicineReminder

        fields = [
            "medicine_name",
            "dosage",
            "frequency",
            "reminder_time",
            "start_date",
            "end_date",
            "email_reminder",
            "notes",
        ]

        widgets = {

            "medicine_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter medicine name",
                }
            ),

            "dosage": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Example: 500 mg",
                }
            ),

            "frequency": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),

            "reminder_time": forms.TimeInput(
                attrs={
                    "class": "form-input",
                    "type": "time",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-input",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-input",
                    "type": "date",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "Additional notes...",
                    "rows": 4,
                }
            ),

            "email_reminder": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),
        }

class HealthVitalsForm(forms.ModelForm):

    class Meta:
        model = HealthVitals

        fields = [
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "heart_rate",
            "blood_sugar",
            "weight",
            "notes",
        ]

        widgets = {
            "blood_pressure_systolic": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 120",
                    "min": "1",
                    "max": "300",
                }
            ),

            "blood_pressure_diastolic": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 80",
                    "min": "1",
                    "max": "200",
                }
            ),

            "heart_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 72",
                    "min": "1",
                    "max": "250",
                }
            ),

            "blood_sugar": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 100",
                    "step": "0.1",
                    "min": "1",
                    "max": "1000",
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 70",
                    "step": "0.1",
                    "min": "1",
                    "max": "500",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Add any notes about this reading...",
                    "rows": 4,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        systolic = cleaned_data.get(
            "blood_pressure_systolic"
        )

        diastolic = cleaned_data.get(
            "blood_pressure_diastolic"
        )

        if systolic is not None and diastolic is not None:

            if systolic <= diastolic:
                raise forms.ValidationError(
                    "Systolic blood pressure must be greater than diastolic pressure."
                )

        return cleaned_data