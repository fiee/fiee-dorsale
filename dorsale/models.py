#!/usr/bin/env python
# -*- coding: utf-8 -*-
import types
from operator import attrgetter
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models, router, transaction
from django.db.models import signals, sql
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT

from django.db.models.deletion import Collector
import six
from collections import Counter, OrderedDict

from django.utils.translation import ugettext_lazy as _
# from south.modelsinspector import add_introspection_rules
from dorsale.conf import settings
from dorsale.managers import DorsaleSiteManager
import logging
logger = logging.getLogger(settings.PROJECT_NAME)  # __name__)

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


class AuthorMixin(models.Model):
    """
    Provide some automatic administration fields:

    :createdby: auth.User
        user that created the object
    :lastchangedby:  auth.User
        last user that changed the object
    :createdon: datetime
        date of creation
    :lastchangedon: datetime
        date of last change
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
    lastchangedon = models.DateTimeField(
        verbose_name=_(u'last changed on'),
        null=True, editable=False,
        help_text=_(u'date and time when this item was changed last time')
        )

    class Meta:
        abstract = True
        get_latest_by = 'createdon'

    def save(self, *args, **kwargs):
        """
        Automatically save time of creation and change;
        can’t save the user, you must do that in your view
        (or use dorsale’s generic views)

        calls `super`
        """
        if self.id:
            self.createdon = now()
            if 'user' in kwargs:
                self.createdby = kwargs['user']
        self.lastchangedon = now()
        if 'user' in kwargs:
            self.lastchangedby = kwargs['user']
            del kwargs['user'] # not allowed in super
        super(AuthorMixin, self).save(*args, **kwargs)

    def original_save(self, *args, **kwargs):
        """
        original save method, for cases where there’s no current Site,
        like in celery tasks

        just calls `super`
        """
        super(AuthorMixin, self).save(*args, **kwargs)


class SiteMixin(models.Model):
    """
    Provide a `site` field (Site this objects belongs to).
    Override default manager `objects` with a `DorsaleSiteManager`.
    """
    site = models.ForeignKey(Site,
        verbose_name=_(u'tenant’s site'),
        editable=False,
        default=settings.SITE_ID,
        help_text=_(u'site of the related customer/project/team')
        )
    objects = DorsaleSiteManager()

    class Meta:
        abstract = True

    def original_save(self, *args, **kwargs):
        """
        original save method, for cases where there’s no current Site,
        like in celery tasks

        just calls `super`
        """
        super(SiteMixin, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Set object’s `site` to kwargs['site'] or current site.

        calls `super`
        """
        if 'site' in kwargs:
            self.site = kwargs['site']
            del kwargs['site']
        else:
            self.site = Site.objects.get_current()
        super(SiteMixin, self).save(*args, **kwargs)


class AuthorSiteMixin(AuthorMixin, SiteMixin):
    """
    Combine `AuthorMixin` and `SiteMixin`.
    """

    class Meta:
        abstract = True
        get_latest_by = 'createdon'

    def save(self, *args, **kwargs):
        """
        Automatically save time of creation and change;
        user only if in kwargs, otherwise you must do that in your view
        (or use dorsale’s generic views)

        calls `super`
        """
        # we inherit from AuthorMixin first, so its save method gets called,
        # but not SiteMixin's
        if 'site' in kwargs:
            self.site = kwargs['site']
            del kwargs['site']
        else:
            self.site = Site.objects.get_current()
        super(AuthorSiteMixin, self).save(*args, **kwargs)


class FakeDeleteMixin(models.Model):
    """
    Add a `deleted` field and prohibit real deletion.
    """
    deleted = models.BooleanField(
        verbose_name=_('deleted?'),
        editable=False,
        default=False,
        help_text=_(u'Is this item marked as deleted?')
        )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, **kwargs):
        """
        Mark this instance as deleted and call `delete()` on all related objects.

        Don’t call `super`!
        """
        logger.info('DELETE %s' % self)
        self.deleted = True
        self.save(**kwargs)

        # the following is copied from django.db.models.base.Model

        using = using or router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, (
            "%s object can't be deleted because its %s attribute is set to None." %
            (self._meta.object_name, self._meta.pk.attname)
        )

        # Find all the related objects that need to be deleted.
        collector = Collector(using=using)
        collector.collect([self], keep_parents=keep_parents)
        #return collector.delete()

        # remove self from deletion collection
        myself_and_friends = collector.data[type(self)].remove(self)
        if myself_and_friends:
            collector.data[type(self)] = myself_and_friends
        else:
            del collector.data[type(self)]

        # Problem: collector.delete() doesn’t call object’s delete method, but deletes!

        # The following is copied from collector.delete() (db.models.deletion)
        
        # sort instance collections
        for model, instances in collector.data.items():
            collector.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        collector.sort()
        # number of objects deleted for each model label
        deleted_counter = Counter()

        with transaction.atomic(using=collector.using, savepoint=False):
            # send pre_delete signals
            for model, obj in collector.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model, instance=obj, using=collector.using
                    )

            ## fast deletes
            #for qs in collector.fast_deletes:
            #    count = qs._raw_delete(using=collector.using)
            #    deleted_counter[qs.model._meta.label] += count

            # update fields
            for model, instances_for_fieldvalues in six.iteritems(collector.field_updates):
                query = sql.UpdateQuery(model)
                for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                    query.update_batch([obj.pk for obj in instances],
                                       {field.name: value}, collector.using)

            # reverse instance collections
            for instances in six.itervalues(collector.data):
                instances.reverse()

            # delete instances
            for model, instances in six.iteritems(collector.data):
                if not issubclass(model, DorsaleBaseModel):
                # handle non-cerebrale models as usual
                    query = sql.DeleteQuery(model)
                    pk_list = [obj.pk for obj in instances]
                    count = query.delete_batch(pk_list, collector.using)
                    deleted_counter[model._meta.label] += count
                else:
                    for inst in instances:
                        inst.delete()  # expensive operation!

                if not model._meta.auto_created:
                    for obj in instances:
                        signals.post_delete.send(
                            sender=model, instance=obj, using=collector.using
                        )

        # update collected instances
        for model, instances_for_fieldvalues in six.iteritems(collector.field_updates):
            for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                for obj in instances:
                    setattr(obj, field.attname, value)
        for model, instances in six.iteritems(collector.data):
            for instance in instances:
                setattr(instance, model._meta.pk.attname, None)
        return sum(deleted_counter.values()), dict(deleted_counter)


class FieldInfoMixin(models.Model):

    items_per_page = int(getattr(settings, 'ITEMS_PER_PAGE', 10))  # : used in list views, overwrite in your models
    list_display = []  # : for list views, ignore if empty

    class Meta:
        abstract = True

    def field_info(self):
        """
        dictionary of the model’s fields (independent of `list_display`,
        thus without methods)

        {name:field,}
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
        generator of the model’s (editable) fields,
        as defined by its `list_display` attribute
        """
        if self.list_display:
            for n in self.list_display:
                if n in self.field_info():
                    yield self.field_info()[n]
                else:
                    yield getattr(self, n, '')
        else:
            for n in self._meta.fields:
                if not n.editable:
                    continue
                yield n

    def fieldnames_verbose(self):
        """
        generator of verbose (translated) names of the model’s fields,
        as defined by its `list_display` attribute
        """
        if self.list_display:
            for n in self.list_display:
                r = self.getattr(n)
                if hasattr(r, 'verbose_name'):
                    r = r.verbose_name
                yield r
        else:
            for f in self._meta.fields:
                if not f.editable:
                    continue
                yield f.verbose_name

    def fieldnames(self):
        """
        list of raw names of the model’s fields,
        as defined by its `list_display` attribute
        """
        if self.list_display:
            return self.list_display
        return [f.name for f in self._meta.fields if f.editable]

    def fieldvalues(self):
        """
        generator of the instance’s field (or method) values,
        dependent of `fieldnames`
        """
        for f in self.fieldnames():
            r = getattr(self, f)
            if type(r) is types.MethodType:
                r = r()
            yield r
        # return (getattr(self, f) for f in self.fieldnames())

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


class DorsaleBaseModel(FakeDeleteMixin, AuthorSiteMixin, FieldInfoMixin):
    """
    Abstract base class for all fiee models.

    Provide ...

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
            you can't delete our objects any more,
            they just get marked as deleted
       :site:
            Site this object belongs to

    2) additional meta info methods/properties for generic view:

       :field_info: dict
            dict of fields, independent of `list_display`
            and thus without methods
       :fields(): generator
            list of fields, influenced by `list_display`
       :fieldnames_verbose(): generator
            list of translated names of editable fields,
            influenced by `list_display`
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
            number of items on one list view page
            (default: 10 or `settings.ITEMS_PER_PAGE`)
       :list_display: list
            list of field names that should be used for generic list views
            (default: empty and thus ignored)
            used by fields(), fieldnames(), fieldnames_verbose() and fieldvalues()

    3) changed/additional manager methods:

       :objects: `DorsaleSiteManager`
            returning only not-deleted objects of the current site
       :really_all_objects: `models.Manager`
            former default manager, returning all objects
    """
    really_all_objects = models.Manager()
    # `objects = models.Manager()`
    # must come before any other manager, if admin should see *all* objects
    objects = DorsaleSiteManager()

    class Meta:
        abstract = True
        get_latest_by = 'createdon'
        # permissions = [
        #    ('view_item', _(u'Can view item')),
        # ]

    @models.permalink
    def get_absolute_url(self):
        """
        link to dorsale’s generic `show_item` view
        """
        mo = ContentType.model_class(self)
        return ('dorsale.views.show_item', (), {
            'app_name'  : mo.app_label,
            'model_name': mo.model,
            'object_id' : self.id,
        })
