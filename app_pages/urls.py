from django.urls import path
from . import views

app_name = "app_pages"

urlpatterns = [
    path("", views.company_pages, name="company_pages"),
    path("company/id/<uuid:uid>/", views.company_public_by_uid, name="company_public_uid"),
    
    path("company/<slug:slug>/", views.company_public_by_slug, name="company_public_slug"),
    path("add-company/", views.add_company, name="add_company"),
    path("company/edit/<int:id>/", views.edit_company, name="edit_company"),

    path("employee/", views.employee_hub, name="employee_hub"),
    path("employee/send-request/<int:user_id>/", views.send_join_request, name="send_join_request"),
    path("employee/approve/<int:request_id>/", views.approve_join_request, name="approve_join_request"),
    path("jobs/", views.job_list, name="job_list"),

    path("jobs/", views.job_list, name="job_list"),
    path("jobs/accept/<int:request_id>/", views.accept_join_request, name="accept_join_request"),
    path("jobs/reject/<int:request_id>/", views.reject_join_request, name="reject_join_request"),
    path("employee/remove/<int:employee_id>/", views.remove_employee, name="remove_employee"),



]