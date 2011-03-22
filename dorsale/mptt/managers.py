# -*- coding: utf-8 -*-
from dorsale.managers import DorsaleSiteManager, DorsaleGroupSiteManager
from mptt.managers import TreeManager

class DorsaleMPTTSiteManager(TreeManager, DorsaleSiteManager):
    pass

class DorsaleMPTTGroupSiteManager(TreeManager, DorsaleGroupSiteManager):
    pass
