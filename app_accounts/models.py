from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify


# 🟩 Custom User Manager
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


# 🟦 Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    activation_date = models.DateTimeField(null=True, blank=True)

    ACCOUNT_TYPE_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('unlimited', 'Unlimited'),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='free')

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    # ✅ Profile Creation Limit Logic
    def can_create_profile(self):
        """
        Limit how many profiles a user can create based on account type.
        - Free: 1 profile
        - Premium: up to 10 profiles
        - Unlimited: no limit
        """
        profile_count = self.userprofile_set.count()

        if self.account_type == "unlimited":
            return True
        elif self.account_type == "premium":
            return profile_count < 10
        return profile_count < 1


# 🟨 User Profile Model
class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        # ✅ Auto-generate username if missing
        if not self.username and self.full_name:
            base = slugify(self.full_name.replace(" ", "_"))
            username = base
            count = 1
            while UserProfile.objects.filter(username=username).exclude(pk=self.pk).exists():
                username = f"{base}_{count}"
                count += 1
            self.username = username

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.user.email
