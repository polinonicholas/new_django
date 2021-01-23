# from django.shortcuts import render
from django.views.generic import ListView
from .models import Category


class CategoryListView(ListView):
    model = Category
    template_name = "categories/category_base.html"



