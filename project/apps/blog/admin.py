from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from . models import Post

admin.site.unregister(Post)
@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
	list_display = ('title',)
	search_fields = ('title',)