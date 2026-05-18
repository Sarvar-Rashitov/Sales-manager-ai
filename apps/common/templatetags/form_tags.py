"""
Custom template tags/filters for forms and general use.
"""
from django import template

register = template.Library()


@register.filter
def getitem(obj, key):
    """Template'da dict yoki form field'ga nom bilan kirish uchun.
    Usage: {{ form|getitem:"field_name" }}
    """
    try:
        return obj[key]
    except (KeyError, TypeError):
        return ""


@register.filter
def split(value, delimiter=","):
    """String'ni bo'lish uchun.
    Usage: {{ "a,b,c"|split:"," }}
    """
    return [v.strip() for v in value.split(delimiter)]
