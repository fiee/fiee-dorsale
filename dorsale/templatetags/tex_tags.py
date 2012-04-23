from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

reTeXSpecials = re.compile(r'([&%|{}~\$\[\]])', re.I|re.M)

@stringfilter
def texquote(input):
    """Quote TeX characters"""
    return reTeXSpecials.sub(r'\\\1{}', input)

register.filter('texquote', texquote)

@stringfilter
def texlines(input):
    """convert \\n to \\crlf"""
    return input.replace('\n', '\\crlf\n')

register.filter('texlines', texlines)
