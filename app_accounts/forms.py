from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re


# --------------------------------------------------
# 🟢 Root Signup Form
# --------------------------------------------------
class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "password1", "password2"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your email"
            })
        }


# ==================================================
# 🔥 SHARED USERNAME CLEANER (Function)
# ==================================================
def clean_username_auto(instance, username):
    """
    Remove special characters automatically.
    Allowed: a-z / A-Z / 0-9 / _ / -
    """

    # Remove not allowed characters
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', username or "")

    # If cleaned is empty → auto-generate
    if not cleaned:
        cleaned = f"user{instance.pk or ''}"

    # Prevent duplicates
    original = cleaned
    count = 1
    while CustomUser.objects.filter(username=cleaned).exclude(pk=instance.pk).exists():
        cleaned = f"{original}{count}"
        count += 1

    return cleaned


# --------------------------------------------------
# 🟢 Child Profile Create Form
# --------------------------------------------------
class ChildProfileCreateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "full_name",
            "job_title",
            "phone",
            "company_name",
            "bio",
            "profile_picture",
            "facebook",
            "linkedin",
            "instagram",
            "website",
        ]

        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose username"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "facebook": forms.URLInput(attrs={"class": "form-control"}),
            "linkedin": forms.URLInput(attrs={"class": "form-control"}),
            "instagram": forms.URLInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # ⭐ AUTO FIX USERNAME
    def clean_username(self):
        username = self.cleaned_data.get("username")
        return clean_username_auto(self.instance, username)


# --------------------------------------------------
# 🟢 Profile Setup Form
# --------------------------------------------------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "full_name",
            "job_title",
            "phone",
            "company_name",
            "bio",
            "profile_picture",
            "facebook",
            "linkedin",
            "instagram",
            "website",
            "username",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "facebook": forms.URLInput(attrs={"class": "form-control"}),
            "linkedin": forms.URLInput(attrs={"class": "form-control"}),
            "instagram": forms.URLInput(attrs={"class": "form-control"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return clean_username_auto(self.instance, username)


# --------------------------------------------------
# 🟢 Profile Update Form
# --------------------------------------------------
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "full_name",
            "job_title",
            "phone",
            "company_name",
            "bio",
            "facebook",
            "linkedin",
            "instagram",
            "website",
            "profile_picture",
            "username",
        ]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        return clean_username_auto(self.instance, username)
