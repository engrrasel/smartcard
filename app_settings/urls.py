from django.urls import path
from . import views

app_name = "app_settings"

urlpatterns = [
    path('', views.settings_home, name="settings_home"),   # ← গুরুত্বপূর্ণ
    path('profile/', views.profile_settings, name="profile_settings"),
    path('email/', views.email_update, name="email_update"),
    path('phone/', views.phone_update, name="phone_update"),
    path('password/', views.password_change, name="password_change"),
]
