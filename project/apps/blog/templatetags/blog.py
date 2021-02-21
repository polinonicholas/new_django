from django import template
from django.template.defaultfilters import stringfilter
from markdownx.utils import markdownify


register = template.Library()

@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]
upto.is_safe = True

@register.filter
def markdown(value):
        return markdownify(value)
markdown.is_safe = True

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)