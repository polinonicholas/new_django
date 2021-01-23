from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from project.apps.users.views import register, profile, email_confirmation, validate_registration, EmailLoginView
from django.contrib.auth.views import (LoginView, 
PasswordResetCompleteView, PasswordResetDoneView, PasswordResetConfirmView, 
PasswordResetView, LogoutView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project.apps.blog.urls')),
    path('ajax/validate_registration/', validate_registration, name='validate_registration'),
    path('categories/', include('project.apps.categories.urls')),
    path('register/', register, name ='register'),
    path('profile/', profile, name ='profile'),
    path('login/', EmailLoginView.as_view(template_name ='users/login.html'), name ='login'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name ='users/password_reset_complete.html'), name ='password_reset_complete'),
    path('password_reset_done/', PasswordResetDoneView.as_view(template_name ='users/password_reset_done.html'), name ='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name ='users/password_reset_confirm.html'), name ='password_reset_confirm'),
    path('password-reset/', PasswordResetView.as_view(template_name ='users/password_reset.html'), name ='password_reset'),
    path('logout/', LogoutView.as_view(template_name ='users/logout.html'), name ='logout'),
    path('activate/<uidb64>/<token>/',email_confirmation, name='email_confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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