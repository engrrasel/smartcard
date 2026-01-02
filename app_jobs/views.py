from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from app_jobs.models import JobPost, EmploymentRequest
from app_pages.models import Employee


from datetime import date

@login_required
def career_dashboard(request):
    tab = request.GET.get("tab", "available")

    jobs = JobPost.objects.filter(
        is_active=True,
        is_public=True
    ).select_related("company")

    my_jobs = Employee.objects.filter(
        user=request.user
    ).select_related("company").order_by("-created_at")

    # 🔹 duration হিসাব
    today = date.today()
    for emp in my_jobs:
        end_date = emp.leave_date if emp.leave_date else today
        emp.duration_days = (end_date - emp.joined_date).days

    requests = EmploymentRequest.objects.filter(
        user=request.user,
        request_type="company_invite",
        status="pending"
    ).select_related("company")

    return render(request, "app_jobs/career_dashboard.html", {
        "active_tab": tab,
        "jobs": jobs,
        "my_jobs": my_jobs,
        "requests": requests,
    })



@login_required
@require_POST
def employment_request_action(request, pk):
    action = request.POST.get("action")

    req = get_object_or_404(
        EmploymentRequest,
        pk=pk,
        user=request.user,
        status="pending"
    )

    if action == "accept":
        Employee.objects.create(
            user=req.user,
            company=req.company,
            is_active=True
        )
        req.status = "accepted"
        req.save()

    elif action == "reject":
        req.status = "rejected"
        req.save()

    return redirect("app_jobs:career_dashboard")
