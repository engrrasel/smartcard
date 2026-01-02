from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from app_jobs.models import EmploymentRequest
 
from .models import (
    Company,
    Employee,
    EmployeeJoinRequest,
)
from .forms import CompanyForm
from app_accounts.models import CustomUser


# ======================================
# ✅ COMPANY PAGES (ONLY OWN)
# ======================================
@login_required
def company_pages(request):
    selected_company = request.GET.get("company")
    companies = list(Company.objects.filter(owner=request.user))

    if selected_company:
        companies.sort(key=lambda c: str(c.id) != str(selected_company))

    return render(request, "pages/company_pages.html", {
        "companies": companies,
        "selected_company": selected_company,
    })


# ======================================
# ✅ PUBLIC COMPANY PAGES (OPEN)
# ======================================
def company_public_by_uid(request, uid):
    company = get_object_or_404(Company, uid=uid)
    return render(request, "pages/company_public.html", {"company": company})


def company_public_by_slug(request, slug):
    company = get_object_or_404(Company, slug=slug)
    return render(request, "pages/company_public.html", {"company": company})


# ======================================
# ✅ ADD COMPANY (OWNER)
# ======================================
@login_required
def add_company(request):
    form = CompanyForm()

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            return redirect("app_pages:company_pages")

    return render(request, "pages/add_company_page.html", {"form": form})


# ======================================
# ✅ EDIT COMPANY (ONLY OWNER)
# ======================================
@login_required
def edit_company(request, id):
    company = get_object_or_404(Company, id=id)

    if company.owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this company.")

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("app_pages:company_pages")
    else:
        form = CompanyForm(instance=company)

    return render(request, "pages/add_company_page.html", {
        "form": form,
        "edit_mode": True,
        "company": company,
    })


# ======================================
# ✅ EMPLOYEE HUB (ONLY OWNER)
# ======================================
@login_required
def employee_hub(request):
    selected_company = request.GET.get("company")
    joined_employees = []
    search_results = []

    companies = list(Company.objects.filter(owner=request.user))

    if selected_company:
        company = get_object_or_404(Company, id=selected_company)

        if company.owner != request.user:
            return HttpResponseForbidden("You are not allowed to manage this company.")

        joined_employees = Employee.objects.filter(
            company=company,
            is_active=True
        )

        query = request.GET.get("q")
        if query:
            active_user_ids = Employee.objects.filter(
                company=company,
                is_active=True
            ).values_list("user_id", flat=True)

            search_results = CustomUser.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            ).exclude(id__in=active_user_ids)

    if selected_company:
        companies.sort(key=lambda c: str(c.id) != str(selected_company))

    return render(request, "pages/employee_hub.html", {
        "joined_employees": joined_employees,
        "search_results": search_results,
        "selected_company": selected_company,
        "companies": companies,
    })


# ======================================
# ✅ SEND JOIN REQUEST (ONLY OWNER)
# ======================================
@login_required
def send_join_request(request, user_id):
    selected_company = request.GET.get("company")

    if not selected_company:
        return redirect("app_pages:employee_hub")

    company = get_object_or_404(Company, id=selected_company)

    # 🔒 Only company owner can invite
    if company.owner != request.user:
        return HttpResponseForbidden("Only the owner can send join requests.")

    # 👉 THIS is the employee being invited
    employee_user = get_object_or_404(CustomUser, id=user_id)

    join_request, created = EmploymentRequest.objects.get_or_create(
        user=employee_user,              # ✅ invite receiver
        company=company,
        request_type="company_invite",
        defaults={
            "status": "pending"
        }
    )

    # If previously rejected/accepted, reset to pending
    if not created and join_request.status in ["accepted", "rejected"]:
        join_request.status = "pending"
        join_request.save()

    return redirect(f"{reverse('app_pages:employee_hub')}?company={company.id}")

# ======================================
# ✅ APPROVE JOIN REQUEST (ONLY OWNER)
# ======================================
@login_required
def approve_join_request(request, request_id):
    join_request = get_object_or_404(EmployeeJoinRequest, id=request_id)

    if join_request.company.owner != request.user:
        return HttpResponseForbidden("You are not allowed to approve this request.")

    Employee.objects.create(
        company=join_request.company,
        user=join_request.user,
        joined_date=timezone.now().date(),
        is_active=True
    )

    join_request.status = "approved"
    join_request.save()

    return redirect(f"{reverse('app_pages:employee_hub')}?company={join_request.company.id}")


# ======================================
# ✅ REMOVE EMPLOYEE (ONLY OWNER)
# ======================================
@login_required
def remove_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if employee.company.owner != request.user:
        return HttpResponseForbidden("You are not allowed to remove this employee.")

    employee.is_active = False
    employee.leave_date = timezone.now().date()
    employee.save()

    return redirect(f"{reverse('app_pages:employee_hub')}?company={employee.company.id}")
