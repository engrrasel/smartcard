from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# --------------------------------------------------
# 🟢 User Settings (Email update etc.)
# --------------------------------------------------
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Update email"
            })
        }


# --------------------------------------------------
# 🟢 Profile Settings (Child profile or parent profile fields)
# --------------------------------------------------
class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["phone", "bio", "profile_picture"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"})
        }
