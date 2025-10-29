from django.contrib.auth import login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, ProfileForm
from .models import UserProfile
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404


import qrcode
from io import BytesIO
import base64



def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = SignupForm(request.POST or None)

    if request.method == "POST":
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
                'Activate your SmartCard account',
                f'Click here to verify your email: {activation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )

            messages.success(
                request,
                "Thank you! Account created succesfully! Please verify your email before login."
            )
            return redirect('login')

        messages.error(request, "Please correct the errors below.")

    return render(request, 'accounts/signup.html', {'form': form})



User = get_user_model()


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

    # ✅ যদি username না থাকে, তৈরি করো
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

    # ✅ Public Profile URL তৈরি করো
    public_url = request.build_absolute_uri(
        reverse('public_profile', args=[profile.username])
    ) if profile.username else None

    context = {
        "profile": profile,
        "public_url": public_url,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.save()
        messages.success(request, "Profile updated successfully!")
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


def email_sent(request):
    return render(request, 'accounts/email_sent.html')




def public_profile(request, username):
    profile = get_object_or_404(UserProfile, username=username)

    # ✅ QR code generate
    qr_data = request.build_absolute_uri()  # Public profile URL
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()

    # ✅ vCard content
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