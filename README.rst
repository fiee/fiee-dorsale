============
fiëé dorsale
============

Rationale
---------

In most of my projects I need some of the same features of Django_ models,
e.g. management data like owner and change date. You don’t want to handle
that for every model in every view again.

For my modular editorial and office automation system "fiëé cérébrale"
everything must be site dependent - most reusable apps out there don’t
care about site dependency, even if everyone has django.contrib.sites
installed.

I’d like to give back to the open source community, but of course nothing
customer-specific and no embarassing secrets from the git history, so it’s
time to pull the generic stuff out of my projects.

I’m planning to make this a cosmos of loosely coupled data bits – 
attachable sticky notes (`fiëé adhésive`_), events (`fiëé témporâle`_),
geodata (`fiëé locâle`, coming soon), categorized with tagging – 
and some useful apps on top of that:
a collaboration tool with to-do list and doodle-like functions 
(`fiëé preposale`, not yet public), a party/banquet planner (`fiëé festîve`,
not yet public), tools for publishers (`fiëé édition`, not public)
and maybe more.
Probably too much for one man’s hobby.
I was also projecting some club-and-congress management app (usable e.g. for
associations and churches), perhaps also LETS...


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
  
  Functionality of DorsaleBaseModel comes from mixins that you can also use on their own:
  
  * AuthorMixin: created and last changed information
  * SiteMixin: site ID
  * AuthorSiteMixin: combined AuthorMixin and SiteMixin (since both override `save`)
  * FakeDeleteMixin: "deleted" marker
  * FieldInfoMixin: metadata methods
  
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


Dependencies
------------

* Python_ 2.7
* Django_ 1.6+ with included contributions (1.9 suggested)
* django-registration_ (or compatible)
* Templates and widgets use jQuery_ and `jQuery UI`_
* django-mptt_ for dorsale.mptt_ (beware, dorsale.mptt is not tested with current django-mptt!)
* Optional `fiëé colorée`_ for color picker widget
* Optional xlwt_ and odfpy_ if you want to export data to XLS and/or ODS
* far too much other stuff that you only need under special circumstances


Known Issues
------------

* uses the deprecated user.message_set.create_ instead of the `messages framework`_ 
  in situations where there’s no request object
  TODO: use e.g. django-async-messages_
* admin site doesn’t work completely
* No proper permission checks (but user-group-ownership checks)
* Still too much dependencies on internal asumptions and other non-public fiee projects (commented code)
* No tests (must finally learn to write them)
* lotsa...


Ideas
-----

* Use class based views
* Try to extract base model stuff to mixins to ease inheritance, have a look at https://github.com/bmihelac/ (django-site-permissions and django-sites-ext)
* Add Sphinx_ docs and enhance setup.py


License
-------

BSD, see LICENSE_
(may not entirely be allowed, must still check licenses of used code)


Author(s)
---------

* fiëé visuëlle, Henning Hraban Ramm, <hraban@fiee.net>, http://www.fiee.net
* contains code from django-mptt_ by Jonathan Buchanan, Craig de Stigter et.al.
* contains JSON helpers by `Felipe Prenholato`_
* contains code from the Django_ project and other sources (as indicated in the code)


.. _LICENSE: ./fiee-dorsale/raw/master/LICENSE
.. _dorsale.models.DorsaleBaseModel: ./fiee-dorsale/blob/master/dorsale/models/models.py
.. _dorsale.models.managers.DorsaleSiteManager: ./fiee-dorsale/blob/master/dorsale/models/managers.py
.. _dorsale.models.managers.DorsaleGroupSiteManager: ./fiee-dorsale/blob/master/dorsale/models/managers.py
.. _dorsale.mptt: ./fiee-dorsale/tree/master/dorsale/mptt/
.. _siteprofile: ./fiee-dorsale/tree/master/siteprofile/
.. _`fiëé colorée`: https://github.com/fiee/fiee-coloree
.. _`fiëé adhésive`: https://github.com/fiee/fiee-adhesive
.. _`fiëé témporâle`: https://github.com/fiee/fiee-temporale

.. _Python: http://www.python.org
.. _Django: http://djangoproject.com
.. _user.message_set.create: http://docs.djangoproject.com/en/1.2/topics/auth/#messages
.. _messages framework: http://docs.djangoproject.com/en/1.2/ref/contrib/messages/
.. _django-async-messages: https://github.com/fiee/django-async-messages/
.. _django-registration: https://bitbucket.org/ubernostrum/django-registration/
.. _django-mptt: https://github.com/django-mptt/django-mptt/
.. _jQuery: http://docs.jquery.com/
.. _jQuery UI: http://jqueryui.com/demos/
.. _Felipe Prenholato: http://chronosbox.org/blog/jsonresponse-in-django?lang=en
.. _xlwt: http://www.python-excel.org
.. _odfpy: https://github.com/eea/odfpy


