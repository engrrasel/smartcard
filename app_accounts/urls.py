from django.urls import path
from .views import (
    signup_view, activate_account, email_sent,
    dashboard, edit_profile, remove_profile_picture
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('email-sent/', email_sent, name='email_sent'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),

    path('dashboard/', dashboard, name='dashboard'),

    # ✅ Profile Routes
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/remove-picture/', remove_profile_picture, name='remove_profile_picture'),
]
