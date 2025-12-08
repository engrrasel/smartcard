from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse

from .models import (
    Company,
    Employee,
    EmployeeJoinRequest,
    JobPost,
    JobApplication
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
        "unread_job_count": JobPost.objects.filter(is_active=True).count()
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

        # ✅ শুধু Active Employees
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
        "unread_job_count": JobPost.objects.filter(is_active=True).count()
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

    if company.owner != request.user:
        return HttpResponseForbidden("Only the owner can send join requests.")

    user = get_object_or_404(CustomUser, id=user_id)

    join_request, created = EmployeeJoinRequest.objects.get_or_create(
        company=company,
        user=user
    )

    if join_request.status in ["approved", "rejected"]:
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

    # ✅ নতুন Employee History তৈরি হবে
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
# ✅ JOB LIST (USER DASHBOARD)
# ======================================
@login_required
def job_list(request):

    jobs = JobPost.objects.filter(is_active=True).order_by("-created_at")

    join_requests = EmployeeJoinRequest.objects.filter(
        user=request.user,
        status="pending"
    ).select_related("company")

    # ✅ সব History দেখাবে
    my_jobs = Employee.objects.filter(
        user=request.user
    ).select_related("company").order_by("-joined_date")

    return render(request, "pages/job_list.html", {
        "jobs": jobs,
        "join_requests": join_requests,
        "my_jobs": my_jobs,
    })


# ======================================
# ✅ ACCEPT JOIN (USER)
# ======================================
@login_required
def accept_join_request(request, request_id):
    join_request = get_object_or_404(
        EmployeeJoinRequest,
        id=request_id,
        user=request.user,
        status="pending"
    )

    Employee.objects.create(
        company=join_request.company,
        user=request.user,
        joined_date=timezone.now().date(),
        is_active=True
    )

    join_request.status = "approved"
    join_request.save()

    return redirect("app_pages:job_list")


# ======================================
# ✅ REJECT JOIN (USER)
# ======================================
@login_required
def reject_join_request(request, request_id):
    join_request = get_object_or_404(
        EmployeeJoinRequest,
        id=request_id,
        user=request.user,
        status="pending"
    )

    join_request.status = "rejected"
    join_request.save()

    return redirect("app_pages:job_list")


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


# ======================================
# ✅ CREATE JOB (OWNER + ADMIN)
# ======================================
@login_required
def create_job(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if company.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to post jobs.")

    if request.method == "POST":
        JobPost.objects.create(
            company=company,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            location=request.POST.get("location"),
            salary=request.POST.get("salary"),
            job_type=request.POST.get("job_type"),
            is_public=True
        )
        return redirect("app_pages:company_pages")

    return render(request, "pages/job_create.html", {"company": company})


# ======================================
# ✅ PUBLIC JOB LIST (OPEN)
# ======================================
def public_job_list(request):
    jobs = JobPost.objects.filter(
        is_active=True,
        is_public=True
    ).select_related("company").order_by("-created_at")

    return render(request, "pages/public_job_list.html", {"jobs": jobs})


# ======================================
# ✅ JOB DETAILS + APPLY
# ======================================
@login_required
def job_details(request, id):
    job = get_object_or_404(JobPost, id=id, is_active=True)

    already_applied = JobApplication.objects.filter(
        job=job,
        user=request.user
    ).exists()

    if request.method == "POST" and not already_applied:
        cv_file = request.FILES.get("cv")
        if cv_file:
            JobApplication.objects.create(
                job=job,
                user=request.user,
                phone=request.POST.get("phone"),
                message=request.POST.get("message"),
                cv=cv_file
            )
        return redirect("app_pages:job_details", id=job.id)

    return render(request, "pages/job_details.html", {
        "job": job,
        "already_applied": already_applied
    })


@login_required
def my_job_posts(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if company.owner != request.user:
        return HttpResponseForbidden("You cannot view this company's jobs.")

    jobs = JobPost.objects.filter(company=company).order_by("-created_at")

    return render(request, "pages/my_job_posts.html", {
        "company": company,
        "jobs": jobs
    })


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    if job.company.owner != request.user:
        return HttpResponseForbidden("You cannot edit this job.")

    if request.method == "POST":
        job.title = request.POST.get("title")
        job.description = request.POST.get("description")
        job.location = request.POST.get("location")
        job.salary = request.POST.get("salary")
        job.job_type = request.POST.get("job_type")
        job.deadline = request.POST.get("deadline")
        job.save()

        return redirect("app_pages:my_job_posts", company_id=job.company.id)

    return render(request, "pages/job_edit.html", {"job": job})


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    if job.company.owner != request.user:
        return HttpResponseForbidden("You cannot delete this job.")

    job.is_active = False
    job.save()

    return redirect("app_pages:my_job_posts", company_id=job.company.id)
