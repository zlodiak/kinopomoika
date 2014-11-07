# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from kinopom.models import Entry
from kinopom.forms import SearchForm


def custom_proc(request):
	"""
	request object for every pages
	"""	
	return{
		'request': request,
		'search_form': SearchForm,
	}

def video(request):
	"""
	handler for main video page
	"""		
	get_all_entries_video = Entry.get_all_entries_video()

	t = loader.get_template('video.html')
	c = RequestContext(request, {
		'get_all_entries_video': get_all_entries_video,		
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 		


def video_detail(request, id):	
	video_obj = Entry.get_video(id=id)
        		
	t = loader.get_template('video_detail.html')
	c = RequestContext(request, {
		'video_obj': video_obj,
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 	