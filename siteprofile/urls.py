from django.conf.urls import url

urlpatterns = [
    url(
        r'^$|^(.*)/$',
        'siteprofile.views.list_modules',
        name='siteprofiles-modules-list')
]
