from django.urls import path
from . views import PostListView, PostDetailView

urlpatterns = [
    path('', PostListView.as_view(), name='blog-base'),
    path('<int:pk>/<str:slug>/', PostDetailView.as_view(), name='post-detail'),
    
    
]

# def get_absolute_url(self):
# 		return reverse('post_detail', kwargs ={ 'slug': self.slug, 
# 			'pk':self.pk})


#blog/post_list.html
#<app>/<model>_<viewtype>.html
