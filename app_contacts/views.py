from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .models import Contact
from django.http import JsonResponse

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
    contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
    contact.delete()
    return redirect("my_contacts")

@login_required
def add_contact(request, user_id):
    owner = get_object_or_404(User, id=user_id)
    visitor = request.user

    if not Contact.objects.filter(owner=owner, visitor=visitor).exists():
        Contact.objects.create(owner=owner, visitor=visitor)

    return redirect('app_accounts:public_profile', username=owner.username)




@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, owner=request.user)
    contact.delete()

    return JsonResponse({"success": True})


from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def contact_profile_db(request, user_id):
    person = get_object_or_404(User, id=user_id)
    return render(request, "app_contacts/contact_profile_db.html", {"person": person})
