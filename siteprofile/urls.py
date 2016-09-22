from django.conf.urls import url
from siteprofile.views import list_modules

urlpatterns = [
    url(
        r'^$|^(.*)/$',
        list_modules,
        name='siteprofiles-modules-list')
]
