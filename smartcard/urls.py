from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True  # ✅ THIS LINE ADDED
        ),
        name='login'
    ),

    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # App URLs
    path('', include('app_accounts.urls')),   # ✅ Only this include needed
]

if settings.DEBUG:
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]