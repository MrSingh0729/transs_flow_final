# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value):
    return value.split()


@register.filter
def add_attr(value, arg):
    """Add attributes to form field based on condition"""
    try:
        attr, val = arg.split(':')
        if value.value():  # If field has a value, add the attribute
            return value.as_widget(attrs={attr: val})
    except:
        return value
    
@register.filter   
def endswith(value, arg):
    """Check if string ends with substring"""
    if isinstance(value, str):
        return value.endswith(arg)
    return False


@register.filter(name='attr')
def attr(field, arg):
    """Adds an HTML attribute to a form field."""
    attrs = {}
    if '=' in arg:
        key, val = arg.split('=', 1)
        attrs[key] = val
    else:
        attrs[arg] = True
    return field.as_widget(attrs=attrs)