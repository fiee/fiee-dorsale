============
fiëé dorsale
============

Why
===

In most of my projects I need some of the same features of Django models,
e.g. management data like owner and change date. You don’t want to handle
that for every model in every view again.

For my modular editorial and office automation system "fiëé cérébrale"
everything must be site dependent - most reusable apps out there don’t
care about site dependency, even if everyone has django.contrib.sites
installed.

I’d like to give back to the open source community, but of course nothing
customer-specific, so it’s time to pull the generic stuff out of my
projects.
