from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from . models import Post
from project.apps.categories.models import Category
from project.apps.comments.models import Comment
from project.apps.comments.variables import render_comment_text
from project.apps.comments.forms import CommentForm
# from django.utils.decorators import method_decorator # NEW
# from django.views.decorators.cache import cache_page # NEW
# @method_decorator(cache_page(60 * 5), name='dispatch') # NEW
class PostListView(ListView):
	model = Post
	template_name = 'blog/blog_base.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 15

class PostsByCategoryView(ListView):
	ordering = 'id'
	paginate_by = 10
	template_name = 'categories/category_base.html'
	context_object_name = 'posts'
	def get_queryset(self):
		# https://docs.djangoproject.com/en/3.1/topics/class-based-views/generic-display/#dynamic-filtering
		# the following category will also be added to the context data
		# self.category = Category.objects.get(slug=self.kwargs['slug'])
		# queryset = Post.objects.filter(category=self.category)
		self.category_name = Category.objects.get(url=self.kwargs['url'])
		self.category = Category.objects.get(url=self.kwargs['url']).get_descendants(include_self=True)
		queryset = Post.objects.filter(category__in=self.category)
		# need to set ordering to get consistent pagination results
		queryset = queryset.order_by(self.ordering)
		return queryset
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['category'] = self.category_name
		return context


class PostDetailView(DetailView):
	model = Post
	context_object_name = 'post'
	template_name = 'blog/blog_detail.html'
	form_class = CommentForm
	def get(request, self, pk, slug, *args, **kwargs):
		page = get_object_or_404(Post, pk=pk)
		resp = super().get(request, *args, **kwargs)
		if page.slug != slug:
			return redirect(page)
		return resp
	def post(self, request, pk, slug):
		self.page = Post.objects.get(pk=pk)
		form = self.form_class(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = self.page
			comment.author = request.user
			comment.content = render_comment_text(comment.content)
			comment.save()
			return redirect(self.page)
		return render(request, self.template_name, {'form': self.form_class})
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['comments'] = Comment.objects.filter(post=self.object)
		context['form'] = CommentForm()
		return context
	# def get_form_kwargs(self):
	# 	kwargs = super(PostDetailView,self).get_form_kwargs()
	# 	kwargs.update(self.kwargs)
	# 	return kwargs
	
	





	





	



