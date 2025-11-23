from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q

import qrcode
import base64
import urllib.parse
from io import BytesIO

from .forms import SignupForm, ChildProfileCreateForm, ProfileUpdateForm

User = get_user_model()


# ───────────────────────────────────────────────
# ✅ Signup
# ───────────────────────────────────────────────
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
            messages.success(request, "Account created & logged in!")
            return redirect("app_accounts:dashboard")

        # Live mode – email activation
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse("app_accounts:activate_account", args=[uid, token])
        )

        send_mail(
            "Activate your SmartCard account",
            f"Click to activate:\n{activation_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        messages.success(request, "Check your email to activate your account.")
        return redirect("app_accounts:email_sent")

    return render(request, "accounts/signup.html", {"form": form})


# ───────────────────────────────────────────────
# ✅ Email Activation
# ───────────────────────────────────────────────
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
        messages.success(request, "Email verified!")
        return redirect("app_accounts:dashboard")

    return render(request, "accounts/activation_invalid.html")


# ───────────────────────────────────────────────
# ✅ Dashboard
# ───────────────────────────────────────────────
@login_required
def dashboard(request):
    user = request.user

    profiles = User.objects.filter(
        Q(pk=user.pk) | Q(parent_user=user)
    ).order_by("-updated_at")

    context = {
        "user": user,   # ← সবচেয়ে গুরুত্বপূর্ণ লাইন
        "profiles": profiles,
        "total_profiles": profiles.count(),
        "daily_views": sum(p.daily_views for p in profiles),
        "monthly_views": sum(p.monthly_views for p in profiles),
        "yearly_views": sum(p.yearly_views for p in profiles),
    }
    return render(request, "accounts/dashboard.html", context)


# ───────────────────────────────────────────────
# ✅ Profile & Card List
# ───────────────────────────────────────────────
@login_required
def profile_and_card(request):
    user = request.user
    profiles = User.objects.filter(
        Q(pk=user.pk) | Q(parent_user=user)
    ).order_by("-updated_at")

    context = {
        "profiles": profiles,
    }
    return render(request, "accounts/profile_&_card.html", context)


# ───────────────────────────────────────────────
# ✅ Create Child Profile (Email + Password OK)
# ───────────────────────────────────────────────
@login_required
def create_profile(request):
    user = request.user

    if not user.can_create_profile():
        messages.error(request, "You reached your profile limit.")
        return redirect("app_accounts:dashboard")

    if request.method == "POST":
        form = ChildProfileCreateForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent_user = user
            child.is_active = True
            child.save()

            messages.success(request, "Profile created successfully!")
            return redirect("app_accounts:profile_and_card")
    else:
        form = ChildProfileCreateForm()

    return render(request, "accounts/profile_create.html", {"form": form})


# ───────────────────────────────────────────────
# ✅ Edit Profile
# ───────────────────────────────────────────────
@login_required
def edit_profile(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated!")
        return redirect("app_accounts:profile_and_card")

    return render(request, "accounts/edit_profile.html", {"form": form, "profile": profile})


# ───────────────────────────────────────────────
# ✅ Remove Profile Picture
# ───────────────────────────────────────────────
@login_required
def remove_profile_picture(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    if profile.profile_picture:
        profile.profile_picture.delete(save=True)

    messages.success(request, "Profile picture removed.")
    return redirect("app_accounts:edit_profile", pk=pk)


# ───────────────────────────────────────────────
# ✅ Public Profile
# ───────────────────────────────────────────────
def public_profile(request, username):
    profile = get_object_or_404(User, username=username, is_active=True)

    if not profile.is_public:
        return render(request, "accounts/profile_not_found.html", status=404)

    today = timezone.now().date()

    if profile.last_viewed != today:
        profile.daily_views = 1
    else:
        profile.daily_views += 1

    profile.monthly_views += 1
    profile.yearly_views += 1
    profile.last_viewed = today
    profile.save()

    url = request.build_absolute_uri(profile.get_absolute_url())

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "accounts/public_profile.html", {
        "profile": profile,
        "qr_code_data": qr_data,
    })


# ───────────────────────────────────────────────
# ✅ Delete Profile
# ───────────────────────────────────────────────
@login_required
def delete_profile(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    profile.delete()
    messages.success(request, "Profile deleted.")
    return redirect("app_accounts:profile_and_card")


# ───────────────────────────────────────────────
# ✅ Download QR
# ───────────────────────────────────────────────
@login_required
def download_qr(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    url = request.build_absolute_uri(profile.get_absolute_url())

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="{profile.username}.png"'
    return response


# ───────────────────────────────────────────────
# ✅ Profile Analytics Dashboard
# ───────────────────────────────────────────────
@login_required
def profile_and_card_dashboard(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    return render(request, "accounts/profile_and_card_dashboard.html", {
        "profile": profile,
    })


# ───────────────────────────────────────────────
# ✅ Search Profiles
# ───────────────────────────────────────────────
@login_required
def profile_search(request):
    query = request.GET.get("q", "").strip()
    user = request.user

    profiles = User.objects.filter(
        Q(pk=user.pk) | Q(parent_user=user)
    )

    if query:
        profiles = profiles.filter(full_name__icontains=query)

    return render(request, "dashboard/profile_search.html", {
        "results": profiles,
        "query": query
    })


# ───────────────────────────────────────────────
# ✅ Toggle Public View
# ───────────────────────────────────────────────
@login_required
@require_POST
def toggle_public_view(request, profile_id):
    try:
        profile = User.objects.get(id=profile_id)

        if profile != request.user and profile.parent_user != request.user:
            return JsonResponse({"status": "error", "message": "Forbidden"}, status=403)

        profile.is_public = not profile.is_public
        profile.save()
        return JsonResponse({"status": "success", "is_public": profile.is_public})

    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)


# ───────────────────────────────────────────────
# Static Pages
# ───────────────────────────────────────────────
def contacts(request):
    return render(request, "dashboard/contacts.html")

def subscription(request):
    return render(request, "dashboard/subscription.html")



# -----------------------------------------
# 🟢 Download Contact vCard (public)
# -----------------------------------------
def download_contact_vcard(request, username):
    profile = get_object_or_404(User, username=username)

    full_name = profile.full_name or ""
    phone = profile.phone or ""
    email = profile.email or ""
    org = profile.company_name or ""
    job = profile.job_title or ""
    website = profile.website or ""

    # Split name
    parts = full_name.split(" ", 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""

    # Photo
    photo_line = ""
    if profile.profile_picture:
        try:
            with open(profile.profile_picture.path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                photo_line = f"PHOTO;ENCODING=b;TYPE=JPEG:{encoded}"
        except:
            pass

    vcard = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{last};{first};;;",
        f"FN:{full_name}",
    ]

    if org:
        vcard.append(f"ORG:{org}")
    if job:
        vcard.append(f"TITLE:{job}")
    if email:
        vcard.append(f"EMAIL;TYPE=INTERNET:{email}")
    if phone:
        vcard.append(f"TEL;TYPE=CELL:{phone}")
    if website:
        vcard.append(f"URL:{website}")
    if photo_line:
        vcard.append(photo_line)

    vcard.append("END:VCARD")

    text = "\r\n".join(vcard)

    filename = urllib.parse.quote(f"{profile.username}.vcf")

    response = HttpResponse(text, content_type="text/vcard; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
