from django.urls import path
from . views import CategoryListView
from project.apps.blog.views import PostsByCategoryView

urlpatterns = [
    path('', CategoryListView.as_view() , name='category-base'), 
    path('<str:slug>/', PostsByCategoryView.as_view() , name='category-detail'),
      
    ]