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
from .models import CustomUser

import qrcode
import base64
import urllib.parse
from io import BytesIO

from .forms import SignupForm, ChildProfileCreateForm, ProfileUpdateForm

User = get_user_model()


# ───────────────────────────────────────────────
# SIGNUP
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
# EMAIL ACTIVATION
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
# DASHBOARD
# ───────────────────────────────────────────────
@login_required
def dashboard(request):
    user = request.user

    profiles = User.objects.filter(
        Q(pk=user.pk) | Q(parent_user=user)
    ).order_by("-updated_at")

    context = {
        "user": user,
        "profiles": profiles,
        "total_profiles": profiles.count(),
        "daily_views": sum(p.daily_views for p in profiles),
        "monthly_views": sum(p.monthly_views for p in profiles),
        "yearly_views": sum(p.yearly_views for p in profiles),
    }
    return render(request, "accounts/dashboard.html", context)


# ───────────────────────────────────────────────
# PROFILE LIST
# ───────────────────────────────────────────────
@login_required
def profile_and_card(request):
    user = request.user

    # MAIN CARD (parent_user = None)
    main_profile = user

    # CHILD CARDS (parent_user = user)
    child_profiles = User.objects.filter(parent_user=user).order_by("-updated_at")

    return render(request, "accounts/profile_&_card.html", {
        "main_profile": main_profile,
        "child_profiles": child_profiles,
    })

# ───────────────────────────────────────────────
# CREATE CHILD PROFILE
# ───────────────────────────────────────────────
@login_required
def create_profile(request):
    user = request.user

    # Profile limit check
    if not user.can_create_profile():
        messages.error(request, "You reached your profile limit.")
        return redirect("app_accounts:dashboard")

    if request.method == "POST":
        form = ChildProfileCreateForm(request.POST, request.FILES)

        if form.is_valid():
            child = form.save(commit=False)
            child.parent_user = user
            child.is_active = True

            # ⭐ Default password set
            default_password = "12345678"
            child.set_password(default_password)

            # ⭐ Username user না দিলে auto generate
            if not child.username or child.username == "":
                # Auto generate unique username
                base_username = child.email.split("@")[0]
                new_username = base_username
                counter = 1

                # check existing username
                from app_accounts.models import CustomUser
                while CustomUser.objects.filter(username=new_username).exists():
                    new_username = f"{base_username}{counter}"
                    counter += 1

                child.username = new_username

            child.save()

            messages.success(request, f"Profile created successfully!")

            return redirect("app_accounts:profile_and_card")

    else:
        form = ChildProfileCreateForm()

    return render(request, "accounts/profile_create.html", {"form": form})

# ───────────────────────────────────────────────
# EDIT PROFILE
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
# REMOVE PROFILE PICTURE
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
# PUBLIC PROFILE
# ───────────────────────────────────────────────
def public_profile(request, username):
    profile = get_object_or_404(User, username=username, is_active=True)

    # ❗ Deleted card handle
    if profile.username.startswith("deleted_"):
        return render(request, "accounts/profile_not_found.html", status=404)

    # ❗ Private profile handle
    if not profile.is_public:
        return render(request, "accounts/profile_not_found.html", status=404)

    # -----------------------------
    # ⭐ VIEW COUNT (ONLY PUBLIC PAGE)
    # -----------------------------
    today = timezone.now().date()

    # First visit today
    if profile.last_viewed != today:
        profile.daily_views = 1
    else:
        profile.daily_views += 1

    # Monthly & yearly counters always increase
    profile.monthly_views += 1
    profile.yearly_views += 1

    profile.last_viewed = today
    profile.save()
    # --------------------------------------------

    # -------- QR Code Generate ----------
    url = request.build_absolute_uri(profile.get_absolute_url())
    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode()
    # -------------------------------------

    return render(request, "accounts/public_profile.html", {
        "profile": profile,
        "qr_code_data": qr_data,
    })


# ───────────────────────────────────────────────
# DOWNLOAD QR
# ───────────────────────────────────────────────
@login_required
def download_qr(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    # ⭐ Permanent ID based QR Link
    url = request.build_absolute_uri(
        reverse("app_accounts:public_profile_by_id", args=[profile.public_id])
    )

    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename=\"{profile.username}.png\"'
    return response


# ───────────────────────────────────────────────
# PROFILE DASHBOARD
# ───────────────────────────────────────────────
@login_required
def profile_and_card_dashboard(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    return render(request, "accounts/profile_and_card_dashboard.html", {"profile": profile})


# ───────────────────────────────────────────────
# SEARCH PROFILE
# ───────────────────────────────────────────────
@login_required
def profile_search(request):
    query = request.GET.get("q", "").strip()
    user = request.user

    profiles = User.objects.filter(Q(pk=user.pk) | Q(parent_user=user))

    if query:
        profiles = profiles.filter(full_name__icontains=query)

    return render(request, "dashboard/profile_search.html", {
        "results": profiles,
        "query": query
    })


# ───────────────────────────────────────────────
# TOGGLE PUBLIC
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
# UNLINK CHILD PROFILE
# ───────────────────────────────────────────────
@login_required
def unlink_profile(request, pk):
    profile = get_object_or_404(User, pk=pk)

    if profile.parent_user != request.user:
        return HttpResponse("Forbidden", status=403)

    profile.parent_user = None
    profile.save(update_fields=["parent_user"])

    messages.success(request, "Child profile unlinked.")
    return redirect("app_accounts:profile_and_card")


# ───────────────────────────────────────────────
# DELETE MOTHER CARD (not user)
"""@login_required
def delete_card(request, pk):
    profile = get_object_or_404(User, pk=pk)

    # Only allow deleting own card (main or child)
    if request.user.pk != profile.pk:
        return HttpResponse("Forbidden", status=403)

    # reset profile data
    profile.full_name = None
    profile.job_title = None
    profile.phone = None
    profile.company_name = None
    profile.bio = None
    profile.facebook = None
    profile.linkedin = None
    profile.instagram = None
    profile.website = None

    # delete profile picture
    if profile.profile_picture:
        profile.profile_picture.delete(save=False)
        profile.profile_picture = None

    # hide public visibility
    profile.is_public = False

    # mark username as deleted
    import uuid
    profile.username = f"deleted_{uuid.uuid4().hex[:10]}"

    profile.save()

    messages.success(request, "Card deleted successfully.")
    return redirect("app_accounts:profile_and_card")
"""

@login_required
def download_contact_vcard(request, username):
    profile = get_object_or_404(User, username=username)

    vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{profile.full_name}
TEL:{profile.phone}
EMAIL:{profile.email}
ORG:{profile.company_name}
TITLE:{profile.job_title}
URL:{profile.website}
END:VCARD
""".strip()

    response = HttpResponse(vcard, content_type='text/vcard')
    response['Content-Disposition'] = f'attachment; filename="{profile.username}.vcf"'
    return response


def subscription(request):
    return render(request, "dashboard/subscription.html")




def public_profile_by_id(request, public_id):

    # Find the profile using permanent public ID
    profile = CustomUser.objects.filter(public_id=public_id, is_public=True).first()

    if profile is None:
        return render(request, "accounts/profile_not_found.html", status=404)

    # 🔥 Redirect browser to username-based URL
    return redirect("app_accounts:public_profile", username=profile.username)



@login_required
def profile_and_card_dashboard(request, pk):
    profile = get_object_or_404(User, pk=pk)

    # ❗ এখানে কোনো ভিউ কাউন্ট হবে না
    # ❗ এখানে public_profile() কখনো কল করবেন না
    # ❗ এখানে profile.get_absolute_url() ব্যবহার করবেন না

    context = {
        "profile": profile,
        "daily_views": profile.daily_views,
        "monthly_views": profile.monthly_views,
        "yearly_views": profile.yearly_views,
    }

    return render(request, "accounts/profile_and_card_dashboard.html", context)
