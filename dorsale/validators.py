import re
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
    
def is_year(year):
    """Check that `year` is a year between 1900 and 2100, otherwise raise ValidationError."""
    try:
        year = int(year)
        if not year in range(1900, 2100):
            raise ValidationError(_(u'This is not a valid year (between 1900 and 2100).'))
    except (TypeError, ValueError), e:
        raise ValidationError, str(e)
    return True
    
def is_page_range(pages):
    """Check if `pages` is a valid page range of a printed product (divisible by 4), otherwise raise ValidationError."""
    if not pages: return
    try:
        pages = int(pages)
        if (pages % 4):
            raise ValidationError(_(u'This is not a valid page range (divisible by 4).'))
    except (TypeError, ValueError), e:
        raise ValidationError, str(e)
    return True
