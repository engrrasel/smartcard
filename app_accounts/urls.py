from django.urls import path
from django.shortcuts import render
from .views import (
    signup_view,
    activate_account,
    dashboard,
    edit_profile,
    remove_profile_picture,
    public_profile,
)
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('signup/', signup_view, name='signup'),
    path('email-sent/', lambda request: render(request, 'accounts/email_sent.html'), name='email_sent'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/remove-picture/', remove_profile_picture, name='remove_profile_picture'),
    path('<slug:username>/', public_profile, name='public_profile'),
]
