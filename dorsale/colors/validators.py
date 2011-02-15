import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def is_html_color_code(field_data):
    """
    Checks that field_data is a HTML color code string.
    """
    try:
        if len(field_data) not in (4,7) or not re.match('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', field_data):
            raise ValidationError(_(u'This is an invalid color code. It must be a html hex color code e.g. #000000'))
    except (TypeError, ValueError), e:
        raise ValidationError, str(e)
    return True

def is_cmyk_color_code(field_data):
    """
    Checks if a CommaSeparatedIntegerField contains a valid CMYK code (e.g. "0,100,100,0")
    """
    try:
        parts = field_data.split(',')
        if not len(field_data) in range(7,16) \
        or len(parts)<>4 \
        or not re.match('^(\d{1,3},){3}\d{1,3}$', field_data):
            raise ValidationError(_(u'This is not a valid CMYK color code. Please use percent values e.g. 0,100,100,0'))
        parts = map(lambda x: int(x), parts)
        if max(parts)>100 or min(parts)<0:
            raise ValidationError(_(u'This is not a valid CMYK color code. Please use percent values e.g. 0,100,100,0'))
    except (TypeError, ValueError), e:
        raise ValidationError(e)
    return True
