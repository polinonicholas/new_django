from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from . models import Post
from project.apps.categories.models import Category

admin.site.unregister(Post)
@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
	list_display = ('title','author','category')
	search_fields = ('title',)
	def save_model(self, request, obj, form, change):
		if not obj.author:
			obj.author = request.user
		if not obj.category:
			obj.category = Category.objects.get(name='Random')
		super().save_model(request, obj, form, change)