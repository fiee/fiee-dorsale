# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from django.db import models


class DorsaleFakeManager(models.Manager):
    """
    Drop-in replacement for DorsaleSiteManager and DorsaleGroupSiteManager
    that takes arbitrary arguments and ignores them.
    """
    def __init__(self, *args, **kwargs):
        super(DorsaleFakeManager, self).__init__()
