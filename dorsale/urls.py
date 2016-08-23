from __future__ import absolute_import
from __future__ import unicode_literals
# from django.conf import settings
from django.conf.urls import url, include, patterns
# from django.conf.urls import * # * needed for 404 handler
# from django.views.generic import create_update #, list_detail
# from django.contrib import admin
import dorsale.views as dv


def makepatterns(mymodule, mymodels, urlpatterns=None):
    if not urlpatterns:
        urlpatterns = patterns('',)

    for mymodel in mymodels:
        name = mymodel.__name__.lower()
#         eco = {
#             'object_example': mymodel(),
#         }
#         if hasattr(mymodel, 'site'):
#             from django.contrib.sites.models import Site
#             eco['site'] = Site.objects.get_current
        urlpatterns.append(url(
            r'^' + name + r'/$',
            dv.list_items,
            {'app_name': mymodule, 'model_name': name},
            name='%s-%s-list' % (mymodule, name)))
        urlpatterns.append(url(
            r'^' + name + r'/(?P<object_id>\d+)/$',
            dv.show_item,
            {'app_name': mymodule, 'model_name': name},
            name='%s-%s-display' % (mymodule, name)))
        urlpatterns.append(url(
            r'^' + name + r'/(?P<object_id>\d+)/edit/$',
            dv.edit_item,
            {'app_name': mymodule, 'model_name': name},
            name='%s-%s-edit' % (mymodule, name)))
        urlpatterns.append(url(
            r'^' + name + r'/(?P<object_id>\d+)/delete/$',
            dv.delete_item,
            {'app_name': mymodule, 'model_name': name},
            name='%s-%s-delete' % (mymodule, name)))
        urlpatterns.append(url(
            r'^' + name + '/new/$',
            dv.new_item,
            {'app_name': mymodule, 'model_name': name},
            name='%s-%s-new' % (mymodule, name)))
#        urlpatterns.append(url(r'^'+name+r'/$', list_detail.object_list, {
#            'queryset': mymodel.objects.all(),
#            'template_name': 'list_items.html',
#            'paginate_by': int(getattr(mymodel, 'items_per_page', getattr(settings, 'ITEMS_PER_PAGE', 10))),
#            'extra_context': eco,
#            }, name='%s-%s-list' % (mymodule, name)))
#        urlpatterns.append(url(r'^'+name+r'/(?P<object_id>\d+)/$', list_detail.object_detail, {
#            'queryset': mymodel.objects.all(),
#            'template_name': 'show_item.html',
#            'extra_context': eco,
#            }, name='%s-%s-display' % (mymodule, name)))
#        urlpatterns.append(url(r'^'+name+r'/(?P<object_id>\d+)/edit/$', create_update.update_object, {
#            'model': mymodel,
#            'template_name': 'edit_item.html',
#            'extra_context': eco,
#            }, name='%s-%s-edit' % (mymodule, name)))

    return urlpatterns
