from django.urls import path
from . import views

app_name = "app_contacts"

urlpatterns = [

    # Contacts Home
    path('', views.my_contacts, name='my_contacts'),

    # Contact Dashboard Pages
    path("dashboard/", views.contact_dashboard, name="contact_dashboard"),
    path("all-connects/", views.all_connects, name="all_connects"),
    path("request/", views.request_view, name="contact_request"),
    path("pending-request/", views.pending_request, name="pending_request"),

    # Contact Actions
    path("add/<int:user_id>/", views.add_contact, name="add_contact"),
    path("contact-profile/<int:user_id>/", views.contact_profile_db, name="contact_profile_db"),
    path("delete/<int:contact_id>/", views.delete_contact, name="delete_contact"),

    # Contact Preview Page
    path("connect/<int:id>/", views.my_connects_db, name="my_connects_db"),

    # Request System
    path("requests/", views.request_view, name="request_view"),
    path("accept/<int:id>/", views.accept_request, name="accept_request"),
    path("reject/<int:id>/", views.reject_request, name="reject_request"),

    # Notes System
    path("save-note/<int:contact_id>/", views.save_note, name="save_note"),
    path("notes/<int:contact_id>/", views.show_notes, name="show_notes"),
    path("get-last-note/<int:contact_id>/", views.get_last_note, name="get_last_note"),

    # Live Interaction Tracking
    path("track/<int:contact_id>/<str:action>/", views.track_action, name="track_action"),

]
