from django.db import models
from django.utils.text import slugify
import uuid
from app_accounts.models import CustomUser


# ================================
# ✅ COMPANY MODEL
# ================================
from django.db import models
from django.utils.text import slugify
import uuid
from app_accounts.models import CustomUser


class Company(models.Model):
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="owned_companies",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)

    # ✅ Human-friendly company username (SEO / UI)
    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True,
        help_text="Unique company username (used in URL)"
    )

    # 🔒 Permanent identifier (never changes)
    uid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    business_type = models.CharField(max_length=100, blank=True, null=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    facebook_page = models.URLField(blank=True, null=True)
    map_location = models.URLField(blank=True, null=True)

    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ================================
    # URL METHODS
    # ================================

    # 🔹 SEO / UI URL (slug based – can change)
    def get_absolute_url(self):
        return f"/pages/{self.slug}/"

    # 🔒 Permanent URL (UID based – never changes)
    def get_public_url(self):
        return f"/pages/id/{self.uid}/"

    # ================================
    # SAVE LOGIC
    # ================================
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Company.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# ================================
# ✅ EMPLOYEE MODEL (FULL HISTORY SUPPORT)
# ================================
class Employee(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="employee_profiles"
    )

    designation = models.CharField(max_length=100, blank=True, null=True)

    # ✅ System will auto-set join date
    joined_date = models.DateField(auto_now_add=True)

    leave_date = models.DateField(blank=True, null=True)

    salary = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} at {self.company}"


# ================================
# ✅ EMPLOYEE JOIN REQUEST
# ================================
class EmployeeJoinRequest(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    # ❌ unique_together REMOVED — So user can request again after leave

    def __str__(self):
        return f"{self.user.email} → {self.company.name} ({self.status})"


# ================================
# ✅ JOB POST (ONLY ONE VERSION)
# ================================
class JobPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")

    JOB_TYPE = (
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("freelance", "Freelance"),
    )

    title = models.CharField(max_length=150)
    description = models.TextField()

    location = models.CharField(max_length=120, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE, default="full_time")

    deadline = models.DateField(blank=True, null=True)  # ⭐ NEW

    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company.name}"


# ================================
# ✅ JOB APPLICATION
# ================================
class JobApplication(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("selected", "Selected"),
        ("rejected", "Rejected"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")

    phone = models.CharField(max_length=20)
    cv = models.FileField(upload_to="job_cvs/", null=True, blank=True)
    message = models.TextField(blank=True, null=True)

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "user")  # ✅ One user one application

    def __str__(self):
        return f"{self.user} → {self.job.title}"


class Product(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


