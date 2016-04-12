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
    try:
        siteprofile = SiteProfile.objects.get(pk=site)
    except SiteProfile.DoesNotExist:
        siteprofile = SiteProfile.objects.create(site_id=-1, admingroup_id=-1)
    return {
        'site': site,
        'site_profile' : siteprofile,
        'MEDIA_URL': settings.MEDIA_URL,
    }
