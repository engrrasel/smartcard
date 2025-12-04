from django.urls import path
from . import views

app_name = "app_pages"

urlpatterns = [
    path("", views.company_pages, name="company_pages"),
]
