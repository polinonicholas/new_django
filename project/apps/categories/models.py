from django.conf import settings
from . import variables
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
  name = models.CharField(max_length=variables.MAX_CATEGORY_LENGTH, unique=True,)
  parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, 
    blank=True, related_name='children',)
  slug = models.SlugField(max_length=variables.MAX_CATEGORY_LENGTH, null=True, 
    blank=True,)
  description = models.TextField(max_length=settings.MAX_DESCRIPTION_LENGTH, 
  	null=True, blank=True,)
  
  class MPTTMeta:
    order_insertion_by = ['name']

  class Meta:
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name, allow_unicode=False)
    super().save(*args, **kwargs)

  def get_absolute_url(self):
    return reverse('category-detail', kwargs ={ 'slug': self.slug, })

