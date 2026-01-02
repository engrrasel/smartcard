from django.urls import path
from . import views

app_name = "app_jobs"

urlpatterns = [
    path("", views.career_dashboard, name="career_dashboard"),
    path(
        "request/<int:pk>/action/",
        views.employment_request_action,
        name="employment_request_action",
    ),
]
