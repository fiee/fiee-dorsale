#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import Module
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext

def list_modules(request, *args):
    """
    This view lists all modules, with pagination.
    
    Available variables in the template:
    :paginator: Paginator object
    :page: current page number of paginator
    :page_obj: page of Paginator, iterate over this to get items
    """
    paginator = Paginator(Module.objects.all(), 20, orphans=2)
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
    return render_to_response('siteprofile/list_modules.html', locals(), context_instance=RequestContext(request))  
