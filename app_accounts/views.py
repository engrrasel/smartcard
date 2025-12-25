# views.py (CLEAN + READY)
from datetime import timedelta
from io import BytesIO
from collections import defaultdict

import qrcode
import requests

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse

from .forms import ChildProfileCreateForm, ProfileUpdateForm, SignupForm
from .utils import get_client_ip, parse_user_agent

# Models
from app_accounts.models import CustomUser, ContactSaveLead, ClickEvent

User = get_user_model()


def _model_field_names(model_cls):
    """Return set of field names for a model class."""
    return {f.name for f in model_cls._meta.get_fields()}


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
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("app_accounts:dashboard")

        user.is_active = False
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(reverse("app_accounts:activate_account", args=[uid, token]))
        send_mail("Activate your SmartCard account", f"Click to activate:\n{activation_link}", settings.DEFAULT_FROM_EMAIL, [user.email])
        messages.success(request, "Check your email to activate your account.")
        return redirect("app_accounts:email_sent")

    return render(request, "accounts/signup.html", {"form": form})


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
@login_required
def dashboard(request):
    user = request.user
    profiles = User.objects.filter(Q(pk=user.pk) | Q(parent_user=user)).order_by("-updated_at")
    return render(request, "accounts/dashboard.html", {
        "user": user,
        "profiles": profiles,
        "total_profiles": profiles.count(),
        "daily_views": sum(p.daily_views for p in profiles),
        "monthly_views": sum(p.monthly_views for p in profiles),
        "yearly_views": sum(p.yearly_views for p in profiles),
    })


# ───────────────────────────────────────────────
@login_required
def profile_and_card(request):
    user = request.user
    return render(request, "accounts/profile_&_card.html", {
        "main_profile": user,
        "child_profiles": User.objects.filter(parent_user=user).order_by("-updated_at"),
    })


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
            child.set_password("12345678")
            if not child.username:
                base = child.email.split("@")[0]
                new_user = base
                counter = 1
                while CustomUser.objects.filter(username=new_user).exists():
                    new_user = f"{base}{counter}"
                    counter += 1
                child.username = new_user
            child.save()
            messages.success(request, "Profile created successfully!")
            return redirect("app_accounts:profile_and_card")

    return render(request, "accounts/profile_create.html", {"form": ChildProfileCreateForm()})


# ───────────────────────────────────────────────
@login_required
def edit_profile(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", 403)

    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated!")
        return redirect("app_accounts:profile_and_card")
    return render(request, "accounts/edit_profile.html", {"form": form, "profile": profile})


# ───────────────────────────────────────────────
@login_required
def remove_profile_picture(request, pk):
    profile = get_object_or_404(User, pk=pk)

    # Security: Only owner or parent user can remove DP
    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", 403)

    # If picture exists AND it is NOT default.png
    if profile.profile_picture and profile.profile_picture.name != "default.png":
        profile.profile_picture.delete(save=False)

    # Set fallback default image
    profile.profile_picture = "default.png"
    profile.save()

    messages.success(request, "Profile picture removed.")
    return redirect("app_accounts:edit_profile", pk=pk)


# ───────────────────────────────────────────────
# public profile only renders template — tracking is handled by track_visit()
def public_profile(request, username):
    profile = CustomUser.objects.filter(
        username=username,
        is_public=True
    ).first()

    if not profile:
        # ✅ প্রফাইল পাব্লিক না হলে এই টেমপ্লেট দেখাবে
        return render(
            request,
            "accounts/profile_not_found.html",
            status=404
        )

    return render(
        request,
        "accounts/public_profile.html",
        {"profile": profile}
    )

# ───────────────────────────────────────────────
@login_required
def download_qr(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", 403)
    qr = qrcode.make(request.build_absolute_uri(reverse("app_accounts:public_profile_by_id", args=[profile.public_id])))
    b = BytesIO()
    qr.save(b, "PNG")
    b.seek(0)
    res = HttpResponse(b, "image/png")
    res["Content-Disposition"] = f'attachment; filename="{profile.username}.png"'
    return res


# ───────────────────────────────────────────────
@login_required
def profile_and_card_dashboard(request, pk):
    """
    Main dashboard for a single profile.
    - loads last contact leads (location logs)
    - loads click events
    - builds a mapping (by device_ip or visitor id) of which buttons were clicked
    so the template can show per-visitor which buttons were clicked.
    """
    profile = get_object_or_404(CustomUser, pk=pk)
    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", 403)

    # Location leads (most recent first)
    base = ContactSaveLead.objects.filter(profile=profile).select_related("visitor").order_by("-timestamp")
    leads = base[:200]
    location_logs = base[:50]

    # Analytics
    total_views = base.count()
    gps_count = base.filter(latitude__isnull=False, longitude__isnull=False).count()
    ip_count = total_views - gps_count

    mobile = base.filter(user_agent__icontains="Mobile").count()
    tablet = base.filter(user_agent__icontains="Tablet").count()
    desktop = total_views - (mobile + tablet)

    today = timezone.now().date()
    labels, values = [], []
    for i in range(15):
        d = today - timedelta(days=(14 - i))
        labels.append(d.strftime("%d %b"))
        values.append(base.filter(timestamp__date=d).count())

    top_countries = base.values("country").annotate(c=Count("id")).order_by("-c")[:5]

    # Click events (all)
    click_events = ClickEvent.objects.filter(profile=profile).order_by("-timestamp")

    # Build mapping of device_ip -> list of clicked buttons (preserve order, unique)
    click_by_ip = defaultdict(list)
    for ce in click_events:
        key = ce.device_ip or "anon"
        btn = (ce.button_type or "").strip().lower()
        if btn and btn not in click_by_ip[key]:
            click_by_ip[key].append(btn)

    # Additionally build mapping for visitor user id if available from ContactSaveLead:
    # We'll prepare a map lead_key -> buttons for quick template use.
    lead_buttons_map = {}
    for lead in location_logs:
        # prefer visitor-based key if visitor exists, else device_ip
        if lead.visitor:
            # try to find clicks by device_ip first; also fallback to using visitor-specific lookup
            key = lead.device_ip or f"user:{lead.visitor.pk}"
        else:
            key = lead.device_ip or "anon"
        buttons = click_by_ip.get(lead.device_ip or "anon", [])
        # store a shallow copy
        lead_buttons_map[lead.id] = buttons

    return render(request, "accounts/profile_and_card_dashboard.html", {
        "profile": profile,
        "leads": leads,
        "location_logs": location_logs,
        "lead_buttons_map": lead_buttons_map,   # use this in template: lead_buttons_map[lead.id]
        "total_views": total_views,
        "gps_count": gps_count,
        "ip_count": ip_count,
        "mobile_count": mobile,
        "tablet_count": tablet,
        "desktop_count": desktop,
        "chart_labels": labels,
        "chart_values": values,
        "top_countries": top_countries,
        "click_events": click_events[:50],
        "click_stats": {
            "total": click_events.count(),
            "connect": click_events.filter(button_type="connect").count(),
            "save": click_events.filter(button_type="save").count(),
            "call": click_events.filter(button_type="call").count(),
        },
    })


# ───────────────────────────────────────────────
@login_required
def profile_search(request):
    query = request.GET.get("q", "").strip()
    profiles = User.objects.filter(Q(pk=request.user.pk) | Q(parent_user=request.user))
    if query:
        profiles = profiles.filter(full_name__icontains=query)
    return render(request, "dashboard/profile_search.html", {"results": profiles, "query": query})


# ───────────────────────────────────────────────
@login_required
@require_POST
def toggle_public_view(request, profile_id):
    profile = get_object_or_404(User, id=profile_id)

    if profile != request.user and profile.parent_user != request.user:
        return JsonResponse({"status": "error"}, status=403)

    import json
    body = json.loads(request.body)

    # 🔍 DEBUG LINE — এখানেই লিখবেন
    print("PUBLIC STATUS:", body.get("is_public"), type(body.get("is_public")))

    # FIXED LOGIC
    profile.is_public = True if body.get("is_public") is True else False
    profile.save(update_fields=["is_public"])

    return JsonResponse({
        "status": "success",
        "is_public": profile.is_public
    })

# ───────────────────────────────────────────────
@login_required
def unlink_profile(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if profile.parent_user != request.user:
        return HttpResponse("Forbidden", 403)
    profile.parent_user = None
    profile.save(update_fields=["parent_user"])
    messages.success(request, "Child profile unlinked.")
    return redirect("app_accounts:profile_and_card")


# ───────────────────────────────────────────────
def download_contact_vcard(request, username):
    profile = get_object_or_404(User, username=username)
    v = f"""BEGIN:VCARD
VERSION:3.0
FN:{profile.full_name}
TEL:{profile.phone}
EMAIL:{profile.email}
ORG:{profile.company_name}
TITLE:{profile.job_title}
URL:{profile.website}
END:VCARD"""
    r = HttpResponse(v, "text/vcard")
    r["Content-Disposition"] = f'attachment; filename="{profile.username}.vcf"'
    return r


def subscription(request):
    return render(request, "dashboard/subscription.html")


def public_profile_by_id(request, public_id):
    profile = CustomUser.objects.filter(public_id=public_id, is_public=True).first()
    if not profile:
        return render(request, "accounts/profile_not_found.html", status=404)
    return redirect("app_accounts:public_profile", username=profile.username)


# ───────────────────────────────────────────────
def ip_to_location(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2).json()
        return r.get("city"), r.get("country")
    except Exception:
        return None, None


# ───────────────────────────────────────────────
@require_POST
@csrf_exempt
def track_save_gps(request, username):
    profile = get_object_or_404(CustomUser, username=username)

    ip = get_client_ip(request) or request.META.get("REMOTE_ADDR", "")
    ua = request.META.get("HTTP_USER_AGENT", "")[:1000]

    raw_lat = request.POST.get("lat") or request.POST.get("latitude")
    raw_lon = request.POST.get("lon") or request.POST.get("longitude")

    try:
        lat = float(raw_lat) if raw_lat not in (None, "") else None
    except:
        lat = None
    try:
        lon = float(raw_lon) if raw_lon not in (None, "") else None
    except:
        lon = None

    is_gps = lat is not None and lon is not None
    device_type, browser, os_name = parse_user_agent(ua)
    allowed = _model_field_names(ContactSaveLead)

    data = {
        "profile": profile,
        "device_ip": ip,
        "user_agent": ua,
        "latitude": lat,
        "longitude": lon,
    }
    for k in ("country", "city", "thana", "post_office", "accuracy", "location_source"):
        v = request.POST.get(k)
        if v:
            data[k] = v
    lead_kwargs = {k: v for k, v in data.items() if k in allowed}
    lead = ContactSaveLead.objects.create(**lead_kwargs)
    redirect_url = reverse("app_accounts:public_profile", args=[username])
    return JsonResponse({
        "success": True,
        "url": redirect_url,
        "lead_id": lead.id,
        "gps_used": is_gps,
        "browser": browser,
        "device": device_type,
        "os": os_name,
    })


# ───────────────────────────────────────────────
@require_POST
@csrf_exempt
def click_track(request, username):
    """
    Save both:
     - a ContactSaveLead (so clicks also produce a short lead record)
     - a ClickEvent (for precise click analytics)
    Visitor is recorded only when a logged-in user views/clicks someone else's profile.
    """
    user = get_object_or_404(CustomUser, username=username)

    ip = get_client_ip(request) or request.META.get("REMOTE_ADDR", "")
    ua = request.META.get("HTTP_USER_AGENT", "")[:1000]

    action = (request.POST.get("action") or "").strip().lower()

    # Visitor detection: only when logged-in user != profile owner
    visitor = request.user if request.user.is_authenticated and request.user != user else None

    raw_lat = request.POST.get("lat") or request.POST.get("latitude")
    raw_lon = request.POST.get("lon") or request.POST.get("longitude")
    try:
        lat = float(raw_lat) if raw_lat not in (None, "") else None
    except:
        lat = None
    try:
        lon = float(raw_lon) if raw_lon not in (None, "") else None
    except:
        lon = None

    allowed = _model_field_names(ContactSaveLead)
    data = {
        "profile": user,
        "visitor": visitor,
        "device_ip": ip,
        "user_agent": ua,
        "latitude": lat,
        "longitude": lon,
        "action": action,
    }
    for k in ("country", "city", "thana", "post_office", "accuracy", "location_source"):
        v = request.POST.get(k)
        if v:
            data[k] = v
    lead_kwargs = {k: v for k, v in data.items() if k in allowed}
    ContactSaveLead.objects.create(**lead_kwargs)

    ClickEvent.objects.create(
        profile=user,
        button_type=action,
        device_ip=ip,
        user_agent=ua,
        latitude=lat,
        longitude=lon,
    )

    return JsonResponse({"saved": True, "action": action})


# ───────────────────────────────────────────────
@csrf_exempt
def track_visit(request, username):
    """
    Called from public_profile JS. Attempts to use GPS when provided, otherwise falls back to IP.
    Visitor recorded only when a logged-in user visits someone else's profile.
    """
    user = get_object_or_404(CustomUser, username=username)

    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    acc_raw = request.GET.get("accuracy")

    def convert_accuracy(meter):
        try:
            m = float(meter)
            return (
                98 if m <= 5 else
                92 if m <= 10 else
                85 if m <= 20 else
                70 if m <= 50 else
                55 if m <= 100 else
                35
            )
        except:
            return None

    country = city = thana = post_office = "Unknown"
    location_source = "IP"
    accuracy = convert_accuracy(acc_raw) or 50

    gps_allowed = bool(lat and lon and acc_raw)
    gps_accuracy_m = None
    if gps_allowed:
        try:
            gps_accuracy_m = float(acc_raw)
        except:
            gps_allowed = False

    if gps_allowed and gps_accuracy_m <= 350:
        location_source = "GPS"
    else:
        lat = None
        lon = None
        location_source = "IP"

    if location_source == "GPS":
        try:
            r = requests.get("https://nominatim.openstreetmap.org/reverse", params={
                "format": "json", "lat": lat, "lon": lon, "zoom": 18, "accept-language": "en", "addressdetails": 1
            }, headers={"User-Agent": "SmartCard-GPS-Tracker/4.0"}, timeout=5).json()
            addr = r.get("address", {})
            country = addr.get("country", "Unknown")
            city = addr.get("state_district") or addr.get("county") or addr.get("state") or "Unknown"
            thana = addr.get("town") or addr.get("city") or addr.get("village") or "Unknown"
            post_office = addr.get("postcode", "-")
            latF = float(lat); lonF = float(lon)
            if (24.14 <= latF <= 24.20) and (90.00 <= lonF <= 90.08):
                thana = "Mirzapur"; city = "Tangail District"
        except Exception as e:
            print("⛔ GPS Reverse Error", e)

    if location_source == "IP":
        try:
            from django.contrib.gis.geoip2 import GeoIP2
            g = GeoIP2()
            ip = request.META.get("REMOTE_ADDR")
            geo = g.city(ip)
            country = geo.get("country_name", "Unknown")
            city = geo.get("city", "Unknown")
            thana = geo.get("region", "Unknown")
            post_office = geo.get("postal_code", "-")
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            accuracy = 40
        except Exception as e:
            print("❗ GEO Lookup Failed →", e)

    visitor = request.user if request.user.is_authenticated and request.user != user else None

    ContactSaveLead.objects.create(
        profile=user,
        visitor=visitor,
        device_ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        latitude=lat,
        longitude=lon,
        country=country,
        city=city,
        thana=thana,
        post_office=post_office,
        accuracy=accuracy,
        location_source=location_source,
    )

    return JsonResponse({
        "status": "saved",
        "source": location_source,
        "accuracy": accuracy,
        "country": country,
        "city": city,
        "thana": thana,
    })


from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except:
        return None
