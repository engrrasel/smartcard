from django import forms
from django.utils.text import slugify
from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "slug",              # ✅ Company Username
            "business_type",
            "founded_year",
            "phone",
            "email",
            "website",
            "address",
            "description",
            "facebook_page",
            "map_location",
            "logo",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Company name"
            }),

            # ✅ Username field (slug)
            "slug": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "company-username",
                "autocomplete": "off"
            }),

            "business_type": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Business type"
            }),
            "founded_year": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Founded year"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Official email"
            }),
            "website": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://example.com"
            }),
            "address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Company address"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Short company description"
            }),
            "facebook_page": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "Facebook page URL"
            }),
            "map_location": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "Google map location link"
            }),

            # ✅ Logo (no Clear / no filename)
            "logo": forms.FileInput(attrs={
                "class": "d-none",
                "accept": "image/*"
            }),
        }

    # ==========================
    # ✅ SLUG VALIDATION LOGIC
    # ==========================
    def clean_slug(self):
        slug = self.cleaned_data.get("slug")

        # যদি user না লেখে → name থেকে auto generate
        if not slug:
            name = self.cleaned_data.get("name", "")
            slug = slugify(name)

        # uniqueness check (edit mode safe)
        qs = Company.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "This company username is already taken."
            )

        return slug
