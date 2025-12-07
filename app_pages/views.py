from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Company, Employee, EmployeeJoinRequest, JobPost
from .forms import CompanyForm
from app_accounts.models import CustomUser


# ================================
# ✅ Company Pages
# ================================
def company_pages(request):
    selected_company = request.GET.get("company")
    companies = list(Company.objects.all())

    # ✅ Move selected company to top
    if selected_company:
        companies.sort(key=lambda c: str(c.id) != str(selected_company))

    return render(request, "pages/company_pages.html", {
        "companies": companies,
        "selected_company": selected_company,
        "unread_job_count": JobPost.objects.filter(is_active=True).count()
    })


# ================================
# ✅ Public Company URLs
# ================================
def company_public_by_uid(request, uid):
    company = get_object_or_404(Company, uid=uid)
    return render(request, "pages/company_public.html", {"company": company})


def company_public_by_slug(request, slug):
    company = get_object_or_404(Company, slug=slug)
    return render(request, "pages/company_public.html", {"company": company})


# ================================
# ✅ Add Company
# ================================
def add_company(request):
    form = CompanyForm()

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("app_pages:company_pages")

    return render(request, "pages/add_company_page.html", {
        "form": form
    })


# ================================
# ✅ Edit Company
# ================================
def edit_company(request, id):
    company = get_object_or_404(Company, id=id)

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


# ================================
# ✅ Employee Hub (Global Search + Joined List)
# ================================
def employee_hub(request):
    selected_company = request.GET.get("company")

    # ✅ Safety check against None / Invalid
    if not selected_company or selected_company == "None":
        selected_company = None

    joined_employees = []
    search_results = []

    if selected_company:
        joined_employees = Employee.objects.filter(company_id=selected_company)

        query = request.GET.get("q")
        if query:
            search_results = CustomUser.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            ).exclude(
                employee_profiles__company_id=selected_company
            )

    companies = list(Company.objects.all())
    if selected_company:
        companies.sort(key=lambda c: str(c.id) != str(selected_company))

    return render(request, "pages/employee_hub.html", {
        "joined_employees": joined_employees,
        "search_results": search_results,
        "selected_company": selected_company,
        "companies": companies,
        "unread_job_count": JobPost.objects.filter(is_active=True).count()
    })


# ================================
# ✅ Send Join Request
# ================================
def send_join_request(request, user_id):
    selected_company = request.GET.get("company")

    if not selected_company:
        return redirect("app_pages:employee_hub")

    company = get_object_or_404(Company, id=selected_company)
    user = get_object_or_404(CustomUser, id=user_id)

    join_request, created = EmployeeJoinRequest.objects.get_or_create(
        company=company,
        user=user
    )

    # ✅ যদি আগেই APPROVED থাকে → আবার রিকুয়েস্ট পাঠানো যাবে না
    if join_request.status == "approved":
        return redirect(f"/pages/employee/?company={company.id}")

    # ✅ যদি আগেই REJECTED থাকে → আবার PENDING করে দাও
    if join_request.status == "rejected":
        join_request.status = "pending"
        join_request.save()

    # ✅ যদি একেবারে নতুন হয় → Pending থাকবেই
    return redirect(f"/pages/employee/?company={company.id}")


# ================================
# ✅ Approve Join Request
# ================================
def approve_join_request(request, request_id):
    join_request = get_object_or_404(EmployeeJoinRequest, id=request_id)

    Employee.objects.get_or_create(
        company=join_request.company,
        user=join_request.user
    )

    join_request.status = "approved"
    join_request.save()

    return redirect(f"/pages/employee/?company={join_request.company.id}")


# ================================
# ✅ Job List
# ================================
def job_list(request):
    # ✅ সব Active Job
    jobs = JobPost.objects.filter(is_active=True).order_by("-created_at")

    # ✅ Login করা User-এর জন্য Pending Join Requests
    join_requests = EmployeeJoinRequest.objects.filter(
        user=request.user,
        status="pending"
    ).select_related("company")

    return render(request, "pages/job_list.html", {
        "jobs": jobs,
        "join_requests": join_requests,
    })


def accept_join_request(request, request_id):
    join_request = get_object_or_404(
        EmployeeJoinRequest,
        id=request_id,
        user=request.user,
        status="pending"
    )

    # ✅ Employee হিসেবে Bind হবে
    Employee.objects.get_or_create(
        company=join_request.company,
        user=request.user
    )

    join_request.status = "approved"
    join_request.save()

    return redirect("app_pages:job_list")


def reject_join_request(request, request_id):
    join_request = get_object_or_404(
        EmployeeJoinRequest,
        id=request_id,
        user=request.user
    )

    # ✅ একেবারে ডিলিট করে দিচ্ছি যাতে আবার নতুন করে রিকুয়েস্ট দেওয়া যায়
    join_request.delete()

    return redirect("app_pages:job_list")



def remove_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    company = employee.company
    user = employee.user

    # ✅ Employee Remove
    employee.delete()

    # ✅ সংশ্লিষ্ট Approved JoinRequest ও ডিলিট করলাম
    EmployeeJoinRequest.objects.filter(
        company=company,
        user=user
    ).delete()

    return redirect(f"/pages/employee/?company={company.id}")
