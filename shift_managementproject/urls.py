from django.conf import settings
from django.conf.urls.static import static

# from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import path, include
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shift.urls')),
    path('accounts/', include('accounts.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
