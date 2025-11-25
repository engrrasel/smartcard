from django.urls import path
from . import views

app_name = "app_contacts" 

urlpatterns = [
    path('', views.my_contacts, name='my_contacts'),
    path('connect/<int:user_id>/', views.add_contact, name='add_contact'),
    path('my-contacts/', views.my_contacts, name='my_contacts'),
    path('contact-profile/<int:user_id>/', views.contact_profile_db, name='contact_profile_db'),

    path('delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
]
