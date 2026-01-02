# smartcard/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 🧩 Django Admin
    path('admin/', admin.site.urls),

    # 📇 Contacts
    path('contacts/', include('app_contacts.urls')),

    # 🏢 Company Pages
    path("pages/", include("app_pages.urls")),

    # 💼 Jobs & Career  ✅ ADD THIS
    path("jobs/", include("app_jobs.urls")),

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

    # 🌐 Accounts (Dashboard, Profile, etc.)
    path('', include(('app_accounts.urls', 'app_account'), namespace='app_account')),

    # ⚙️ Settings
    path('settings/', include('app_settings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
