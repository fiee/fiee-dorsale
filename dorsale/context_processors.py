from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from siteprofile.models import SiteProfile


def info(request):
    """Add some information to the context:

    :site: site ID of current site
    :site_profile: `dorsale.siteprofile.models.SiteProfile` of current site
    :MEDIA_URL: `settings.MEDIA_URL`
    """
    site = Site.objects.get_current()
    return {
        'site': site,
        'site_profile' : SiteProfile.objects.get(pk=site),
        'MEDIA_URL': settings.MEDIA_URL,
    }
