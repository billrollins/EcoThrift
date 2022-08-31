# templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter(name='dict_get')
def dict_get(d, k):
    '''Returns the given key from a dictionary.'''
    return d[k]