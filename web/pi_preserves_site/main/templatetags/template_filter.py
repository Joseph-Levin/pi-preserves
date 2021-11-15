from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def filenamesplit(value):
    """Converts a filepath to only the filename"""
    return value.split('/')[-1]