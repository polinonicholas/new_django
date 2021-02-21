from django.conf import settings
from . import variables
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from collections import deque

class Category(MPTTModel):
  name = models.CharField(max_length=variables.MAX_CATEGORY_LENGTH, unique=True,)
  parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, 
    blank=True, related_name='children',)
  slug = models.SlugField(max_length=variables.MAX_CATEGORY_LENGTH, null=True, 
    blank=True,)
  description = models.TextField(max_length=settings.MAX_DESCRIPTION_LENGTH, 
  	null=True, blank=True,)
  url = models.CharField(max_length=255, blank=True)
  
  class MPTTMeta:
    order_insertion_by = ['name']

  class Meta:
    verbose_name_plural = 'Categories'

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    orig_url = self.url
    d = deque([slugify(self.name, allow_unicode=False)])
    if self.parent:
      qs = list(self.parent.get_ancestors(include_self=True))
      data = [cat.name for cat in qs]
      for cat in reversed(data):
        d.appendleft(slugify(cat, allow_unicode=False))
    self.slug = slugify(list(d), allow_unicode=False)
    self.url = '/'.join(list(d))
    super().save(*args, **kwargs)
    if orig_url != self.url:
      for child in self.get_children():
        child.save()
  def get_absolute_url(self):
    return reverse('category-detail', kwargs ={ 'url': self.url, })
