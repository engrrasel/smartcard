from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, ProfileForm
from .models import CustomUser, UserProfile


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            activation_link = request.build_absolute_uri(
                reverse('activate_account', args=[uid, token])
            )

            send_mail(
                "Activate your SmartCard Account",
                f"Click the link to activate: {activation_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )

            messages.success(request, "Check your email to verify your account.")
            return redirect('email_sent')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'accounts/activation_invalid.html')


def email_sent(request):
    return render(request, 'accounts/email_sent.html')


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('edit_profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {"form": form})


@login_required
def remove_profile_picture(request):
    profile = request.user.userprofile
    if profile.profile_picture:
        profile.profile_picture.delete()
        profile.profile_picture = None
        profile.save()
        messages.success(request, "Profile picture removed successfully!")
    return redirect('edit_profile')
