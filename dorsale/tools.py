# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
# from django.utils.translation import ugettext_lazy as _
import os
import re
import hashlib
import unicodedata
import importlib
# from django.conf import settings
import logging
logger = logging.getLogger(__name__)


def get_instance_id_path(instance, source_filename, target_filename='', id=None):
    """
    Create the path for a file (don’t make directories, just a string).
    This works as callable for `upload_to`.
    Unfortunately, while the instance isn’t yet saved, its ID is None;
    you need to move it after saving.

    :instance: Model instance
    :source_filename: string
        original file name
    :target_filename: string
        target file name; defaults to source_filename
    :id: string, integer
        define id to get a defined path
    """
    if not id:
        if hasattr(instance, 'pk'):
            iid = str(instance.pk)
        else:
            # this also doesn’t work while the instance is unsaved
            iid = instance.__hash__()
    else:
        iid = id
    if not target_filename:
        fn, ext = os.path.splitext(source_filename.lower())
        target_filename = "%s_%s%s" % (instance.__class__.__name__, iid, ext)
    path = os.path.join(
        instance.__class__.__module__.replace('.models', ''),
        instance.__class__.__name__,
        iid,
        target_filename)
    return path


# DEPRECATED
def get_hash_path(instance, source_filename, target_filename=''):
    """
    Create a hashed path for a file - no real security, just hard to guess.
    This works as callable for `upload_to`.

    @deprecated
    """
    if hasattr(instance, 'pk'):
        id = str(instance.pk)
    else:
        id = instance.__hash__()
    if not target_filename:
        fn, ext = os.path.splitext(source_filename.lower())
        target_filename = "%s_%s%s" % (instance.__class__.__name__, id, ext)
    path = os.path.join(
        instance.__class__.__module__.replace('.models', ''),
        instance.__class__.__name__,
        hashlib.md5(id).hexdigest(),
        target_filename)
    return path


def move_file_to_instance_id_path(storage, instance, attribute):
    """
    Move a file object that was saved without instance ID to a proper path.
    You must call instance.save() afterwards.

    :storage: Django’s storage object (`FileStorage` or compatible)
    :instance: model instance
    :attribute: name of the instance’s file attribute
    """
    filo = instance.__dict__[attribute]
    newpath = get_instance_id_path(instance, filo.name)
    openfile = storage.open(filo, 'rb')
    newfile = storage.save(newpath, openfile)
    openfile.close()
    instance.__dict__[attribute] = newfile
    # now delete original file
    if storage.exists(newpath):
        try:
            storage.delete(filo)
        except Exception as ex:
            logger.info('Couldn’t delete %s', filo)
    else:
        logger.info('Moving file %s failed.', filo)
    return filo


def slugify(text):
    """Convert `text` to a harmless, URL-ready, lowercase ASCII string."""
    if type(text) is str:
        text = unicode(text, 'utf-8')
    text = unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore')
    text = re.sub(r'[^\w\d\-]+', '', text)
    return text.replace(' ', '_').replace('__', '_').replace('--', '-')


def class_from_name(name):
    """
    Take a class name like `django.db.models.Model` and return the class
    """
    parts = name.split('.')
    mod = importlib.import_module('.'.join(parts[:-1]))
    return getattr(mod, parts[-1])
