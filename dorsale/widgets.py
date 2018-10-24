from __future__ import absolute_import
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class DatePickerWidget(forms.TextInput):
    """
    Simple pop-up calendar using jquery.datepicker
    """
#    class Media:
#        extend = True
#        css = {}
#        js = {}

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(DatePickerWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(DatePickerWidget, self).render(name, value, attrs)
        return rendered + mark_safe('''<script type="text/javascript">
        $(function(){$('#id_%s').datepicker({ dateFormat: 'yy-mm-dd' });});
        </script>''' % (name))  # $.datepicker.regional['%s'] // , self.language
