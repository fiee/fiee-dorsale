from django import template

register = template.Library()

@register.simple_tag
def orderby(fieldname, request_ordering):
    """check if the fieldname is in request_ordering and then revert it"""
    if fieldname in request_ordering:
        minus = '-'+fieldname
        if minus in request_ordering:
            ordering = request_ordering.replace(minus, fieldname)
        else:
            ordering = request_ordering.replace(fieldname, '-'+fieldname)
    else:
        ordering = fieldname
    return ordering
