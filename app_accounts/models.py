# Updated models.py (Option B: merge parent_user + keep old structure)

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from datetime import date

# ─────────────────────────────────────────────
# 🔵 Custom User Manager
# ─────────────────────────────────────────────
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# ─────────────────────────────────────────────
# 🔵 Custom User Model (Now supports parent_user + profile-like fields)
# ─────────────────────────────────────────────
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Login
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    activation_date = models.DateTimeField(null=True, blank=True)

    # NEW → Parent user = যেই user এই profile/user তৈরি করেছে
    parent_user = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="child_profiles"
    )

    # Subscription
    ACCOUNT_TYPE_CHOICES = [
        ("free", "Free"),
        ("premium", "Premium"),
        ("unlimited", "Unlimited"),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default="free")

    # Profile fields (moved from UserProfile)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    username = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Analytics
    daily_views = models.PositiveIntegerField(default=0)
    monthly_views = models.PositiveIntegerField(default=0)
    yearly_views = models.PositiveIntegerField(default=0)
    last_viewed = models.DateField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-updated_at", "-date_joined"]

    def __str__(self):
        return self.full_name or self.email

    # Public URL
    def get_absolute_url(self):
        if not self.username:
            return reverse("app_accounts:dashboard")
        return reverse("app_accounts:public_profile", args=[self.username])

    # Profile creation limit logic
    def can_create_profile(self):
        count = self.child_profiles.count()

        if self.account_type == "unlimited":
            return True
        if self.account_type == "premium":
            return count < 10
        return count < 1  # free user can create 1 profile

    # Auto-generate username
    def save(self, *args, **kwargs):
        if not self.username:
            base = slugify(self.full_name or self.email.split("@")[0])
            username = base or "user"
            count = 1

            qs = CustomUser.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            while qs.filter(username=username).exists():
                username = f"{base}-{count}"
                count += 1

            self.username = username

        super().save(*args, **kwargs)
