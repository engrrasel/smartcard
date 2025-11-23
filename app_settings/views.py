from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .forms import UserSettingsForm, ProfileSettingsForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# --------------------------------------------------
# 🔵 Profile Settings (Parent or Child Profile)
# --------------------------------------------------
@login_required
def profile_settings(request):
    user = request.user

    # Option B: Profile = Current user itself
    profile = user  

    u_form = UserSettingsForm(request.POST or None, instance=user)
    p_form = ProfileSettingsForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST":
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile settings updated successfully!")
            return redirect("app_settings:profile_settings")

    return render(request, "settings/profile_settings.html", {
        "u_form": u_form,
        "p_form": p_form,
        "profile": profile
    })


# --------------------------------------------------
# 🔵 Password Change
# --------------------------------------------------
@login_required
def password_change(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated successfully!")
        return redirect("app_settings:change_password")

    return render(request, "settings/change_password.html", {"form": form})


# --------------------------------------------------
# 🔵 Email Update
# --------------------------------------------------
@login_required
def email_update(request):
    if request.method == "POST":
        new_email = request.POST.get("email")

        if not new_email:
            messages.error(request, "Email cannot be empty.")
            return redirect("app_settings:email_update")

        request.user.email = new_email
        request.user.save()

        messages.success(request, "Email updated successfully!")
        return redirect("app_settings:email_update")

    return render(request, "settings/email_update.html")


# --------------------------------------------------
# 🔵 Phone Update (Now updates CustomUser directly)
# --------------------------------------------------
@login_required
def phone_update(request):
    user = request.user

    if request.method == "POST":
        phone = request.POST.get("phone")

        if not phone:
            messages.error(request, "Phone number cannot be empty.")
            return redirect("app_settings:phone_update")

        user.phone = phone
        user.save()

        messages.success(request, "Phone number updated successfully!")
        return redirect("app_settings:phone_update")

    return render(request, "settings/phone_update.html", {"profile": user})


# --------------------------------------------------
# 🔵 Settings Home
# --------------------------------------------------
@login_required
def settings_home(request):
    return render(request, "settings/settings_home.html")
