# models.py
# ======================================================
#  🔥 NEXT LEVEL TRACKING READY MODELS.PY (FINAL CLEAN BUILD)
# ======================================================

import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)

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

    # ========== TEAM PROFILE SUPPORT ==========
    parent_user = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="child_profiles"
    )

    ACCOUNT_TYPE_CHOICES = [
        ("starter", "Starter"),
        ("pro", "Pro"),
        ("elite", "Elite"),
    ]
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default="starter"
    )

    # ========== BASIC PROFILE ==========
    full_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        null=True,
        blank=True,
        default="default.png"
    )

    # ========== SOCIAL LINKS ==========
    facebook = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    # ========== PROFILE ANALYTICS ==========
    daily_views = models.PositiveIntegerField(default=0)
    monthly_views = models.PositiveIntegerField(default=0)
    yearly_views = models.PositiveIntegerField(default=0)
    last_viewed = models.DateField(null=True, blank=True)

    save_count = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # --------------------------------------------------
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
        if self.account_type == "elite":
            return True
        if self.account_type == "pro":
            return count < 10
        return count < 0  # starter cannot create any child

    # AUTO UNIQUE USERNAME
    def save(self, *args, **kwargs):
        if not self.username:
            base = slugify(self.full_name or self.email.split("@")[0])
            username = base or "user"

            counter = 1
            qs = CustomUser.objects.exclude(pk=self.pk) if self.pk else CustomUser.objects.all()

            while qs.filter(username=username).exists():
                username = f"{base}-{counter}"
                counter += 1

            self.username = username

        super().save(*args, **kwargs)


# ======================================================
#   NEXT LEVEL CONTACT SAVE TRACKER 🚀
# ======================================================
class ContactSaveLead(models.Model):
    profile = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="visits"
    )

    # Logged-in visitor (optional)
    visitor = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="visits_made",
        help_text="If the visitor was logged in"
    )

    # Device Info
    device_ip = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    user_agent = models.TextField(null=True, blank=True)

    # Coordinates
    latitude = models.FloatField(null=True, blank=True, db_index=True)
    longitude = models.FloatField(null=True, blank=True, db_index=True)

    # Location Details
    city = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    country = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    thana = models.CharField(max_length=120, null=True, blank=True)
    post_office = models.CharField(max_length=120, null=True, blank=True)

    # accuracy is stored as percent (0-100) — you may also store raw meters if needed later
    accuracy = models.IntegerField(null=True, blank=True)

    # LOCATION SOURCE
    location_source = models.CharField(
        max_length=5,
        choices=[("GPS", "GPS"), ("IP", "IP")],
        default="IP",
        db_index=True
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # --------------------------------------------------
    def location_label(self):
        if self.latitude and self.longitude:
            return f"📍 GPS({self.latitude}, {self.longitude})"
        if self.city or self.country:
            return f"🌍 {self.city or ''}, {self.country or ''}"
        return "❓ Unknown"

    def is_gps(self):
        """Return True when this record came from GPS and coords look valid."""
        try:
            return self.location_source == "GPS" and self.latitude is not None and self.longitude is not None
        except Exception:
            return False

    def visitor_display(self):
        """Return (name, avatar_url) tuple for quick template use."""
        if not self.visitor:
            return None, None
        name = self.visitor.full_name or self.visitor.email
        avatar = getattr(self.visitor.profile_picture, "url", None) or ""
        return name, avatar

    def __str__(self):
        return f"{self.profile} [{self.location_label()}]"

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["profile", "timestamp"]),
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
            models.Index(fields=["location_source"]),
        ]


# ======================================================
#   BUTTON CLICK TRACKER
# ======================================================
class ClickEvent(models.Model):
    profile = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="clicks"
    )

    button_type = models.CharField(max_length=50)  # connect, save, call, fb, insta...
    device_ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    # --------------------------------------------------
    def __str__(self):
        return f"{self.profile.username} → {self.button_type}"

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["profile", "timestamp"]),
        ]
