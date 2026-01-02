from django.urls import path
from . import views

app_name = "app_pages"

urlpatterns = [

    # =========================
    # ✅ Company Pages (Owner)
    # =========================
    path("", views.company_pages, name="company_pages"),

    path(
        "company/id/<uuid:uid>/",
        views.company_public_by_uid,
        name="company_public_uid"
    ),
    path(
        "company/<slug:slug>/",
        views.company_public_by_slug,
        name="company_public_slug"
    ),

    path("add-company/", views.add_company, name="add_company"),
    path("company/edit/<int:id>/", views.edit_company, name="edit_company"),


    # =========================
    # ✅ Employee System (Owner)
    # =========================
    path("employee/", views.employee_hub, name="employee_hub"),
    path(
        "employee/send-request/<int:user_id>/",
        views.send_join_request,
        name="send_join_request"
    ),
    path(
        "employee/approve/<int:request_id>/",
        views.approve_join_request,
        name="approve_join_request"
    ),
    path(
        "employee/remove/<int:employee_id>/",
        views.remove_employee,
        name="remove_employee"
    ),

        path("products/", views.company_products, name="products"),
        path("recruitment/", views.recruitment_dashboard, name="recruitment"),


    path(
        "employee/live-search/",
        views.employee_live_search,
        name="employee_live_search"
    ),

    path("company/<int:company_id>/manage/",
         views.company_manage,
         name="company_manage"),

    path("company/<int:company_id>/deactivate/",
         views.company_deactivate,
         name="company_deactivate"),

]
