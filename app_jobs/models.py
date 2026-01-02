from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from app_pages.models import Company

User = settings.AUTH_USER_MODEL


class JobPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    salary = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company.name}"


class EmploymentRequest(models.Model):
    REQUEST_TYPE = [
        ("job_apply", "Job Apply"),          # Employee → Company
        ("company_invite", "Company Invite") # Company → Employee
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="employment_requests"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employment_requests"
    )

    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    cv = models.FileField(upload_to="job_cvs/", blank=True)

    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # 🚫 Duplicate job apply block
            models.UniqueConstraint(
                fields=["user", "job"],
                condition=models.Q(request_type="job_apply"),
                name="unique_job_application"
            ),
            # 🚫 Duplicate company invite block
            models.UniqueConstraint(
                fields=["user", "company"],
                condition=models.Q(request_type="company_invite"),
                name="unique_company_invite"
            ),
        ]

    def clean(self):
        # ✔ job_apply must have job
        if self.request_type == "job_apply" and not self.job:
            raise ValidationError("Job is required for job apply request.")

        # ✔ company_invite must NOT have job
        if self.request_type == "company_invite" and self.job:
            raise ValidationError("Company invite should not be linked to a job.")

    def __str__(self):
        return f"{self.company} ↔ {self.user} ({self.request_type})"
