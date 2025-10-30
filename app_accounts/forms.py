from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile


# ✅ Signup Form
class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']


# ✅ Profile Form (for profile editing)
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )

    # ✅ Username এখন ফর্মে দৃশ্যমান থাকবে (readonly নয়, একবার সেট না থাকলে এডিট করা যাবে)
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique username'})
    )

    class Meta:
        model = UserProfile
        exclude = ['user']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short bio'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Facebook profile'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn profile'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Instagram profile'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Website'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Show current email of the user
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

        # ✅ যদি username আগে থেকেই থাকে তাহলে তা readonly করে দিচ্ছি
        if self.instance and self.instance.username:
            self.fields['username'].disabled = True
            self.fields['username'].help_text = "Username already set and cannot be changed again."
        else:
            self.fields['username'].help_text = "Choose a unique username (only once)."
