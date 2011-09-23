from django.conf import settings
from django.contrib.sites.models import Site
#from django.http import HttpResponsePermanentRedirect

class MultiSiteMiddleware: 
    """
    Change SITE_ID according to the calling host.

    from http://groups.google.de/group/django-users/msg/157d6d1334a2e72b?pli=1
    """
    def process_request(self, request): 
        if request.path.startswith('/admin/'): 
            return 
        try: 
            host = request.get_host().rsplit(':', 1)[0]  # strip port from hostname
            site = Site.objects.get(domain=host)
            settings.SITE_ID = site.id 
            return 
        except Site.DoesNotExist:
            pass # default SITE_ID
            #return HttpResponsePermanentRedirect(settings.NO_SITE_REDIRECT) 
