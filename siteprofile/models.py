# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

# TODO: lookup table? if it makes sense at all...
AVAILABILITY = (
    ('avail',  _(u'available')),
    ('custom', _(u'available, but customer specific')),
    ('intg',   _(u'available, but not yet integrated')),
    ('dev',    _(u'in development')),
    ('plan',   _(u'in planning stage')),
    ('demand', _(u'on demand')),
)

class Module(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), max_length=63, unique=True, help_text=_(u'Name of module'))
    code = models.SlugField(verbose_name=_(u'Code'), max_length=31, unique=True, help_text=_(u'Base url of module'))
    description = models.CharField(verbose_name=_(u'Description'), max_length=255, help_text=_(u'Some words about this module'))
    available = models.CharField(verbose_name=_(u'Availability'), max_length=15, choices=AVAILABILITY, default='dev', help_text=_(u'Is this module already available?'))

    class Meta(object):
        verbose_name = _(u'Module')
        verbose_name_plural = _(u'Modules')
        
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.code)
    
    def get_absolute_url(self):
        return '/modules/%s/' % self.code
    
    def availability(self):
        """
        verbose version of `available`
        """
        return dict(AVAILABILITY)[self.available]
    
class SiteProfile(models.Model):
    site = models.OneToOneField(Site, primary_key=True, verbose_name=_(u'Site'), help_text=_(u'Tenant’s site'))
    code = models.SlugField(verbose_name=_(u'Code'), max_length=31, unique=True, help_text=_(u'Server name of site (www for www.example.com). This is used as the template name of the menu, base page of CMS pages and perhaps additional CSS.'))
    baselanguage = models.CharField(verbose_name=_(u'Base Language'), max_length=7, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, help_text=_(u'Base language of this site'))
    admingroup = models.ForeignKey(Group, verbose_name=_(u'Admin Group'), help_text=_(u'Members of this group are admins of this site.'))
    ownstyle = models.BooleanField(verbose_name=_(u'Use own style?'), default=False, help_text=_(u'Should the look differ from the main site’s? Use an additional CSS? Name of the CSS must be the code!'))
    homeurl = models.CharField(verbose_name=_(u'Start URL'), max_length=31, blank=True, help_text=_(u'URL of base view of this site. Same as code if empty!'))
    modules = models.ManyToManyField(Module, verbose_name=_(u'Modules'), help_text=_(u'The site has access to these modules.'))

    class Meta(object):
        verbose_name = _(u'Site Profile')
        verbose_name_plural = _(u'Site Profiles')
        
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
