from __future__ import unicode_literals
from django import template
import logging
logger = logging.getLogger(__name__)
register = template.Library()

@register.simple_tag
def orderby(fieldname, request_ordering):
    """check if the fieldname is in request_ordering and then revert it"""
    request_ordering = list(request_ordering)
    ordering = []
    for ro_field in request_ordering:
        if fieldname in ro_field:
            minus = '-'+fieldname
            try:
                if minus in ro_field:
                    ordering.append(ro_field.replace(minus, fieldname))
                else:
                    ordering.append(ro_field.replace(fieldname, '-'+fieldname))
            except AttributeError as ex:
                logger.error('field name "%s" should be a string, but is a %s' % (ro_field, type(ro_field)))
                logger.exception(ex)
        else:
            ordering.append(fieldname)
    return ','.join(ordering)
