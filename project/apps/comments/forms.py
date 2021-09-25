from django import forms
from . models import Comment
from project.customized_classes import DivErrorList
from project.apps.blog.models import Post
from django_bleach.forms import BleachField
from markdownx.widgets import MarkdownxWidget

class CommentForm(forms.ModelForm):
	class Meta: 
		model = Comment
		fields = ['content']
		widgets = {'content': forms.Textarea(attrs={'rows': 4,
			'class': 'comment_content'})}
		labels = {'content': 'Leave a comment...'}
		error_class=DivErrorList

	# def __init__(self, *args, **kwargs):
	# 	pk = kwargs.get('pk')
	# 	super(CommentForm, self).__init__(*args, **kwargs)
	# 	self.fields['content'].widget.attrs.update({'placeholder':
	# 		f"Your thoughts on '{Post.objects.get(pk=pk).title}'..."})
