from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from dorsale.tools import assert_on_exception

class ColorPickerWidget(forms.TextInput):
    """
    Simple HTML RGB color input using jquery.colorPicker
    
    see also
    http://djangosnippets.org/snippets/1261/
    http://www.web2media.net/laktek/2008/10/27/really-simple-color-picker-in-jquery/
    http://github.com/laktek/really-simple-color-picker
    """
    input_type = 'color' # HTML 5, Opera only
    
    class Media:
        extend = True
        css = {
            'all': (
                settings.MEDIA_URL + 'colorpicker/colorPicker.css',
            )
        }
        js = (
            #'http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js',
            settings.MEDIA_URL + 'colorpicker/jquery.colorPicker.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ColorPickerWidget, self).__init__(attrs=attrs)

    @assert_on_exception
    def render(self, name, value, attrs=None):
        rendered = super(ColorPickerWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            $(function() {
            $('#id_%s').colorPicker();
            });
            </script>''' % name)
