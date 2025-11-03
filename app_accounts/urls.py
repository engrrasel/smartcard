from django.urls import path
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "app_accounts"  # ✅ এই নামটা সব জায়গায় consistent রাখো

urlpatterns = [
    # 🔐 Authentication
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='app_accounts:login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('email-sent/', lambda request: render(request, 'accounts/email_sent.html'), name='email_sent'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),

    # 🏠 Dashboard & Profiles
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/<int:pk>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:pk>/remove-picture/', views.remove_profile_picture, name='remove_profile_picture'),

    # 🆕 Profile Dashboard Page
    path('profile-dashboard/', views.profile_dashboard, name='profile_dashboard'),

    # 🌐 Public Profile
    path('<slug:username>/', views.public_profile, name='public_profile'),

    # 🧾 QR / Delete
    path('profile/<int:pk>/download_qr/', views.download_qr, name='download_qr'),
    path('profile/<int:pk>/delete/', views.delete_profile, name='delete_profile'),

    # 🧍‍♂️ Additional Pages (to be added soon)
    path('contacts/', views.contacts, name='contacts'),
    path('subscription/', views.subscription, name='subscription'),
    path('settings/', views.settings, name='settings'),
]
