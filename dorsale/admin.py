# -*- coding: utf-8 -*-
import datetime
from django.contrib import admin
from django.contrib.sites.models import Site

class DorsaleBaseAdmin(admin.ModelAdmin):
    """
    ModelAdmin for DorsaleBaseModels, automaticalls sets createdby, 
    createdon, lastchangedby, lastchangedon, site and deleted fields.
    
    Beware, this overrides "queryset" and "has_change_permissions"!
    
    TODO: Permissions
    
    TODO: see http://www.stereoplex.com/blog/filtering-dropdown-lists-in-the-django-admin
    """
    def save_model(self, request, obj, form, change):
        if not change:
            if hasattr(obj, 'createdby'): obj.createdby = request.user
            if hasattr(obj, 'createdon'): obj.createdon = datetime.datetime.now()
            if hasattr(obj, 'deleted'): obj.deleted = False
        if hasattr(obj, 'site'): obj.site = Site.objects.get_current()  # we could allow superusers to change the site
        if hasattr(obj, 'lastchangedby'): obj.lastchangedby = request.user
        if hasattr(obj, 'lastchangedon'): obj.lastchangedon = datetime.datetime.now()
        obj.save()

    def queryset(self, request):
        # TODO: query (group) permissions
        qs = self.model._default_manager.get_query_set()
        ordering = self.ordering or ()
        if not request.user.is_superuser and hasattr(self.model, 'createdby'):
            qs = qs.filter(createdby=request.user)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def has_class_permission(self, request, obj=None):
        return super(DorsaleBaseAdmin, self).has_change_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        if not self.has_class_permission(request, obj):
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.createdby_id:  # if hasattr(obj, 'createdby'): 
            # TODO: Permissions!
            return False
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

try:
    from registration.models import RegistrationProfile
    # RegistrationProfile should not show up in admin
    admin.site.unregister(RegistrationProfile)
except:
    pass
    # print "registration was activated before dorsale!"
