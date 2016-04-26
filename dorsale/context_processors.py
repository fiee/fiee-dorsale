from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site


def info(request):
    """Add some information to the context:

    :site: site ID of current site
    :site_profile: `dorsale.siteprofile.models.SiteProfile` of current site
    :MEDIA_URL: `settings.MEDIA_URL`
    """
    site = Site.objects.get_current()
    try:
        from siteprofile.models import SiteProfile
        siteprofile = SiteProfile.objects.get(pk=site)
    except ImportError:
        siteprofile = None
    except SiteProfile.DoesNotExist:
        siteprofile = SiteProfile.objects.create(site_id=-1, admingroup_id=-1)
    return {
        'site': site,
        'site_profile' : siteprofile,
        'MEDIA_URL': settings.MEDIA_URL,
    }
