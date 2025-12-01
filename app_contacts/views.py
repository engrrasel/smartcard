from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Contact, ContactNote
from django.utils import timezone 

User = get_user_model()


# ==========================
# 📌 My Contacts Page
# ==========================
@login_required
def my_contacts(request):
    contact_list = Contact.objects.filter(
        owner=request.user, 
        status__in=["accepted", "saved"]   # 🟢 savedও দেখবে
    ).order_by("-created_at")

    paginator = Paginator(contact_list, 5)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)
    return render(request, "app_contacts/my_contacts.html", {'contacts': contacts})


# ==========================
# 🔥 Send Connection Request
# ==========================
@login_required(login_url='/login/')
def add_contact(request, user_id):
    sender = request.user                     # খ
    receiver = get_object_or_404(User, id=user_id)  # ক

    # 🔹 ক এর কাছে pending request send হবে
    Contact.objects.get_or_create(
        owner=receiver,
        visitor=sender,
        defaults={"status": "pending"}
    )

    # 🔹 খ-এর লিস্টে saved immediately দেখাবে
    Contact.objects.get_or_create(
        owner=sender,
        visitor=receiver,
        defaults={"status": "saved"}  # pending নয়, saved দেখাবে
    )

    return redirect('app_accounts:public_profile', username=receiver.username)



# ==========================
# 📬 Incoming Requests
# ==========================
@login_required
def request_view(request):
    requests = Contact.objects.filter(owner=request.user, status="pending")

    return render(request, "contacts/request.html", {
        "requests": requests,
        "req_count": requests.count(),   # ← 🔥 COUNT added
    })



# ==========================
# 🟢 Accept Request
# ==========================
@login_required
def accept_request(request, id):
    req = get_object_or_404(Contact, id=id, owner=request.user, status="pending")
    req.status = "accepted"
    req.save()

    Contact.objects.get_or_create(owner=req.visitor, visitor=req.owner, status="accepted")

    return JsonResponse({"success": True, "id": id, "action": "accepted"})



# ==========================
# 🔴 Reject Request
# ==========================
@login_required
def reject_request(request, id):
    req = get_object_or_404(Contact, id=id, owner=request.user, status="pending")
    req.delete()
    return JsonResponse({"success": True, "id": id, "action": "rejected"})



# ==========================
# 📊 Dashboard
# ==========================
@login_required
def contact_dashboard(request):
    contacts_count = Contact.objects.filter(owner=request.user, status="accepted").count()
    request_count = Contact.objects.filter(owner=request.user, status="pending").count()

    return render(request, "contacts/connects_dashboard.html", {
        "contacts_count": contacts_count,
        "request_count": request_count,
    })



# ==========================
# 🔗 Accepted Connections
# ==========================
@login_required(login_url='/login/')
def all_connects(request):
    contacts = Contact.objects.filter(
        owner=request.user, 
        status__in=["accepted", "saved"]
    ).order_by("-created_at")

    return render(request, "contacts/all_connects.html", {"contacts": contacts})



# ==========================
# 👤 Single Profile DB Page
# ==========================
@login_required
def my_connects_db(request, id):
    contact = get_object_or_404(Contact, id=id, owner=request.user)
    user = contact.visitor
    notes = ContactNote.objects.filter(contact=contact).order_by("-created_at")

    return render(request, "contacts/my_connects_db.html", {
        "contact": contact,
        "user": user,
        "notes": notes,
    })



# ==========================
# 🗑 Delete Contact
# ==========================
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_contact(request, contact_id):
    # যেই Contact delete করতে চাচ্ছি
    contact = get_object_or_404(Contact, id=contact_id)

    # লগইন করা ইউজার owner না visitor – দুজনের একজন না হলে delete করতে দেবে না
    if contact.owner != request.user and contact.visitor != request.user:
        return JsonResponse({"success": False, "error": "Not allowed"}, status=403)

    # ✅ আগে সব note / child ডাটা delete করি (FK constraint safe)
    ContactNote.objects.filter(contact_id=contact_id).delete()

    # ✅ তারপর main contact delete করি
    contact.delete()

    return JsonResponse({"success": True})

# ==========================
# 📝 Save Note
# ==========================
@login_required
def save_note(request, contact_id):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()

        if not text:
            return JsonResponse({"success": False, "message": "Note cannot be empty"})

        note = ContactNote.objects.create(contact_id=contact_id, text=text)

        # 🔥 UTC → Local time convert
        local_time = timezone.localtime(note.created_at)

        return JsonResponse({
            "success": True,
            "text": note.text,
            "time": local_time.strftime("%d %b %Y — %I:%M %p"),
            "count": ContactNote.objects.filter(contact_id=contact_id).count()
        })

    return JsonResponse({"success": False, "message": "Only POST allowed"}, status=405)



# ==========================
# 🔄 Last Note Fetch (AJAX)
# ==========================
@login_required
def get_last_note(request, contact_id):
    note = ContactNote.objects.filter(contact_id=contact_id).order_by("-created_at").first()

    if note:
        # 🕒 UTC → Bangladesh local time
        local_time = timezone.localtime(note.created_at)

        return JsonResponse({
            "exists": True,
            "text": note.text,
            "time": local_time.strftime("%d %b %Y — %I:%M %p"),
        })
    return JsonResponse({"exists": False})



@login_required
def pending_request(request):
    return render(request, "contacts/pending.html")


@login_required
def contact_profile_db(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "contacts/contact_profile.html", {"user": user})



@login_required
def show_notes(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
    notes = ContactNote.objects.filter(contact=contact).order_by("-created_at")

    return render(request, "contacts/all_notes.html", {
        "contact": contact,
        "notes": notes
    })


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def track_action(request, contact_id, action):
    contact = Contact.objects.get(id=contact_id)

    if action == "call":
        contact.call_count += 1
    elif action == "email":
        contact.email_count += 1

    contact.save()

    return JsonResponse({
        "success": True,
        "call": contact.call_count,
        "email": contact.email_count
    })


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    request.session.flush()   # 💥 multi-tab session kill
    return redirect('/login/')
