
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
"""customized error class for forms 
https://docs.djangoproject.com/en/3.1/ref/forms/api/#customizing-the-error-list-format
"""
class DivErrorList(ErrorList):
	def __str__(self):
		return self.as_divs()
	def as_divs(self):
		if not self: 
			return ''
		return mark_safe('<div class="errorlist">%s</div>' % ''\
		.join(['<div class="error">%s</div>' % e for e in self]))


