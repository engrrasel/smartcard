from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages

from .models import (
    Company,
    Employee,
    EmployeeJoinRequest,
    Product,
    JobPost,
)
from .forms import CompanyForm
from app_accounts.models import CustomUser
from app_jobs.models import EmploymentRequest


# ======================================
# ✅ COMPANY DASHBOARD (OWNER ONLY)
# ======================================
@login_required
def company_pages(request):
    companies = Company.objects.filter(owner=request.user)

    company_id = request.GET.get("company")
    selected_company = companies.filter(id=company_id).first() if company_id else companies.first()

    # 🔒 Permanent absolute public URL (UID based)
    for company in companies:
        company.absolute_public_url = request.build_absolute_uri(
            company.get_public_url()
        )

    return render(request, "pages/company_pages.html", {
        "companies": companies,
        "selected_company": selected_company,
        "active_tab": "dashboard",
    })


# ======================================
# ✅ PUBLIC COMPANY PAGES
# ======================================
def company_public_by_uid(request, uid):
    company = get_object_or_404(Company, uid=uid)
    return redirect(company.get_absolute_url())


def company_public_by_slug(request, slug):
    company = get_object_or_404(Company, slug=slug)
    return render(request, "pages/company_public.html", {"company": company})


# ======================================
# ✅ ADD COMPANY
# ======================================
@login_required
def add_company(request):
    form = CompanyForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.owner = request.user
        company.save()
        messages.success(request, "Company created successfully.")
        return redirect("app_pages:company_pages")

    return render(request, "pages/add_company_page.html", {
        "form": form,
    })


# ======================================
# ✅ MANAGE / EDIT COMPANY
# ======================================
@login_required
def company_manage(request, company_id):
    company = get_object_or_404(
        Company,
        id=company_id,
        owner=request.user
    )

    form = CompanyForm(
        request.POST or None,
        request.FILES or None,
        instance=company
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Company information updated successfully.")
        return redirect("app_pages:company_pages")

    return render(request, "pages/add_company_page.html", {
        "form": form,
        "edit_mode": True,
        "company": company,
        "active_tab": "manage",
    })


# ======================================
# ✅ PRODUCTS (COMPANY WISE)
# ======================================
@login_required
def company_products(request):
    companies = list(Company.objects.filter(owner=request.user))

    selected_company = get_object_or_404(
        Company,
        id=request.GET.get("company"),
        owner=request.user
    )

    products = Product.objects.filter(company=selected_company)
    companies.sort(key=lambda c: c.id != selected_company.id)

    return render(request, "pages/company_products.html", {
        "companies": companies,
        "selected_company": selected_company,
        "products": products,
        "active_tab": "products",
    })


# ======================================
# ✅ EMPLOYEE HUB
# ======================================
@login_required
def employee_hub(request):
    company_id = request.GET.get("company")

    companies = list(Company.objects.filter(owner=request.user))
    selected_company = None
    joined_employees = []
    search_results = []

    if company_id:
        selected_company = get_object_or_404(
            Company,
            id=company_id,
            owner=request.user
        )

        joined_employees = Employee.objects.filter(
            company=selected_company,
            is_active=True
        )

        query = request.GET.get("q")
        if query:
            active_user_ids = joined_employees.values_list("user_id", flat=True)
            search_results = CustomUser.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            ).exclude(id__in=active_user_ids)

        companies.sort(key=lambda c: c.id != selected_company.id)

    return render(request, "pages/employee_hub.html", {
        "companies": companies,
        "selected_company": selected_company,
        "joined_employees": joined_employees,
        "search_results": search_results,
        "active_tab": "employee",
    })


# ======================================
# ✅ SEND JOIN REQUEST
# ======================================
@login_required
def send_join_request(request, user_id):
    company = get_object_or_404(
        Company,
        id=request.GET.get("company"),
        owner=request.user
    )

    user = get_object_or_404(CustomUser, id=user_id)

    join_request, created = EmploymentRequest.objects.get_or_create(
        user=user,
        company=company,
        request_type="company_invite",
        defaults={"status": "pending"}
    )

    if not created and join_request.status in ["accepted", "rejected"]:
        join_request.status = "pending"
        join_request.save()

    return redirect(
        f"{reverse('app_pages:employee_hub')}?company={company.id}"
    )


# ======================================
# ✅ APPROVE JOIN REQUEST
# ======================================
@login_required
def approve_join_request(request, request_id):
    join_request = get_object_or_404(EmployeeJoinRequest, id=request_id)

    if join_request.company.owner != request.user:
        return HttpResponseForbidden()

    Employee.objects.create(
        company=join_request.company,
        user=join_request.user,
        joined_date=timezone.now().date(),
        is_active=True
    )

    join_request.status = "approved"
    join_request.save()

    return redirect(
        f"{reverse('app_pages:employee_hub')}?company={join_request.company.id}"
    )


# ======================================
# ✅ REMOVE EMPLOYEE
# ======================================
@login_required
def remove_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if employee.company.owner != request.user:
        return HttpResponseForbidden()

    employee.is_active = False
    employee.leave_date = timezone.now().date()
    employee.save()

    return redirect(
        f"{reverse('app_pages:employee_hub')}?company={employee.company.id}"
    )


# ======================================
# ✅ RECRUITMENT (JOB POSTS)
# ======================================
@login_required
def recruitment_dashboard(request):
    companies = list(Company.objects.filter(owner=request.user))

    selected_company = get_object_or_404(
        Company,
        id=request.GET.get("company"),
        owner=request.user
    )

    jobs = JobPost.objects.filter(company=selected_company)
    companies.sort(key=lambda c: c.id != selected_company.id)

    return render(request, "pages/recruitment_dashboard.html", {
        "companies": companies,
        "selected_company": selected_company,
        "jobs": jobs,
        "active_tab": "recruitment",
    })


# ======================================
# ✅ EMPLOYEE LIVE SEARCH (AJAX)
# ======================================
@login_required
def employee_live_search(request):
    company_id = request.GET.get("company")
    q = request.GET.get("q", "").strip()

    if not company_id or not q:
        return JsonResponse({"results": []})

    company = get_object_or_404(Company, id=company_id)

    if company.owner != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    active_ids = Employee.objects.filter(
        company=company,
        is_active=True
    ).values_list("user_id", flat=True)

    users = CustomUser.objects.filter(
        Q(full_name__icontains=q) |
        Q(email__icontains=q) |
        Q(phone__icontains=q)
    ).exclude(id__in=active_ids)[:10]

    return JsonResponse({
        "results": [{
            "id": u.id,
            "name": u.full_name or "—",
            "email": u.email,
            "avatar": u.profile_picture.url if u.profile_picture else "/static/img/default-user.png"
        } for u in users]
    })


# ======================================
# ✅ DEACTIVATE COMPANY
# ======================================
@login_required
def company_deactivate(request, company_id):
    company = get_object_or_404(
        Company,
        id=company_id,
        owner=request.user
    )

    company.is_active = False
    company.save()

    messages.success(request, "Company page has been deactivated.")
    return redirect("app_pages:company_pages")



@login_required
def employee_profile_dashboard(request, pk):
    return redirect("app_account:profile_and_card_dashboard", pk=pk)
