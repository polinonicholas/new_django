from django.urls import path
from games.views import ItemsByCategoryView, CategoryListView

urlpatterns = [
	// ...
    path('', CategoryListView.as_view() , name='category-list'),
    path('<str:slug>/', ItemsByCategoryView.as_view() , name='category-detail'),
    ]