from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name", "business_type", "founded_year",
            "phone", "email", "website",
            "address", "description",
            "facebook_page", "map_location",
            "logo"
        ]
