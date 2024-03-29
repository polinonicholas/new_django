from django.contrib import admin
from .models import Category
from project.apps.blog.models import Post
from mptt.admin import DraggableMPTTAdmin

class CategoryAdmin(DraggableMPTTAdmin):
    pass

admin.site.register(Category, CategoryAdmin )
admin.site.register(Post)