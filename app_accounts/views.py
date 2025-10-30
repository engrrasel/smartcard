from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import SignupForm, ProfileUpdateForm
from .models import UserProfile
import qrcode
from io import BytesIO
import base64


User = get_user_model()


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        # ✅ DEBUG মোডে ইমেল ভেরিফিকেশন স্কিপ
        if settings.DEBUG:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "✅ Test Mode: Account created and logged in (email verification skipped).")
            return redirect('dashboard')

        # 🚨 Production এ ইমেল ভেরিফিকেশন পাঠাবে
        else:
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(
                reverse('activate_account', args=[uid, token])
            )
            send_mail(
                'Activate your SmartCard account',
                f'Click here to verify your email: {activation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            messages.success(request, "Account created! Please verify your email.")
            return redirect('login')

    return render(request, 'accounts/signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your email is verified. Welcome!")
        return redirect('dashboard')

    return render(request, "accounts/activation_invalid.html")


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # ✅ username generate if missing
    if not profile.username and profile.full_name:
        from django.utils.text import slugify
        base = slugify(profile.full_name.replace(" ", "_"))
        username = base
        count = 1
        while UserProfile.objects.filter(username=username).exists():
            username = f"{base}_{count}"
            count += 1
        profile.username = username
        profile.save()

    public_url = request.build_absolute_uri(
        reverse('public_profile', args=[profile.username])
    ) if profile.username else None

    context = {"profile": profile, "public_url": public_url}
    return render(request, 'accounts/dashboard.html', context)


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        new_email = form.cleaned_data.get('email')

        # ইমেইল আপডেট
        if new_email and new_email != request.user.email:
            request.user.email = new_email
            request.user.save()

        profile.save()
        messages.success(request, "✅ Profile updated successfully!")
        return redirect('edit_profile')

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


def public_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    qr_data = request.build_absolute_uri()
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()

    vcard_data = f"""BEGIN:VCARD
VERSION:3.0
N:{profile.full_name or ""}
TEL:{profile.phone or ""}
EMAIL:{profile.user.email or ""}
ORG:{profile.company_name or ""}
TITLE:{profile.job_title or ""}
URL:{profile.website or ""}
END:VCARD
"""

    return render(request, "accounts/public_profile.html", {
        "profile": profile,
        "qr_code_data": qr_code_data,
        "vcard_data": vcard_data,
    })
