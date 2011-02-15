from django.db import models
from django.forms import fields
from validators import is_html_color_code
from widgets import ColorPickerWidget

class HtmlColorCodeField(models.CharField):
    """
    A CharField that checks that the value is a valid HTML color code (Hex triplet).
    Has no required argument. Uses `validators.is_html_color_code` for validation.
    
    Mix of several djangosnippets
    """
    def __init__(self, **kwargs):
        kwargs['max_length'] = 7
        #validator_list = kwargs.get('validator_list', [])
        #validator_list.append(HtmlColorCodeField.is_html_color_code)
        #kwargs['validator_list'] = validator_list
        super(HtmlColorCodeField,self).__init__(**kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(HtmlColorCodeField, self).formfield(**kwargs)
        
    def get_internal_type(self):
        return 'CharField'
    
    def validate(self, value, all_values):
        return is_html_color_code(value)

    def widget_attrs(self, widget):
        if isinstance(widget, (fields.TextInput)):
            return {'maxlength': str(7)}

try:
    # for South
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^dorsale\.colors\.fields\.HtmlColorCodeField"])
except ImportError:
    pass
