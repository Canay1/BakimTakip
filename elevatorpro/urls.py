from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),  # login/logout hazır gelir

    # Ana sayfa → dashboard'a yönlendir
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # Uygulama url'lerini dahil et
    path('', include('elevator.urls')),

    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
]