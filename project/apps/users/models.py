from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from . import variables
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django import forms
# from django.contrib.auth.base_user import BaseUserManager

class User(AbstractUser):
	is_active = models.BooleanField(_('active'), default=True)
	email = models.EmailField(_('email address'), unique=True)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	image = models.ImageField(default=variables.random_image, 
		upload_to='profile_pics')
	bio = models.CharField(max_length=variables.MAX_BIO_LENGTH, blank=True, 
		null =True)

	# objects = UserManager()
	# class UserManager(BaseUserManager)


	








	
    
    