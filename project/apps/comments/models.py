from django.db import models
from django.conf import settings
from django.utils import timezone
from project.apps.blog.models import Post
from django_bleach.models import BleachField

class Comment(models.Model):
	content = content = models.TextField()
	posted = models.DateField(auto_now_add=True)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)



	