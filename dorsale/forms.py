#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db import models
from django.forms import ModelForm
try:
    from coloree.fields import HtmlColorCodeField
    from coloree.widgets import ColorPickerWidget
    coloree_active = True
except ImportError:
    coloree_active = False
from widgets import DatePickerWidget

class DorsaleBaseModelForm(ModelForm):
    
    class Meta:
        #exclude = ['createdon','createdby','lastchangedon','lastchangedby','site','deleted',]
        pass

    def __init__(self, *args, **kwargs):
        """
        Required keyword parameter: `user` = current user
        """
        self.user = kwargs.pop('user', None)
        super(DorsaleBaseModelForm, self).__init__(*args, **kwargs)
        if 'group' in self.fields:
            self.fields['group'].queryset = Group.objects.filter(user=self.user)
    
    def save(self, commit=True):
        """
        Save our model and set creation/update user and date automatically.
        
        Beware, 'user' is an additional required keyword parameter in creation!
        """
        obj = super(DorsaleBaseModelForm, self).save(commit=False)
        if hasattr(obj, 'lastchangedby'): obj.lastchangedby = self.user
        if hasattr(obj, 'lastchangedon'): obj.lastchangedon = datetime.datetime.now()
        if hasattr(obj, 'site'): obj.site = Site.objects.get_current()
        if not obj.pk: # new dataset
            if hasattr(obj, 'createdby'): obj.createdby = self.user
            if hasattr(obj, 'createdon'): obj.createdon = datetime.datetime.now()
            if hasattr(obj, 'deleted'): obj.deleted = False
        if commit:
            obj.save()
            self.save_m2m()
        return obj
            
def ModelFormFactory(some_model, *args, **kwargs):
    """
    Create a ModelForm for `some_model`.
    
    `DateField` and `coloree.fields.HtmlColorCodeField` get their own widgets assigned,
    if there’s NO keyword argument 'disabled'.
    
    see also http://stackoverflow.com/questions/297383/dynamically-update-modelforms-meta-class
    """
    widdict = {}
    if not('disabled' in kwargs and kwargs['disabled']):
        # set some widgets for special fields
        for field in some_model._meta.local_fields:
            if type(field) is models.DateField:
                widdict[field.name] = DatePickerWidget()
            elif coloree_active and type(field) is HtmlColorCodeField:
                widdict[field.name] = ColorPickerWidget()
    try:
        del kwargs['disabled']
    except KeyError:
        pass
    
    class MyModelForm(DorsaleBaseModelForm):
        class Meta:
            model = some_model
            widgets = widdict

    return MyModelForm(*args, **kwargs)
