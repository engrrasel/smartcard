from django import forms
from django.contrib.auth import get_user_model
from app_accounts.models import UserProfile

User = get_user_model()

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ "email"]

class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "bio", "profile_picture"]
