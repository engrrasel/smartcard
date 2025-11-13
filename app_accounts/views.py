# ─────────────────────────────────────────────
# ✅ Django Core Imports
# ─────────────────────────────────────────────
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile as Profile
from django.views.decorators.http import require_POST



# ─────────────────────────────────────────────
# ✅ Third-Party / Utility Imports
# ─────────────────────────────────────────────
import base64
import qrcode
from io import BytesIO

# ─────────────────────────────────────────────
# ✅ Local App Imports
# ─────────────────────────────────────────────
from .forms import SignupForm, ProfileForm, ProfileUpdateForm
from .models import UserProfile

User = get_user_model()

# -----------------------------
# 🟩 Helper Function
# -----------------------------
def get_or_create_profile(user):
    profiles = UserProfile.objects.filter(user=user).order_by("-id")
    if profiles.count() > 1:
        main_profile = profiles.first()
        profiles.exclude(id=main_profile.id).delete()
    elif profiles.exists():
        main_profile = profiles.first()
    else:
        main_profile = UserProfile.objects.create(user=user)

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
# 🟢 Signup
# -----------------------------
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("app_accounts:dashboard")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)

        if settings.DEBUG:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "✅ Test Mode: Account created and logged in.")
            return redirect("app_accounts:dashboard")

        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse("app_accounts:activate_account", args=[uid, token])
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

        return redirect("app_accounts:email_sent")

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
        return redirect("app_accounts:dashboard")

    return render(request, "accounts/activation_invalid.html")


# -----------------------------
# 🟢 Dashboard
# -----------------------------
@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")


# -----------------------------
# 🟢 Profile & Card
# -----------------------------
@login_required
def profile_and_card(request):
    profiles = UserProfile.objects.filter(user=request.user)
    main_profile = profiles.order_by("-updated_at").first()

    public_url = (
        request.build_absolute_uri(
            reverse("app_accounts:public_profile", args=[main_profile.username])
        )
        if main_profile and main_profile.username
        else None
    )

    context = {
        "profiles": profiles,
        "main_profile": main_profile,
        "public_url": public_url,
    }
    return render(request, "accounts/profile_&_card.html", context)


# -----------------------------
# 🟢 Create Profile
# -----------------------------
@login_required
def create_profile(request):
    user = request.user

    if hasattr(user, "can_create_profile") and not user.can_create_profile():
        messages.error(
            request, "⚠️ You’ve reached your profile creation limit. Upgrade your plan!"
        )
        return redirect("app_accounts:dashboard")

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, "✅ New profile created successfully!")
            return redirect("app_accounts:dashboard")
    else:
        form = ProfileForm()

    return render(request, "accounts/profile_create.html", {"form": form})


# -----------------------------
# 🟢 Edit Profile
# -----------------------------
@login_required
def edit_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        new_email = form.cleaned_data.get("email")

        if new_email and new_email != request.user.email:
            request.user.email = new_email
            request.user.save()

        profile.save()
        messages.success(request, "✅ Profile updated successfully!")
        return redirect("app_accounts:edit_profile", pk=profile.pk)

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
    return redirect("app_accounts:edit_profile", pk=profile.pk)


# -----------------------------
# 🟢 Public Profile + QR + vCard
# -----------------------------
from datetime import date

from datetime import date
from django.utils import timezone

def public_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)

    # 🔒 যদি প্রোফাইল পাবলিক না হয়, তাহলে দেখাবে না
    if not profile.is_public:
        return render(request, "accounts/profile_not_found.html", status=404)

    today = timezone.now().date()

    if profile.last_viewed != today:
        profile.daily_views = 1
        profile.last_viewed = today
    else:
        profile.daily_views += 1

    if not profile.last_viewed or profile.last_viewed.month != today.month:
        profile.monthly_views = 0
    if not profile.last_viewed or profile.last_viewed.year != today.year:
        profile.yearly_views = 0

    profile.monthly_views += 1
    profile.yearly_views += 1
    profile.save()

    profile_url = request.build_absolute_uri(
        reverse("app_accounts:public_profile", args=[username])
    )

    qr = qrcode.make(profile_url)
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

    context = {
        "profile": profile,
        "qr_code_data": qr_code_data,
        "vcard_data": vcard_data,
    }
    return render(request, "accounts/public_profile.html", context)


@login_required
def delete_profile(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    profile.delete()
    messages.success(request, "Profile deleted successfully.")
    return redirect("app_accounts:dashboard")


@login_required
def download_qr(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    url = request.build_absolute_uri(profile.get_absolute_url())

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="{profile.username or profile.pk}.png"'
    return response


# -----------------------------
# 🟢 Others
# -----------------------------
@login_required
def dashboard(request):
    user = request.user
    profiles = UserProfile.objects.filter(user=user)

    # ✅ মোট প্রোফাইল সংখ্যা
    total_profiles = profiles.count()

    # ✅ সব প্রোফাইলের ভিউ কাউন্ট যোগফল
    daily_views = sum(profile.daily_views for profile in profiles)
    monthly_views = sum(profile.monthly_views for profile in profiles)
    yearly_views = sum(profile.yearly_views for profile in profiles)

    context = {
        "profiles": profiles,
        "total_profiles": total_profiles,
        "daily_views": daily_views,
        "monthly_views": monthly_views,
        "yearly_views": yearly_views,
    }
    return render(request, "accounts/dashboard.html", context)




def contacts(request):
    return render(request, "dashboard/contacts.html")

def subscription(request):
    return render(request, "dashboard/subscription.html")

def settings(request):
    return render(request, "dashboard/settings.html")


@login_required
def profile_and_card_dashboard(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    
    # Dummy data – পরবর্তীতে analytics যুক্ত করতে পারো
    daily_views = getattr(profile, "daily_views", 15)
    monthly_views = getattr(profile, "monthly_views", 220)
    yearly_views = getattr(profile, "yearly_views", 3520)
    
    context = {
        "profile": profile,
        "daily_views": daily_views,
        "monthly_views": monthly_views,
        "yearly_views": yearly_views,
    }
    return render(request, "accounts/profile_and_card_dashboard.html", context)



# -----------------------------
# 🟢 Search Profiles (Fixed ✅)
# -----------------------------
@login_required
def profile_search(request):
    query = request.GET.get("q", "").strip()
    results = UserProfile.objects.filter(user=request.user)

    if query:
        results = results.filter(full_name__icontains=query)

    context = {"results": results, "query": query}
    return render(request, "dashboard/profile_search.html", context)



@login_required
@require_POST
def toggle_public_view(request, profile_id):
    try:
        profile = UserProfile.objects.get(id=profile_id, user=request.user)
        profile.is_public = not profile.is_public
        profile.save(update_fields=["is_public"])
        return JsonResponse({
            "status": "success",
            "is_public": profile.is_public
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Profile not found"
        }, status=404)