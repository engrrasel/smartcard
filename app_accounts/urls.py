# app_accounts/urls.py
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "app_account"

urlpatterns = [
    # 🔐 Authentication
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='app_account:login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('email-sent/', lambda request: render(request, 'accounts/email_sent.html'), name='email_sent'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),

    # 🏠 Dashboard & Profiles
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/<int:pk>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<int:pk>/remove-picture/', views.remove_profile_picture, name='remove_profile_picture'),


    # 🌐 Public Profile
    path('<slug:username>/', views.public_profile, name='public_profile'),
]
