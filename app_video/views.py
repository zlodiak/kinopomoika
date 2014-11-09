# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.core import serializers

from app_comments.models import Comment
from app_comments.forms import CommentForm
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
	'''
	page detail for video
	and increment views
	'''
	count_comments = Comment.objects.filter(video_id=id, is_active=True).count()

	if request.method == 'POST':	
		count_comments_on_page = int(request.POST.get('count_comments_on_page', ''))
		count_comments_all = int(request.POST.get('count_comments_all', ''))

		comments = Comment.get_comments_entries_video(video_id=id, cut_begin=count_comments_on_page, cut_end=count_comments_all + 5)

		result = serializers.serialize('json', comments)

		return HttpResponse(json.dumps(result), content_type='application/json')
	else:	
		Entry.increment_views(id)
		comment_form = CommentForm()

		video_obj = Entry.get_video(id=id)
		comment_obj = Comment.get_comments_entries_video(video_id=id, cut_begin=0, cut_end=5)
	        		
		t = loader.get_template('video_detail.html')
		c = RequestContext(request, {
			'video_obj': video_obj,
			'comment_obj': comment_obj,
			'comment_form': comment_form,
			'count_comments': count_comments,
		}, [custom_proc])	
		
		return HttpResponse(t.render(c)) 	