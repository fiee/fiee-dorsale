============
fiëé dorsale
============

Rationale
---------

In most of my projects I need some of the same features of Django models,
e.g. management data like owner and change date. You don’t want to handle
that for every model in every view again.

For my modular editorial and office automation system "fiëé cérébrale"
everything must be site dependent - most reusable apps out there don’t
care about site dependency, even if everyone has django.contrib.sites
installed.

I’d like to give back to the open source community, but of course nothing
customer-specific and no embarassing secrets from the git history, so it’s
time to pull the generic stuff out of my projects.


What and how
------------

* Use dorsale.models.DorsaleBaseModel_ as base for your own models, 
  and you get for free:
  
  * "created by / on" and "last changed by / on"
  * "deleted" marker (no real deletion anymore)
  * "site" ID
  * "objects.all()" returns only not-deleted objects of the current site 
    (see dorsale.models.managers.DorsaleSiteManager_)
  * some metadata methods for your templates
  
* Use dorsale.models.managers.DorsaleSiteManager_ and 
  dorsale.models.managers.DorsaleGroupSiteManager_
  to restrict "objects.all()" like above or even to items 
  that belong to a Group the current User belongs to.
  
* Use siteprofile_ ...

  * to change your application’s view by site
  * to restrict parts of your application (modules) by site

* Use dorsale.mptt_ ...

  * to get hierarchical dorsale models

See the code for more information!

Goodies
-------

* Widgets and tools for RGB and CMYK colors: see dorsale.colors_


Dependencies
------------

* Django 1.2 (may work with 1.1.) with included contributions
* django-registration_ (or compatible; beware: use the source version, the one in PyPI is broken!)
* Templates and widgets use `YUI grids css`_, jQuery_ and `jQuery UI`_
* django-mptt_ (current github version, not the old one from googlecode) for dorsale.mptt_


Known Issues
------------

* uses the deprecated user.message_set.create_ instead of the `messages framework`_ 
  in situations where there’s no request object
* admin site doesn’t work completely
* No proper permission checks (but user-group-ownership checks)
* Still too much dependencies on internal asumptions and other non-public fiee projects (commented code)
* lotsa...


License
-------

BSD, like Django itself, see LICENSE_
(may not entirely be allowed, must still check licenses of used code)


Author(s)
---------

* fiëé visuëlle, Henning Hraban Ramm, <hraban@fiee.net>, http://www.fiee.net
* contains code from django-mptt_ by Jonathan Buchanan et.al.
* contains code from the Django project and other sources (as indicated in the code)


.. _LICENSE: ./fiee-dorsale/raw/master/LICENSE
.. _dorsale.models.DorsaleBaseModel: ./fiee-dorsale/blob/master/dorsale/models/models.py
.. _dorsale.models.managers.DorsaleSiteManager: ./fiee-dorsale/blob/master/dorsale/models/managers.py
.. _dorsale.models.managers.DorsaleGroupSiteManager: ./fiee-dorsale/blob/master/dorsale/models/managers.py
.. _dorsale.colors: ./fiee-dorsale/tree/master/dorsale/colors/
.. _dorsale.mptt: ./fiee-dorsale/tree/master/dorsale/mptt/
.. _siteprofile: ./fiee-dorsale/tree/master/siteprofile/
.. _user.message_set.create: http://docs.djangoproject.com/en/1.2/topics/auth/#messages
.. _messages framework: http://docs.djangoproject.com/en/1.2/ref/contrib/messages/
.. _django-registration: https://bitbucket.org/ubernostrum/django-registration/
.. _django-mptt: https://github.com/django-mptt/django-mptt/
.. _YUI grids css: http://developer.yahoo.com/yui/grids/
.. _jQuery: http://docs.jquery.com/
.. _jQuery UI: http://jqueryui.com/demos/
