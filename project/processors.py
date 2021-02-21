from project.apps.categories.models import Category
from django.db.models import Count

def all_categories(request):
	return {'all_categories': Category.objects.all()}