# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from dorsale.models import DorsaleBaseModel


class DorsaleMPTTBaseModel(DorsaleBaseModel): 
    """
    Base model for multiple inheritance from `DorsaleBaseModel` and `MPTTModel`.
    
    i.e.:

        from mptt.models import MPTTModel

        class MyModel(MPTTModel, DorsaleBaseModel):
            name = models.CharField(verbose_name=_('Name'), max_length=63, unique=True)
            parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
            tree = DorsaleMPTTSiteManager()
        
        mptt.register(MyModel)
    
    Like with MPTTModel, you must define a 'parent' field which is a ForeignKey to 'self', see django-mptt docs!
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        just calls `super`
        """
        super(DorsaleMPTTBaseModel, self).save(*args, **kwargs)

    def delete(self, using=None, *args, **kwargs):
        """
        mark this instance as deleted and call delete() on all related objects
        
        doesn’t call `super`!
        """
        # copied from MPTTModel (we need the same behaviour, just without calling super)
        tree_width = (self._mpttfield('right') -
                      self._mpttfield('left') + 1)
        target_right = self._mpttfield('right')
        tree_id = self._mpttfield('tree_id')
        self._tree_manager._close_gap(tree_width, target_right, tree_id)
        
        # mark as deleted and delete all children
        DorsaleBaseModel.delete(self, using, *args, **kwargs)
