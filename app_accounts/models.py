# ======================================================
#  🔥 NEXT LEVEL TRACKING READY MODELS.PY (FINAL BUILD)
# ======================================================

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
import uuid


# ======================================================
#   USER CREATION MANAGER
# ======================================================
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

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# ======================================================
#   MAIN USER MODEL + NFC PUBLIC CARD
# ======================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    activation_date = models.DateTimeField(null=True, blank=True)

    # PRO/ELITE accounts can create team profiles
    parent_user = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="child_profiles"
    )

    ACCOUNT_TYPE_CHOICES = [
        ("starter", "Starter"),
        ("pro", "Pro"),
        ("elite", "Elite"),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default="starter")

    full_name = models.CharField(max_length=150, blank=True, null=True)
    username = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='default.png')

    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # 📊 PROFILE ANALYTICS
    daily_views = models.PositiveIntegerField(default=0)
    monthly_views = models.PositiveIntegerField(default=0)
    yearly_views = models.PositiveIntegerField(default=0)
    last_viewed = models.DateField(blank=True, null=True)

    save_count = models.PositiveIntegerField(default=0)   # ⭐ When someone saves contact

    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name or self.email

    # PUBLIC URL
    def get_absolute_url(self):
        if not self.username or self.username.startswith("deleted_"):
            return reverse("app_accounts:dashboard")
        return reverse("app_accounts:public_profile", args=[self.username])

    def get_permanent_url(self):
        return reverse("app_accounts:public_profile_by_id", args=[self.public_id])

    def can_create_profile(self):
        count = self.child_profiles.count()
        if self.account_type == "elite": return True
        if self.account_type == "pro": return count < 10
        return count < 0

    # AUTO-UNIQUE USERNAME GENERATOR
    def save(self, *args, **kwargs):
        if not self.username:
            base = slugify(self.full_name or self.email.split("@")[0])
            username = base or "user"
            counter = 1
            qs = CustomUser.objects.exclude(pk=self.pk) if self.pk else CustomUser.objects.all()
            while qs.filter(username=username).exists():
                username = f"{base}-{counter}" ; counter += 1
            self.username = username

        super().save(*args, **kwargs)



# ======================================================
#  NEXT LEVEL CONTACT SAVE TRACKER 🚀
# ======================================================
# ================== Visitor Save + Location Tracking ==================
class ContactSaveLead(models.Model):
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="visits")

    device_ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    thana = models.CharField(max_length=120, null=True, blank=True)
    post_office = models.CharField(max_length=120, null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
  # ← 🔥 MOST IMPORTANT

    timestamp = models.DateTimeField(auto_now_add=True)

    def location_label(self):
        if self.latitude and self.longitude:
            return f"📍 GPS({self.latitude}, {self.longitude})"
        if self.city or self.country:
            return f"🌍 {self.city or ''}, {self.country or ''}"
        return "❓ Unknown"

    def __str__(self):
        return f"{self.profile} [{self.location_label()}]"


# ================== Button Click Tracking ==================
class ClickEvent(models.Model):
    profile = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="clicks")

    button_type = models.CharField(max_length=50)  # connect, save, call, fb, insta...
    device_ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.username} → {self.button_type}"


