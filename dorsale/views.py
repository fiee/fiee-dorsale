#!/usr/bin/env python
# -*- coding: utf-8 -*-
from conf import settings
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from siteprofile.models import SiteProfile
from dorsale.forms import ModelFormFactory
#from adhesive.models import Note

def get_model(app_name, model_name):
    """
    Find a Model or ModelForm (not a view).
    
    :app_name: name of the application, e.g. 'edition' for dorsale.edition
    :model_name: name of the model, e.g. 'Issue' for dorsale.edition.models.Issue
    """
    return ContentType.objects.get(app_label=app_name.lower(), model=model_name.lower()).model_class()

def render_404(request, params):
    """Return a 404 error with my own template."""
    params['path'] = request.get_full_path()
    response = render_to_response('404.html', params, context_instance=RequestContext(request))
    response.status_code=404
    return response   

@login_required
def home(request, **kwargs):
    """Render an index view with the root.html template."""
    site = Site.objects.get_current()
    profile = SiteProfile.objects.get(pk=site)
    if profile and profile.homeurl and profile.homeurl != '/':
        return redirect(profile.homeurl)
    else:
        return render_to_response('root.html', {}, context_instance=RequestContext(request)) 

@login_required
def list_items(request, app_name='', model_name='', template='dorsale/list_items.html'):
    """
    List all (allowed) items of `app_name.model_name` (e.g. edition.issue), with pagination.
    Render 404 if model doesn't exist. Allow customization by `template`.
    
    Available variables in the template:
    :object_example: empty object of the requested type (e.g. for table titles)
    :paginator: Paginator object
    :page: current page number of paginator
    :page_obj: page of Paginator, iterate over this to get items
    """
    object_model = get_model(app_name, model_name)
    if object_model:
        object_example = object_model()

        # set order (works also with several fields like "country,city", even if that's nut supported by the UI)
        qs = object_model.objects.mine(request.user.id)
        orderby = request.GET.get('orderby', 'id')
        l_orderby = orderby.split(',')
        try:
            qs = qs.order_by(*l_orderby)
        except FieldError, e:
            orderby = 'id'

        paginator = Paginator(qs, int(getattr(object_model, 'items_per_page', getattr(settings, 'DORSALE_ITEMS_PER_PAGE', 10))), orphans=2)
        # check if a valid number was requested as page, otherwise 1
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
            
        # check if the page exists, otherwise last
        try:
            page_obj = paginator.page(page)
        except (EmptyPage, InvalidPage):
            page_obj = paginator.page(paginator.num_pages) 
        
        del object_model    
        return render_to_response(template, locals(), context_instance=RequestContext(request))  
    else:
        return render_404(request, locals())

@login_required
def show_item(request, app_name='', model_name='', object_id=None, template='dorsale/show_item.html', _c=0):
    """
    Display one object: `app_name.model_name(id=object_id)`.
    Render 404 if object is not available. Allow customization by `template`.
    
    Available variables in the template:
    :item: the requested object
    :item_type: ContentType of the requested object
    :form: ModelForm for this object
    :notes: Notes on this object
    """
    if not object_id:
        return render_404(request, locals())
    object_model = get_model(app_name, model_name)
    try:
        item = object_model.objects.mine(request.user.id).get(pk=object_id)
        item_type = ContentType.objects.get_for_model(item)
        if hasattr(item, 'notes'):
            notes = item.notes.all()
        #else:
        #    notes = Note.objects.filter(content_type__pk=item_type.id, object_id=object_id)
    except:
        return render_404(request, locals())
    form = ModelFormFactory(object_model, user=request.user, instance=item, disabled=True)
    if not form.visible_fields() and _c<3:  # sometimes it works only in the second try, why?
        return show_item(request, app_name, model_name, object_id, template, _c+1)
    return render_to_response(template, locals(), context_instance=RequestContext(request))


@login_required
def edit_item(request, app_name='', model_name='', object_id=None, title='', template='dorsale/edit_item.html'):
    """
    Allow to edit one object: `app_name.model_name(id=object_id)`.
    
    Available variables in the template:
    :item: the requested object
    :item_type: ContentType of the requested object
    :form: ModelForm for this object
    :notes: Notes on this object
    """
    action = request.META['PATH_INFO']
    object_model = get_model(app_name, model_name)
    if not title:
        title = _(u'Edit %s') % object_model._meta.verbose_name
    if object_id:
        item = object_model.objects.get(pk=object_id)
        item_type = ContentType.objects.get_for_model(item)
        if hasattr(item, 'notes'):
            notes = item.notes.all()
        #else:
        #    notes = Note.objects.filter(content_type__pk=item_type.id, object_id=object_id)
        if request.method == 'POST':
            form = ModelFormFactory(object_model, request.POST, request.FILES, user=request.user, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, _(u"%(model_name)s %(model_id)s saved.") % {'model_name':object_model._meta.verbose_name, 'model_id':object_id})
                return HttpResponseRedirect(request.path)
        else:
            form = ModelFormFactory(object_model, user=request.user, instance=item)
        return render_to_response(template, locals(), context_instance=RequestContext(request))
    else:
        return HttpResponse(status=404)  


@login_required
def delete_item(request, app_name='', model_name='', object_id=None, title='', template='dorsale/delete_item.html'):
    """
    Allow to delete one object: `app_name.model_name(id=object_id)`.
    
    Available variables in the template:
    :item: the requested object
    :form: ModelForm for this object
    """
    action = request.META['PATH_INFO']
    object_model = get_model(app_name, model_name)
    if not title:
        title = _(u'Delete %s') % object_model._meta.verbose_name
    if object_id:
        try:
            item = object_model.objects.get(pk=object_id)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
        if request.method == 'POST':
            item.delete() # no big deal, since we only mark as deleted
            messages.success(request, _(u"%(model_name)s %(model_id)s deleted.") % {'model_name':object_model._meta.verbose_name, 'model_id':object_id})
            return HttpResponseRedirect('/%s/%s/' % (app_name, model_name))
        return render_to_response(template, locals(), context_instance=RequestContext(request))
    else:
        return HttpResponse(status=404)  

@login_required
def new_item(request, app_name='', model_name='', title='', unique_fields=[], postprocess=None, template='dorsale/edit_item.html'):
    """
    Generate a new object of app_name.model_name and redirect to its single view.
    
    :title: (str) form title (defaults to "New model_name")
    :unique_fields: (list of str) check if an object with the same fields exists
    :postprocess: (callable with userid, itemid) call this after saving the new item
    
    Available variables in the template:
    :form: ModelForm
    :action: calling URL
    :app_name:
    :model_name:
    :title:
    """
    action = request.META['PATH_INFO']
    object_model = get_model(app_name, model_name)
    if not title:
        title = _(u'New %s') % object_model._meta.verbose_name
    if request.method=='POST':
        form = ModelFormFactory(object_model, request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                params = {}
                if unique_fields:
                    # customize: which fields should be unique?
                    for pn in unique_fields:
                        params[pn] = form.cleaned_data[pn]
                    item = object_model.objects.get(**params)
                    messages.error(request, _(u'This %s already exists!') % object_model._meta.verbose_name)
                else:
                    raise ObjectDoesNotExist()
                del params
            except ObjectDoesNotExist:
                item = form.save()
                messages.success(request, _(u"New %s saved.") % object_model._meta.verbose_name)
                if postprocess:
                    postprocess(request.user.id, item.pk)
                return HttpResponseRedirect('/%s/%s/%d/' % (app_name, model_name, item.id))
    else:
        form = ModelFormFactory(object_model, user=request.user, )
    del object_model
    del postprocess
    return render_to_response(template, locals(), context_instance=RequestContext(request))
