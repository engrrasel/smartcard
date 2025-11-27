from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .models import Contact
from django.http import JsonResponse
from .models import ContactNote
from django.db.models import Q


User = get_user_model()

@login_required
def my_contacts(request):
    contact_list = Contact.objects.filter(owner=request.user).order_by("-created_at")

    # Pagination
    paginator = Paginator(contact_list, 5)  # প্রতি পেজে ৫টি contact
    page = request.GET.get('page')
    contacts = paginator.get_page(page)

    return render(request, "app_contacts/my_contacts.html", {
        'contacts': contacts
    })



@login_required
def delete_contact(request, contact_id):
    if request.method == "DELETE":  # DELETE request coming from JS
        contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
        contact.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@login_required
def add_contact(request, user_id):

    sender = request.user                        # B = requester
    receiver = get_object_or_404(User, id=user_id)  # A = profile owner

    # Already pending request exists?
    if Contact.objects.filter(owner=receiver, visitor=sender, status="pending").exists():
        return redirect('app_accounts:public_profile', username=receiver.username)

    # If already accepted, don't duplicate
    if Contact.objects.filter(owner=receiver, visitor=sender, status="accepted").exists():
        return redirect('app_accounts:public_profile', username=receiver.username)

    # Send request → Only one way
    Contact.objects.create(owner=receiver, visitor=sender, status="pending")

    return redirect('app_accounts:public_profile', username=receiver.username)


@login_required
def request_view(request):
    requests = Contact.objects.filter(owner=request.user, status="pending")
    return render(request, "contacts/request.html", {"requests": requests})


@login_required
def accept_request(request, id):
    req = get_object_or_404(Contact, id=id, owner=request.user, status="pending")

    req.status = "accepted"
    req.save()

    # Reverse contact for requester 🔥
    Contact.objects.get_or_create(
        owner=req.visitor,   # B now gets A
        visitor=req.owner,   # A also becomes visible to B
        status="accepted"
    )

    return redirect("app_contacts:request_view")


@login_required
def reject_request(request, id):
    req = get_object_or_404(Contact, id=id, owner=request.user, status="pending")
    req.delete()
    return redirect("app_contacts:request_view")


# ==========================
# CONTACT DASHBOARD (MAIN)
# ==========================
@login_required
def contact_dashboard(request):
    contacts_count = Contact.objects.filter(owner=request.user).count()
    request_count  = Contact.objects.filter(visitor=request.user).count()

    return render(request, "contacts/connects_dashboard.html", {
        "contacts_count": contacts_count,
        "request_count": request_count,
    })


# ==========================
# ALL CONTACTS PAGE
# ==========================
@login_required
def add_contact(request, user_id):

    userA = request.user  # Request sender
    userB = get_object_or_404(User, id=user_id)

    # Request Already Exists?
    if Contact.objects.filter(owner=userB, visitor=userA, status="pending").exists():
        return redirect('app_accounts:public_profile', username=userB.username)

    # Create connection request only B side
    Contact.objects.create(owner=userB, visitor=userA, status="pending")

    return redirect('app_accounts:public_profile', username=userB.username)


# ==========================
# REQUEST LIST PAGE
# ==========================
@login_required
def request_view(request):
    requests = Contact.objects.filter(owner=request.user, status="pending")  # 🔥 only pending
    return render(request, "contacts/request.html", {"requests": requests})


@login_required
def accept_request(request, id):
    req = get_object_or_404(Contact, id=id, owner=request.user, status="pending")
    req.status = "accepted"
    req.save()

    # Reverse contact add
    Contact.objects.get_or_create(owner=req.visitor, visitor=request.user, status="accepted")

    return redirect("app_contacts:contact_request")


@login_required
def reject_request(request, id):
    req = get_object_or_404(Contact, id=id, owner=request.user, status="pending")
    req.delete()
    return redirect("app_contacts:contact_request")


# ==========================
# PENDING PAGE
# ==========================
@login_required
def pending_request(request):
    return render(request, "contacts/pending.html")


# ==========================
# CONTACT PROFILE PAGE
# ==========================
@login_required
def contact_profile_db(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "contacts/contact_profile.html", {"user": user})


@login_required
def add_contact_form(request):
    return render(request, "contacts/add_contact_form.html")



from django.http import JsonResponse

from django.http import JsonResponse

@login_required
def save_note(request, contact_id):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()

        if not text:
            return JsonResponse({"success": False, "message": "Note cannot be empty"})

        note = ContactNote.objects.create(contact_id=contact_id, text=text)

        return JsonResponse({
            "success": True,
            "text": note.text,
            "time": note.created_at.strftime("%d %b %Y — %I:%M %p"),
            "count": ContactNote.objects.filter(contact_id=contact_id).count()
        })

    # 🔥 এখানে GET রিকোয়েস্ট আসলে error নয়, JSON রিটার্ন করবে
    return JsonResponse({"success": False, "message": "Only POST allowed"}, status=405)


from django.views.decorators.csrf import csrf_exempt
from .models import Contact, ContactNote

@csrf_exempt
def track_action(request, contact_id, action):
    contact = Contact.objects.get(id=contact_id)

    if action == "call":
        contact.call_count += 1
    elif action == "email":
        contact.email_count += 1
    contact.save()

    return JsonResponse({"success": True,
                         "call": contact.call_count,
                         "email": contact.email_count})



@login_required
def my_connects_db(request, id):
    contact = get_object_or_404(Contact, id=id, owner=request.user)
    user = contact.visitor

    notes = ContactNote.objects.filter(contact=contact).order_by("-created_at")

    return render(request, "contacts/my_connects_db.html", {
        "contact": contact,
        "user": user,
        "notes": notes,           # ← এইটা ছিল না 😎
    })


@login_required
def show_notes(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
    notes = ContactNote.objects.filter(contact=contact).order_by("-created_at")

    return render(request, "contacts/all_notes.html", {
        "contact": contact,
        "notes": notes
    })



@login_required
def get_last_note(request, contact_id):
    note = ContactNote.objects.filter(contact_id=contact_id).order_by("-created_at").first()

    if note:
        return JsonResponse({
            "exists": True,
            "text": note.text,
            "time": note.created_at.strftime("%d %b %Y — %I:%M %p")
        })
    return JsonResponse({"exists": False})


@login_required
def all_connects(request):
    contacts = Contact.objects.filter(
        (Q(owner=request.user) | Q(visitor=request.user)),
        status="accepted"
    ).order_by("-created_at")

    return render(request, "contacts/my_connects.html", {"contacts": contacts})
