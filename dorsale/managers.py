#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
import logging
logger = logging.getLogger(__name__)

class DorsaleSiteManager(CurrentSiteManager):
    """
    Model manager, based on `contrib.sites.managers.CurrentSiteManager`
    
    Limit objects to
    - belonging to current site (via model.site.id==settings.SITE_ID)
    - not deleted (model.deleted==False)
    
    with `mine(userid)`:
    - user <> -1 (i.e. a user is logged in, like `is_authenticated`)
    - user exists and is active

    `site_field_name` is the name of the model’s field that's a foreign key to `django.contrib.sites.models.Site`
    """
    def __init__(self, site_field_name='site'):
        super(DorsaleSiteManager, self).__init__(site_field_name)

    def get_query_set(self):
        """Return all objects that belong to the current site and are not deleted"""
        return super(DorsaleSiteManager, self).get_query_set().filter(deleted=False)

    def get_deleted_query_set(self):
        """Return all objects that belong to the current site and *are* deleted"""
        return super(DorsaleSiteManager, self).get_query_set().filter(deleted=True)
    
    def mine(self, userid):
        """
        Filter by authenticated (existing, active) user,
        return an empty queryset if not authenticated.
        
        Requires user ID < 0 for unauthenticated users (e.g. from `django-registration`).
        
        We can’t expect a request object and take the user from there, 
        since `mine` might also get called in creation of forms.
        
        If you inherit this method, you can access `self.user` (`contrib.auth.models.User` or `None`).
        """
        try:
            self.user = User.objects.get(pk=userid)
        except:
            logger.error(_(u'User #%d doesn’t exist!') % userid)
            self.user = None
        if userid < 0 or not self.user or not self.user.is_active:
            return QuerySet(self.model).none()
        return self.get_query_set()

class DorsaleGroupSiteManager(DorsaleSiteManager):
    """
    Model manager, based on `contrib.sites.managers.CurrentSiteManager`

    Limit objects to
    - belonging to current site (via model.site.id==settings.SITE_ID)
    - not deleted (model.deleted==False)
    
    with `mine(userid)`:
    - user <> -1 (i.e. a user is logged in, like is_authenticated)
    - owned by a grop the user is a member of
    
    `site_field_name` is the name of the model's field 
    that's a foreign key to `django.contrib.sites.models.Site`
    
    `group_field_name` is the name of the model's field 
    that's a foreign key to `django.contrib.auth.models.Group`; 
    may be a foreign key lookup like 'product__group'
    """
    def __init__(self, site_field_name='site', group_field_name='group'):
        super(DorsaleGroupSiteManager, self).__init__(site_field_name)
        self.__group_field_name = group_field_name
        self.__group_is_checked = False
    
    def mine(self, userid):
        """
        This filters by the user's group
        """
        qs = super(DorsaleGroupSiteManager, self).mine(userid)  # : queryset
        if not self.user:
            return qs
        # user = User.objects.get(pk=userid)
        # check the group field
        if self.user.is_active and not self.user.is_superuser and qs.count() > 0 and self.__group_field_name:
            if not self.__group_is_checked:
                # We don't check if group_field exists to allow chains like 'product__group'
                group_count = self.user.groups.count()
                if group_count == 0 and hasattr(self.user, 'message_set'):
                    # This is deprecated, but we can't use the messages framework, since we don't have a request object
                    self.user.message_set.create(
                        message=_(u"You do not yet belong to any groups. Ask your administrator to add you to one."))
                    logger.error(_(u"User %s doesn’t belong to any group!") % self.user.username)
                self.__group_is_checked = True
            # filter on the user's groups
            qs = qs.filter(**{self.__group_field_name + '__in':self.user.groups.all()})
        return qs

