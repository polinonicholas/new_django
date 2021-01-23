from django.urls import path
from .views import register, profile, validate_username

urlpatterns = [path('', validate_username, 
	name='validate_username' )
]

# url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),