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
from django.utils.text import slugify
from io import BytesIO
import base64
import qrcode

from .forms import SignupForm, ProfileUpdateForm, ProfileForm
from .models import UserProfile

User = get_user_model()


# -----------------------------
# 🟩 Helper Function
# -----------------------------
def get_or_create_profile(user):
    """
    Return user's latest profile or create one.
    - If multiple exist, keep only the latest.
    - Ensures unique username always.
    """
    profiles = UserProfile.objects.filter(user=user).order_by("-id")

    # যদি একাধিক প্রোফাইল থাকে, শুধু সর্বশেষটা রাখো
    if profiles.count() > 1:
        main_profile = profiles.first()
        profiles.exclude(id=main_profile.id).delete()
    elif profiles.exists():
        main_profile = profiles.first()
    else:
        main_profile = UserProfile.objects.create(user=user)

    # ✅ যদি username না থাকে, সেট করো
    if not main_profile.username:
        base = slugify(main_profile.full_name or user.email.split("@")[0])
        username = base
        count = 1
        while UserProfile.objects.filter(username=username).exists():
            username = f"{base}_{count}"
            count += 1
        main_profile.username = username
        main_profile.save()

    return main_profile


# -----------------------------
# 🟢 Signup (Email Verification Skip in DEBUG Mode)
# -----------------------------
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("app_account:dashboard")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        # ✅ Test Mode (DEBUG=True): Skip verification
        if settings.DEBUG:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "✅ Test Mode: Account created and logged in.")
            return redirect("app_account:dashboard")

        # 🚀 Production Mode: Send activation email
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse("app_account:activate_account", args=[uid, token])
        )

        try:
            send_mail(
                "Activate your SmartCard account",
                f"Click the link to verify your email:\n\n{activation_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            messages.success(
                request,
                "✅ Account created! Please check your email to verify your account.",
            )
        except Exception as e:
            messages.error(request, f"⚠️ Failed to send verification email: {e}")

        return redirect("app_account:email_sent")

    return render(request, "accounts/signup.html", {"form": form})


# -----------------------------
# 🟢 Email Activation
# -----------------------------
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
        messages.success(request, "🎉 Email verified successfully!")
        return redirect("app_account:dashboard")

    return render(request, "accounts/activation_invalid.html")


# -----------------------------
# 🟢 Dashboard
# -----------------------------
@login_required
def dashboard(request):
    profiles = UserProfile.objects.filter(user=request.user)
    main_profile = profiles.order_by("-updated_at").first()

    public_url = (
        request.build_absolute_uri(
            reverse("app_account:public_profile", args=[main_profile.username])
        )
        if main_profile and main_profile.username
        else None
    )

    context = {
        "profiles": profiles,
        "main_profile": main_profile,
        "public_url": public_url,
    }
    return render(request, "accounts/dashboard.html", context)


# -----------------------------
# 🟢 Create Profile (Respect Account Type Limit)
# -----------------------------
@login_required
def create_profile(request):
    user = request.user

    # ✅ Check account type limits
    if hasattr(user, "can_create_profile") and not user.can_create_profile():
        messages.error(
            request, "⚠️ You’ve reached your profile creation limit. Upgrade your plan!"
        )
        return redirect("app_account:dashboard")

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "✅ New profile created successfully!")
            return redirect("app_account:dashboard")
    else:
        form = ProfileForm()

    return render(request, "accounts/profile_create.html", {"form": form})


# -----------------------------
# 🟢 Edit Profile (Specific by PK)
# -----------------------------
@login_required
def edit_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        new_email = form.cleaned_data.get("email")

        # update user email if changed
        if new_email and new_email != request.user.email:
            request.user.email = new_email
            request.user.save()

        profile.save()
        messages.success(request, "✅ Profile updated successfully!")
        return redirect("app_account:edit_profile", pk=profile.pk)

    return render(request, "accounts/edit_profile.html", {"form": form})


# -----------------------------
# 🟢 Remove Profile Picture
# -----------------------------
@login_required
def remove_profile_picture(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    
    if profile.profile_picture:
        profile.profile_picture.delete(save=True)
        messages.success(request, "🗑 Profile picture removed successfully!")
    else:
        messages.warning(request, "⚠️ No profile picture to remove.")

    return redirect("app_account:edit_profile", pk=profile.pk)


# -----------------------------
# 🟢 Public Profile + QR + vCard
# -----------------------------
def public_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)
    profile_url = request.build_absolute_uri(
        reverse("app_account:public_profile", args=[username])
    )

    # ✅ Generate QR Code
    qr = qrcode.make(profile_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()

    # ✅ Generate vCard
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

    context = {
        "profile": profile,
        "qr_code_data": qr_code_data,
        "vcard_data": vcard_data,
    }
    return render(request, "accounts/public_profile.html", context)

"""@login_required
def delete_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    profile.delete()
    messages.success(request, "🗑️ Profile deleted successfully.")
    return redirect("dashboard:dashboard")
"""