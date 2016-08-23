# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from dorsale.models import AuthorMixin, FakeDeleteMixin, FieldInfoMixin
from siteprofile.managers import DorsaleSiteManager


# TODO: lookup table? if it makes sense at all...
AVAILABILITY = (
    ('avail',  _('available')),
    ('custom', _('available, but customer specific')),
    ('intg',   _('available, but not yet integrated')),
    ('dev',    _('in development')),
    ('plan',   _('in planning stage')),
    ('demand', _('on demand')),
)


class Module(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=63, unique=True,
        help_text=_('Name of module'))
    code = models.SlugField(
        verbose_name=_('Code'),
        max_length=31, unique=True,
        help_text=_('Base url of module'))
    description = models.CharField(
        verbose_name=_('Description'),
        max_length=255,
        help_text=_('Some words about this module'))
    available = models.CharField(
        verbose_name=_('Availability'),
        max_length=15,
        choices=AVAILABILITY, default='dev',
        help_text=_('Is this module already available?'))

    class Meta(object):
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.code)

    def get_absolute_url(self):
        return '/modules/%s/' % self.code

    def availability(self):
        """
        verbose version of `available`
        """
        return dict(AVAILABILITY)[self.available]


class SiteProfile(models.Model):
    site = models.OneToOneField(
        Site,
        primary_key=True,
        verbose_name=_('Site'),
        help_text=_('Tenant’s site'))
    code = models.SlugField(
        verbose_name=_('Code'),
        max_length=31, unique=True,
        help_text=_('Server name of site (www for www.example.com). This is used as the template name of the menu, base page of CMS pages and perhaps additional CSS.'))
    baselanguage = models.CharField(
        verbose_name=_('Base Language'),
        max_length=7,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE,
        help_text=_('Base language of this site'))
    admingroup = models.ForeignKey(
        Group,
        verbose_name=_('Admin Group'),
        help_text=_('Members of this group are admins of this site.'))
    ownstyle = models.BooleanField(
        verbose_name=_('Use own style?'),
        default=False,
        help_text=_('Should the look differ from the main site’s? Use an additional CSS? Name of the CSS must be the code!'))
    homeurl = models.CharField(
        verbose_name=_('Start URL'),
        max_length=31, blank=True,
        help_text=_('URL of base view of this site. Same as code if empty!'))
    modules = models.ManyToManyField(
        Module,
        verbose_name=_('Modules'),
        help_text=_('The site has access to these modules.'))

    class Meta(object):
        verbose_name = _('Site Profile')
        verbose_name_plural = _('Site Profiles')

    def __unicode__(self):
        return self.code

    def get_absolute_url(self):
        return '/sites/%s/' % self.code

    def css(self):
        """
        location of site style sheet
        """
        return 'css/style-%s.css' % self.code

    def menu_template(self):
        """
        location of site menu template
        """
        return 'siteprofile/%s/menu.html' % self.code

    def header_template(self):
        """
        location of site header template
        """
        return 'siteprofile/%s/header.html' % self.code

    def modlist(self):
        """
        list of module codes, to use in templates like

        {% if "mymod" in site_profile.modlist %}

        """
        return [m.code for m in self.modules.all()]


class SiteMixin(models.Model):
    """
    Provide a `site` field (Site this objects belongs to).
    Override default manager `objects` with a `DorsaleSiteManager`.
    """
    site = models.ForeignKey(Site,
        verbose_name=_('tenant’s site'),
        editable=False,
        default=settings.SITE_ID,
        help_text=_('site of the related customer/project/team')
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
        #    ('view_item', _('Can view item')),
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
