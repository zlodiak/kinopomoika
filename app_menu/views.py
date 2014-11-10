# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response

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

	all_tags_entries = Tag.objects.all()
        		
	t = loader.get_template('page_tags.html')
	c = RequestContext(request, {
		'all_tags_entries': all_tags_entries,
		'tag_entries': tag_entries,
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 	