# smartcard/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    # 🧩 Django Admin
    path('admin/', admin.site.urls),
    
    path('contacts/', include('app_contacts.urls')),


    # 🔐 Authentication
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='app_account:login'),
        name='logout'
    ),

    # 🌐 Main App URLs (namespace সহ)
    path('', include(('app_accounts.urls', 'app_account'), namespace='app_account')),
    path('settings/', include('app_settings.urls')),

]
# 🖼️ Media files serve (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
