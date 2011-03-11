#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from django.utils.translation import ugettext_lazy as _
_ = lambda s: s # don’t import settings!

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Zurich'
LANGUAGE_CODE = 'de'
LANGUAGES = (('de', _(u'German')),
             ('en', _(u'English')),
             )

USE_I18N = True
USE_L10N = True
