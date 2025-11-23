# Updated forms.py according to new CustomUser + parent_user system

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

# --------------------------------------------------
# 🟢 Signup Form (Root account only)
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


# --------------------------------------------------
# 🟢 Child Profile Create Form (Premium/Unlimited users)
# --------------------------------------------------
class ChildProfileCreateForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force enable fields
        self.fields['email'].disabled = False
        self.fields['password1'].disabled = False
        self.fields['password2'].disabled = False

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password1",
            "password2",
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


# --------------------------------------------------
# 🟢 Profile Setup (first time or create mode)
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
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }


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
        }
