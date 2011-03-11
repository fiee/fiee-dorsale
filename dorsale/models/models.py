#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import types
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models, router
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.db.models.query_utils import CollectedObjects, CyclicDependency
from django.utils.translation import ugettext_lazy as _
#from south.modelsinspector import add_introspection_rules
from dorsale.conf import settings
from managers import DorsaleSiteManager, DorsaleGroupSiteManager

class DorsaleBaseModel(models.Model):
    """
    Abstract base class for all fiee models.
    
    Provides ...
    
    1) automatic administrations fields:
    
       :createdby: auth.User 
            user that created the object
       :lastchangedby:  auth.User
            last user that changed the object
       :createdon: datetime 
            date of creation
       :lastchangedon: datetime
            date of last change
       :deleted: bool
            you can't delete our objects any more, they just get marked as deleted
       :site:
            Site this object belongs to
    
    2) additional meta info methods/properties for generic view:
    
       :field_info: dict
            dict of fields, independent of `list_display` and thus without methods
       :fields(): generator
            list of fields, influenced by `list_display`
       :fieldnames_verbose(): generator
            list of translated names of editable fields, influenced by `list_display`
       :fieldnames(): list 
            list of raw names of editable fields or `list_display`
       :fieldvalues(): generator
            list of field values, influenced by `list_display`
       :classname(): unicode
            translated class name
       :classname_plural(): unicode
            translated plural class name
       :get_absolute_url(): str
            '/module/model/id/' (doesn't work?)
       :items_per_page: int (r/w)
            number of items on one list view page (default: 10 or `settings.ITEMS_PER_PAGE`)
       :list_display: list
            list of field names that should be used for generic list views (default: empty and thus ignored)
            used by fields(), fieldnames(), fieldnames_verbose() and fieldvalues()
       
    3) changed/additional manager methods:
    
       :objects: `DorsaleSiteManager`
            returning only not-deleted objects of the current site
       :really_all_objects: `models.Manager`
            former default manager, returning all objects
    """
    createdby = models.ForeignKey(User, 
                    verbose_name=_('created by'), 
                    related_name="%(app_label)s_%(class)s_createdset", 
                    editable=False, 
                    default=settings.ANONYMOUS_USER_ID, 
                    help_text=_(u'user that was logged in when this item was created')
                    )
    createdon = models.DateTimeField(
                    verbose_name=_(u'created on'), 
                    null=True, editable=False, 
                    help_text=_(u'date and time when this item was created')
                    )
    lastchangedby = models.ForeignKey(User, 
                    verbose_name=_('last changed by'), 
                    related_name="%(app_label)s_%(class)s_changedset", 
                    editable=False, 
                    default=settings.ANONYMOUS_USER_ID, 
                    help_text=_(u'user that was logged in when this item was changed last time')
                    )
    deleted = models.BooleanField(
                    verbose_name=_('deleted?'), 
                    editable=False, 
                    default=False, 
                    help_text=_(u'Is this item marked as deleted?')
                    )
    lastchangedon = models.DateTimeField(
                    verbose_name=_(u'last changed on'), 
                    null=True, editable=False, 
                    help_text=_(u'date and time when this item was changed last time')
                    )
    site = models.ForeignKey(Site, 
                    verbose_name=_(u'tenant’s site'), 
                    editable=False, 
                    default=settings.SITE_ID, 
                    help_text=_(u'site of the related customer/project/team')
                    )
     
    really_all_objects = models.Manager()
    # objects = models.Manager() must come before any other manager, if admin should see *all* objects
    objects = DorsaleSiteManager()
    
    items_per_page = int(getattr(settings, 'ITEMS_PER_PAGE', 10)) #: used in list views, overwrite in your models
    list_display = [] #: for list views, ignore if empty
    
    class Meta:
        abstract = True
        #permissions = [
        #    ('view_item', _(u'Can view item')),
        #]
        
    def save(self, *args, **kwargs):
        """
        Automatically save time of creation and change;
        can’t save the user, you must do that in your view
        (or use dorsale’s generic views)
        """
        if not self.id:
            self.createdon = datetime.datetime.now()
        self.lastchangedon = datetime.datetime.now()
        if 'site' in kwargs:
            self.site = kwargs['site']
            del kwargs['site']
        else:
            self.site = Site.objects.get_current()
        super(DorsaleBaseModel, self).save(*args, **kwargs)

    def original_save(self, *args, **kwargs):
        """
        original save method, for cases where there’s no current Site, like in celery tasks
        """
        super(DorsaleBaseModel, self).save(*args, **kwargs)
        
    def delete(self, using=None, *args, **kwargs):
        """
        mark this instance as deleted and call delete() on all related objects
        """
        self.deleted = True
        self.save(*args, **kwargs)
        
        # the following is copied from django.db.models.base.Model
        
        using = using or router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)

        # Find all the related objects than need to be deleted.
        seen_objs = CollectedObjects()
        self._collect_sub_objects(seen_objs)
        
        # the following is copied from django.db.models.query.delete_objects()
        
        try:
            ordered_classes = seen_objs.keys()
        except CyclicDependency:
            # If there is a cyclic dependency, we cannot in general delete the
            # objects.  However, if an appropriate transaction is set up, or if the
            # database is lax enough, it will succeed. So for now, we go ahead and
            # try anyway.
            ordered_classes = seen_objs.unordered_keys()

        for cls in ordered_classes:
            items = seen_objs[cls].items()
            for no, ob in items:
                if not ob is self:
                    ob.delete()
        
        #for related in self._meta.get_all_related_objects():
        #    for o in related.model.objects.all(): # ALL objects?? couldn't find appropriate filter
        #        o.delete()
    
    def field_info(self):
        """
        dictionary of the model’s fields (independent of `list_display`, thus without methods)
        """
        try:
            return self._field_info
        except:
            self._field_info = {}
            for n in self._meta.fields:
                if hasattr(n, 'name'):
                    self._field_info[n.name] = n
            return self._field_info
    
    def fields(self):
        """
        generator of the model’s (editable) fields, as defined by its `list_display` attribute
        """
        if self.list_display:
            for n in self.list_display:
                if n in self.field_info():
                    yield self.field_info()[n]
                else:
                    yield getattr(self, n, '')
        else:
            for n in self._meta.fields:
                if not n.editable: continue
                yield n
    
    def fieldnames_verbose(self):
        """
        generator of verbose (translated) names of the model’s fields, as defined by its `list_display` attribute
        """
        if self.list_display:
            for n in self.list_display:
                r = self.getattr(n)
                if hasattr(r, 'verbose_name'):
                    r = r.verbose_name
                yield r
        else:
            for f in self._meta.fields:
                if not f.editable: continue
                yield f.verbose_name
    
    def fieldnames(self):
        """
        list of raw names of the model’s fields, as defined by its `list_display` attribute
        """
        if self.list_display:
            return self.list_display
        return [f.name for f in self._meta.fields if f.editable]
    
    def fieldvalues(self):
        """
        generator of the instance’s field (or method) values, dependent of `fieldnames`
        """
        for f in self.fieldnames():
            r = getattr(self, f)
            if type(r) is types.MethodType:
                r = r()
            yield r
        #return (getattr(self, f) for f in self.fieldnames())
    
    def classname(self):
        """
        verbose (translated) name of this model
        """
        return self._meta.verbose_name
    
    def classname_plural(self):
        """
        verbose (translated) plural name of this model
        """
        return self._meta.verbose_name_plural
    
    @models.permalink
    def get_absolute_url(self):
        """
        link to dorsale’s generic `show_item` view
        """
        mo = ContentType.model_class(self)
        #return '/%s/%s/%d/' % (mo.app_label, mo.model, self.id)
        return ('dorsale.views.show_item', (), {
            'app_name'  : mo.app_label,
            'model_name': mo.model,
            'object_id' : self.id,
        })

