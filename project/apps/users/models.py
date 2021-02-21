from django.db import models
from PIL import Image
from django.utils import timezone
from . import variables
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from . managers import CustomUserManager

class User(AbstractUser):
	is_active = models.BooleanField(_('active'), default=True)
	email = models.EmailField(_('email address'), unique=True)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	image = models.ImageField(default=variables.random_image, 
		upload_to='profile_pics')
	bio = models.CharField(max_length=variables.MAX_BIO_LENGTH, blank=True, 
		null =True)
	joined = models.DateTimeField(default = timezone.now)

	objects = CustomUserManager()