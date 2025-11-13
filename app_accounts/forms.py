from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, UserProfile


# -----------------------------
# 🟢 Signup Form
# -----------------------------
class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "password1", "password2"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your email"
            }),
        }


# -----------------------------
# 🟢 Profile Creation Form
# -----------------------------
class ProfileForm(forms.ModelForm):
    """Used for creating a new UserProfile."""

    class Meta:
        model = UserProfile
        exclude = (
            "user",
            "daily_views",
            "monthly_views",
            "yearly_views",
            "last_viewed",
            "is_public",
        )
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "job_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Job title"}),
            "company_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company name"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short bio"}),
            "facebook": forms.URLInput(attrs={"class": "form-control", "placeholder": "Facebook profile URL"}),
            "linkedin": forms.URLInput(attrs={"class": "form-control", "placeholder": "LinkedIn profile URL"}),
            "instagram": forms.URLInput(attrs={"class": "form-control", "placeholder": "Instagram profile URL"}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "Website URL"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }


# -----------------------------
# 🟢 Profile Update Form
# -----------------------------
class ProfileUpdateForm(forms.ModelForm):
    """Used for editing existing UserProfile (with email + username support)."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"}),
    )

    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Unique username"}),
    )

    class Meta:
        model = UserProfile
        exclude = (
            "user",
            "daily_views",
            "monthly_views",
            "yearly_views",
            "last_viewed",
            "is_public",
        )
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "job_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Job title"}),
            "company_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company name"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short bio"}),
            "facebook": forms.URLInput(attrs={"class": "form-control", "placeholder": "Facebook profile URL"}),
            "linkedin": forms.URLInput(attrs={"class": "form-control", "placeholder": "LinkedIn profile URL"}),
            "instagram": forms.URLInput(attrs={"class": "form-control", "placeholder": "Instagram profile URL"}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "Website URL"}),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Pre-fill email field
        if self.instance and getattr(self.instance, "user", None):
            self.fields["email"].initial = self.instance.user.email

        # ✅ Username logic
        if self.instance and getattr(self.instance, "username", None):
            self.fields["username"].disabled = True
            self.fields["username"].help_text = "Username already set (cannot be changed)."
        else:
            self.fields["username"].help_text = "Choose a unique username (only once)."

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not username:
            return getattr(self.instance, "username", None)

        username = username.strip().lower()

        # ✅ Check if username already exists
        qs = UserProfile.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("❌ This username is already taken.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)

        # ✅ Update email in CustomUser
        new_email = self.cleaned_data.get("email")
        if new_email and getattr(profile, "user", None):
            user = profile.user
            if user.email != new_email:
                user.email = new_email
                if commit:
                    user.save()

        # ✅ Assign username if not already set
        username_input = self.cleaned_data.get("username")
        if username_input and not profile.username:
            profile.username = username_input

        if commit:
            profile.save()
        return profile
