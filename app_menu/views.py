# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from kinopom.models import Tag, Entry


def custom_proc(request):
	"""
	request object for every pages
	"""	
	return{
		'request': request,
	}


def tags(request, id_tag):	
	'''
	page for tags output with left sidebar
	'''
	tag_entries = None
	
	if id_tag:
		tag_entries = Entry.objects.filter(tags=id_tag)

		paginator = Paginator(tag_entries, 3)
		list_pages = paginator.page_range
		
		page = request.GET.get('page')
		try:
			tag_entries_paginated = paginator.page(page)
		except PageNotAnInteger:
			tag_entries_paginated = paginator.page(1)
		except EmptyPage:
			tag_entries_paginated = paginator.page(paginator.num_pages)	
			
		last_page = list_pages[-1]			

	if not id_tag:
		id_tag = 0

	all_tags_entries = Tag.objects.all()

	first_page = list_pages[0]			
        		
	t = loader.get_template('page_tags.html')
	c = RequestContext(request, {
		'all_tags_entries': all_tags_entries,
		'tag_entries_paginated': tag_entries_paginated,
		'id_tag': int(id_tag),
		'list_pages': list_pages,
		'last_page': last_page,
		'first_page': first_page,			
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 	