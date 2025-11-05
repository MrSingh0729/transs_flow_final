from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    return form[field_name]


@register.filter(name='add_attr')
def add_attr(field, attr):
    attrs = attr.split(':')
    return field.as_widget(attrs={attrs[0]: attrs[1]})