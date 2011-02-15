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
** "created by / on" and "last changed by / on"
** "deleted" marker (no real deletion anymore)
** "site" ID
** "objects.all()" returns only not-deleted objects of the current site 
   (see dorsale.models.managers.DorsaleSiteManager_)
** some metadata methods for your templates
  See the code for more information!
* Use dorsale.models.managers.DorsaleSiteManager_ and 
  dorsale.models.managers.DorsaleGroupSiteManager_
  to restrict "objects.all()" like above or even to items 
  that belong to a Group the current User belongs to.
* Use siteprofile 
** to change your application’s view by site
** to restrict parts of your application (modules) by site

Goodies
-------

* Widgets and tools for RGB and CMYK colors: see dorsale.colors_


Dependencies
------------

* Django 1.2 (may work with 1.1.) with included contributions
* django-registration (or compatible)
* Templates and widgets use YUI-CSS, jQuery and jQuery-UI


Known Issues
------------

* uses the deprecated user.message_set.create instead of the messages framework 
  in situations where there’s no request object
* admin site doesn’t work completely
* No proper permission checks (but user-group-ownership checks)
* Still too much dependencies on internal asumptions and other non-public fiee projects (commented code)
* lotsa...


License
-------

BSD, like Django itself, see LICENSE
(may not entirely be allowed, must still check licenses of used code)


Author(s)
---------

* fiëé visuëlle, Henning Hraban Ramm, <hraban@fiee.net>, http://www.fiee.net
* contains code from the Django project and other sources (as indicated in the code)


.. _dorsale.models.DorsaleBaseModel: ./blob/master/dorsale/models/models.py
.. _dorsale.models.managers.DorsaleSiteManager: ./blob/master/dorsale/models/managers.py
.. _dorsale.models.managers.DorsaleGroupSiteManager: ./blob/master/dorsale/models/managers.py
.. _dorsale.colors: ./tree/master/dorsale/colors/
