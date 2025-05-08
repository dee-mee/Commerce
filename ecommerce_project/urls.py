"""
URL configuration for ecommerce_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    
    # Authentication URLs - using Django's built-in views
    path("login/", auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path("logout/", auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    
    # Custom auth app URLs
    path("", include("auth_app.urls")),
    
    # Other app URLs
    path("store/", include("store.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("payment/", include("payment.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("wishlist/", include("wishlist.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
