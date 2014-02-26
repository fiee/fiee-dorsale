from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from dorsale.tools import assert_on_exception
        
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
    
    @assert_on_exception    
    def render(self, name, value, attrs=None):
        rendered = super(DatePickerWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
        $(function(){$('#id_%s').datepicker({ dateFormat: 'yy-mm-dd' });});
        </script>''' % (name))  # $.datepicker.regional['%s'] // , self.language
