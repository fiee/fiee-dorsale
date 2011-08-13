#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db import models
from django.forms import ModelForm
from colors.fields import HtmlColorCodeField
from colors.widgets import ColorPickerWidget
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
        obj.lastchangedby = self.user
        obj.lastchangedon = datetime.datetime.now()
        obj.site = Site.objects.get_current()
        if not obj.pk: # new dataset
            obj.createdby = self.user
            obj.createdon = datetime.datetime.now()
            obj.deleted = False
        if commit:
            obj.save()
            self.save_m2m()
        return obj
            
def ModelFormFactory(some_model, *args, **kwargs):
    """
    Create a ModelForm for some_model
    
    DateField and dorsale’s HtmlColorCodeField get their own widgets assigned,
    if there’s NO keyword argument 'disabled'.
    
    see also http://stackoverflow.com/questions/297383/dynamically-update-modelforms-meta-class
    """
    widdict = {}
    if not('disabled' in kwargs and kwargs['disabled']):
        # set some widgets for special fields
        for field in some_model._meta.local_fields:
            if type(field) is models.DateField:
                widdict[field.name] = DatePickerWidget()
            elif type(field) is HtmlColorCodeField:
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
