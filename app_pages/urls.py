from django.urls import path
from . import views

app_name = "app_pages"

urlpatterns = [
    path("", views.company_pages, name="company_pages"),
    path("company/id/<uuid:uid>/", views.company_public_by_uid, name="company_public_uid"),
    
    path("company/<slug:slug>/", views.company_public_by_slug, name="company_public_slug"),
    path("add-company/", views.add_company, name="add_company"),
    path("company/edit/<int:id>/", views.edit_company, name="edit_company"),



]