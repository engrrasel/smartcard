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
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps   # ←⭐ Lazy load model fix
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import timedelta  
from django.db.models import Count

from .models import CustomUser, ContactSaveLead
from .utils import get_client_ip, parse_user_agent
# ----- Models -----
from app_accounts.models import CustomUser
# ❗ ContactSaveLead direct import remove করা হয়েছে

# ----- Others -----
import requests
import qrcode
import base64
import urllib.parse
from io import BytesIO

# ----- Forms -----
from .forms import SignupForm, ChildProfileCreateForm, ProfileUpdateForm

User = get_user_model()

# --- Lazy Load Function (Reusable) ---
def LeadModel():
    return apps.get_model('app_contacts', 'ContactSaveLead')  # ←🔥 Safe import


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

            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
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
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
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
            child.set_password("12345678")  # Default password

            if not child.username:
                base = child.email.split("@")[0]
                new_user = base
                counter = 1
                while CustomUser.objects.filter(username=new_user).exists():
                    new_user = f"{base}{counter}"; counter += 1
                child.username = new_user

            child.save()
            messages.success(request, "Profile created successfully!")
            return redirect("app_accounts:profile_and_card")

    return render(request, "accounts/profile_create.html", {"form": ChildProfileCreateForm()})


# ───────────────────────────────────────────────
@login_required
def edit_profile(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if profile != request.user and profile.parent_user != request.user: return HttpResponse("Forbidden", 403)

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
    if profile != request.user and profile.parent_user != request.user: return HttpResponse("Forbidden",403)

    if profile.profile_picture: profile.profile_picture.delete(save=True)
    messages.success(request, "Profile picture removed.")
    return redirect("app_accounts:edit_profile", pk=pk)


# ───────────────────────────────────────────────
def public_profile(request, username):
    profile = get_object_or_404(CustomUser, username=username)

    # ===================== Visitor Location Log Here =====================
    ip = get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")

    lat = request.GET.get("lat")   # JS থেকে আসবে
    lon = request.GET.get("lon")

    if lat and lon:     # GPS Detected
        try:
            geo = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"format":"json","lat":lat,"lon":lon,"zoom":18,"accept-language":"en"},
                headers={"User-Agent":"SmartCard-Visit/1.0"}
            ).json()

            addr = geo.get("address", {})
            country = addr.get("country")
            district = addr.get("state_district") or addr.get("county")
            thana = addr.get("town") or addr.get("village")
            post = addr.get("postcode")
        except:
            country=district=thana=post=None
    
        ContactSaveLead.objects.create(
            profile=profile,
            device_ip=ip,
            user_agent="PROFILE_VISIT | "+ua,
            latitude=lat, longitude=lon,
            country=country, city=district,
            thana=thana, post_office=post
        )

    # ========================================================

    return render(request,"accounts/public_profile.html",{"profile":profile})


# ───────────────────────────────────────────────
@login_required
def download_qr(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if profile!=request.user and profile.parent_user!=request.user: return HttpResponse("Forbidden",403)

    qr = qrcode.make(request.build_absolute_uri(reverse("app_accounts:public_profile_by_id",args=[profile.public_id])))
    b = BytesIO(); qr.save(b,"PNG"); b.seek(0)
    res = HttpResponse(b,"image/png")
    res["Content-Disposition"]=f'attachment; filename="{profile.username}.png"'
    return res


# ───────────────────────────────────────────────


@login_required
def profile_and_card_dashboard(request, pk):
    profile = get_object_or_404(CustomUser, pk=pk)

    if profile != request.user and profile.parent_user != request.user:
        return HttpResponse("Forbidden", 403)

    # ====================== FIXED — Main Query (Un-Sliced!) ======================
    base = ContactSaveLead.objects.filter(profile=profile).order_by("-timestamp")

    # UI তে দেখানোর জন্য আমরা শুধু slice নিচ্ছি — filter এর পরে 👍
    leads = base[:200]
    location_logs = base[:50]

    # ================= ANALYTICS =================
    total_views = base.count()
    gps_count   = base.filter(latitude__isnull=False, longitude__isnull=False).count()
    ip_count    = total_views - gps_count

    mobile  = base.filter(user_agent__icontains="Mobile").count()
    tablet  = base.filter(user_agent__icontains="Tablet").count()
    desktop = total_views - (mobile + tablet)

    # ========== LAST 15 DAYS CHART ==========
    today = timezone.now().date()
    labels, values = [], []

    for i in range(15):
        d = today - timedelta(days=(14-i))
        labels.append(d.strftime("%d %b"))
        values.append(base.filter(timestamp__date=d).count())

    # ========== TOP COUNTRY ==========
    top_countries = base.values("country").annotate(c=Count("id")).order_by("-c")[:5]

    # ========== BUTTON CLICK COUNTS ==========
    click_logs = base.exclude(user_agent__icontains="Unknown")[:50]  # optional

    click_stats = {
        "total": total_views,
        "connect": base.filter(user_agent__icontains="connect").count(),
        "save": base.filter(user_agent__icontains="save").count(),
        "call": base.filter(user_agent__icontains="call").count(),
    }

    return render(request,"accounts/profile_and_card_dashboard.html",{
        "profile": profile,
        "leads": leads,
        "location_logs": location_logs,

        # Main Analytics
        "total_views": total_views,
        "gps_count": gps_count,
        "ip_count": ip_count,
        "mobile_count": mobile,
        "tablet_count": tablet,
        "desktop_count": desktop,
        "chart_labels": labels,
        "chart_values": values,
        "top_countries": top_countries,

        # Click Analytics
        "click_logs": click_logs,
        "click_stats": click_stats,
    })




# ───────────────────────────────────────────────
@login_required
def profile_search(request):
    query=request.GET.get("q","").strip()
    profiles=User.objects.filter(Q(pk=request.user.pk)|Q(parent_user=request.user))
    if query: profiles=profiles.filter(full_name__icontains=query)

    return render(request,"dashboard/profile_search.html",{"results":profiles,"query":query})


# ───────────────────────────────────────────────
@login_required
@require_POST
def toggle_public_view(request,profile_id):
    try:
        profile=User.objects.get(id=profile_id)
        if profile!=request.user and profile.parent_user!=request.user:
            return JsonResponse({"status":"error","message":"Forbidden"},403)

        profile.is_public=not profile.is_public; profile.save()
        return JsonResponse({"status":"success","is_public":profile.is_public})

    except User.DoesNotExist:
        return JsonResponse({"status":"error","message":"Profile not found"},404)


# ───────────────────────────────────────────────
@login_required
def unlink_profile(request,pk):
    profile=get_object_or_404(User,pk=pk)
    if profile.parent_user!=request.user: return HttpResponse("Forbidden",403)
    profile.parent_user=None; profile.save(update_fields=["parent_user"])
    messages.success(request,"Child profile unlinked.")
    return redirect("app_accounts:profile_and_card")


# ───────────────────────────────────────────────
def download_contact_vcard(request,username):
    profile=get_object_or_404(User,username=username)
    v=f"""BEGIN:VCARD
VERSION:3.0
FN:{profile.full_name}
TEL:{profile.phone}
EMAIL:{profile.email}
ORG:{profile.company_name}
TITLE:{profile.job_title}
URL:{profile.website}
END:VCARD"""

    r=HttpResponse(v,'text/vcard')
    r['Content-Disposition']=f'attachment; filename="{profile.username}.vcf"'
    return r


def subscription(request):
    return render(request,"dashboard/subscription.html")


def public_profile_by_id(request,public_id):
    profile=CustomUser.objects.filter(public_id=public_id,is_public=True).first()
    if not profile:return render(request,"accounts/profile_not_found.html",status=404)
    return redirect("app_accounts:public_profile",username=profile.username)


# ───────────────────────────────────────────────
def ip_to_location(ip):
    try:
        r=requests.get(f"http://ip-api.com/json/{ip}",timeout=2).json()
        return r.get("city"),r.get("country")
    except:
        return None,None


# ───────────────────────────────────────────────


# ───────────────────────────────────────────────
def track_save_gps(request, username):
    """
    Save Contact বাটনে ক্লিকের সময়:
    - GPS থাকলে lat/lon সহ log
    - না থাকলে শুধুই IP + UA log
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST only"}, status=405)

    # ❗ পূর্বে ছিল UserProfile → কিন্তু তোমার model হলো CustomUser
    profile = get_object_or_404(CustomUser, username=username)

    ip = get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")

    lat = request.POST.get("lat")
    lon = request.POST.get("lon")

    is_gps = bool(lat and lon)

    # 🔥 parse_user_agent আসলেই use হবে তাই রেখেছি (তুমি ডিলিট চাইনি)
    device_type, browser, os_name = parse_user_agent(ua)

    # ❗ ProfileVisitLead model তোমার প্রোজেক্টে নেই
    # তাই তোমার existing ContactSaveLead use করেই same log save করছি

    lead = ContactSaveLead.objects.create(
        profile=profile,
        device_ip=ip,
        user_agent=ua,
        latitude=lat or None,
        longitude=lon or None,
        # 🔥 তোমার original কোডের is_gps / device browser save-logic remove করিনি
        # তবে DB তে field নাই → তাই JSON response এ preserve রাখলাম
    )

    # Save করার পর আবার public profile-এ পাঠানো হচ্ছে (Original logic untouched)
    redirect_url = reverse("app_accounts:public_profile", args=[username])

    return JsonResponse({
        "success": True,
        "url": redirect_url,
        "lead_id": lead.id,
        "gps_used": is_gps,        # ⭐ original idea preserved
        "browser": browser,
        "device": device_type,
        "os": os_name,
    })




@require_POST
@csrf_exempt
def click_track(request, username):
    user = get_object_or_404(CustomUser, username=username)

    ip = get_client_ip(request)
    ua = request.META.get("HTTP_USER_AGENT", "")
    action = request.POST.get("action")

    # 🔥 Only store click action (No Location Track)
    ContactSaveLead.objects.create(
        profile=user,
        device_ip=ip,
        user_agent=f"{action} | {ua}",
        latitude=None,
        longitude=None,
        country=None,
        city=None,
        thana=None,
        post_office=None,
    )

    return JsonResponse({"saved": True, "action": action})




@csrf_exempt
def track_visit(request, username):
    print("📌 TRACK VISIT HIT — USER =", username)

    user = get_object_or_404(CustomUser, username=username)

    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    acc_raw = request.GET.get("accuracy")  # meter-based accuracy from JS

    # ---------- ACCURACY CONVERT FUNCTION ----------
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
        except Exception:
            return None

    # Default values
    country = city = thana = post_office = "Unknown"
    location_source = "IP"  # default fallback
    accuracy = convert_accuracy(acc_raw) or 50

    # ----------- Decide: GPS usable or not? ----------
    gps_allowed = bool(lat and lon and acc_raw)
    gps_accuracy_m = None

    if gps_allowed:
        try:
            gps_accuracy_m = float(acc_raw)
        except Exception:
            gps_allowed = False

    # যদি GPS আছে কিন্তু accuracy অনেক খারাপ (৩৫০m+) → IP হিসেবে ধরব
    if gps_allowed and gps_accuracy_m is not None and gps_accuracy_m <= 350:
        location_source = "GPS"
    else:
        lat = None
        lon = None
        location_source = "IP"

    # ================= GPS REVERSE GEO =================
    # ================= GPS REVERSE GEO =================
# ================= GPS SMART REVERSE GEO =================
    if location_source == "GPS":
        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "format": "json",
                    "lat": lat,
                    "lon": lon,
                    "zoom": 18,
                    "accept-language": "en",
                    "addressdetails": 1
                },
                headers={"User-Agent": "SmartCard-GPS-Tracker/3.0"}
            ).json()

            addr = r.get("address", {})

            country = addr.get("country", "Unknown")

            # Main City/District Field
            city = (
                addr.get("state_district")
                or addr.get("county")
                or addr.get("state")
                or "Unknown"
            )

            # Raw possible thana sources
            detected = [
                addr.get("town"), addr.get("city"),
                addr.get("municipality"), addr.get("village"),
                addr.get("suburb"), addr.get("hamlet"),
                addr.get("neighbourhood"), addr.get("quarter")
            ]
            thana = next((x for x in detected if x), "Unknown")

            post_office = addr.get("postcode", "-")

            # 🔥 AUTO FIX → IF GPS area is inside Mirzapur range
            lat_f = float(lat); lon_f = float(lon)

            # -------- Mirzapur GPS Boundary --------
            # তুমি চাইলে আমি boundary আরও refine করে দেব।
            if 24.07 <= lat_f <= 24.26 and 90.00 <= lon_f <= 90.25:
                thana = "Mirzapur"

            print("📍 RAW:", addr)
            print("🏷 FINAL THANA:", thana)

        except Exception as e:
            print("⛔ GPS GEO ERROR =", e)



    # ================= IP GEO (fallback) =================
    if location_source == "IP":
        try:
            from django.contrib.gis.geoip2 import GeoIP2

            g = GeoIP2()
            ip = request.META.get("REMOTE_ADDR")

            geo = g.city(ip)  # city lookup

            country = geo.get("country_name", "Unknown")
            city = geo.get("city", "Unknown")
            # GeoIP2 তে সাধারণত 'region' বা 'region_name' থাকে
            thana = geo.get("region", "Unknown") or geo.get("region_name", "Unknown")
            post_office = geo.get("postal_code", "-")

            lat = geo.get("latitude")
            lon = geo.get("longitude")

            accuracy = 40  # approx for IP

            print("🌍 IP GEO SUCCESS:", country, city)

        except Exception as e:
            print("❗ GEO Lookup Failed →", e)

    # ---------- SAVE TO DATABASE ----------
    ContactSaveLead.objects.create(
        profile=user,
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

    print("✔ Location Stored Successfully →", location_source, "ACC%", accuracy)
    return JsonResponse({
        "status": "saved",
        "source": location_source,
        "accuracy": accuracy,
        "country": country,
        "city": city,
        "thana": thana,
    })
