from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from . import variables

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default=variables.random_image, 
		upload_to='profile_pics')
	bio = models.CharField(max_length =variables.MAX_BIO_LENGTH, blank=True, 
		null =True)
	# activation_key = models.CharField(max_length=40)
	# key_expires = models.DateTimeField()

	def __str__(self):
		return f'{self.user.username} Profile'

	
	








	
    
    