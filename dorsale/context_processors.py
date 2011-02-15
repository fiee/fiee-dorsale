from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
#from siteprofile.models import SiteProfile

def info(request):
    site = Site.objects.get_current()
    return {
        'site': site,
        #'site_profile' : SiteProfile.objects.get(pk=site),
        'MEDIA_URL': settings.MEDIA_URL,
        'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
    }
