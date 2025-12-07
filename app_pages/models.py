from django.db import models
from django.utils.text import slugify
import uuid

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
