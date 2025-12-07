from django.db import models
from django.utils.text import slugify
import uuid
from app_accounts.models import CustomUser

class Company(models.Model):
    name = models.CharField(max_length=100)

    # ✅ Permanent URL ID (Never changes)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # ✅ Auto URL from Company Name
    slug = models.SlugField(unique=True, blank=True)

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

    def public_slug_url(self):
        return f"/pages/company/{self.slug}/"

    def public_uid_url(self):
        return f"/pages/company/id/{self.uid}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Company.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name





class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="employee_profiles")

    designation = models.CharField(max_length=100, blank=True, null=True)
    joined_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "user")

    def __str__(self):
        return f"{self.user.full_name or self.user.email} ({self.company.name})"




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

    class Meta:
        unique_together = ("company", "user")



class JobPost(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")

    title = models.CharField(max_length=150)
    description = models.TextField()

    location = models.CharField(max_length=120, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.company.name}"
