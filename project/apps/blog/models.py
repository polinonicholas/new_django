from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from mptt.models import TreeForeignKey

class Post(models.Model):
	title = models.CharField(max_length = settings.MAX_TITLE_LENGTH)
	content = models.TextField()
	date_posted = models.DateTimeField(default = timezone.now)
	author = models.ForeignKey(User, on_delete= models.CASCADE)
	category = TreeForeignKey('categories.Category', on_delete=models.CASCADE)
	slug = models.SlugField(max_length=settings.MAX_TITLE_LENGTH, null=True, 
    blank=True,)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('post-detail', kwargs ={ 'pk':self.pk,
			'slug': self.slug,})



	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super(Post, self).save(*args, **kwargs)
		
	# def get_slug(self):
	# 	return self.slug