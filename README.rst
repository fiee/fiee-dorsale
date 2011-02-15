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


Dependencies
------------

* Django 1.2 (may work with 1.1.) with included contributions
* django-registration (or compatible)


Known Issues
------------

* uses the deprecated user.message_set.create instead of the messages framework 
  in situations where there’s no request object
* No proper permission checks (but user-group-ownership checks)
* Still too much dependencies on internal asumptions and other non-public fiee projects (commented code)
* lotsa...


License
-------

BSD, like Django itself, see LICENSE
(may not entirely allowed, must still check licenses of used code)


Author(s)
---------

* fiëé visuëlle, Henning Hraban Ramm, <hraban@fiee.net>, http://www.fiee.net
* contains code from the Django project and other sources (as indicated in the code)
