from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('',
    url(r'^$|^(.*)/$', 'siteprofile.views.list_modules', name='siteprofiles-modules-list')
)
