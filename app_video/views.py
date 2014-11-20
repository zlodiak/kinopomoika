# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.core import serializers
from django.contrib.auth.models import User

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
	# increment count of views
	Entry.increment_views(id)

	comment_form = CommentForm()

	video_obj = Entry.get_video(id=id)
	comment_obj = Comment.get_comments_entries_video(video_id=id)
	user_email = User.objects.get(id=video_obj.user_id).email
	related_video = Entry.objects.filter()
        		
	t = loader.get_template('video_detail.html')
	c = RequestContext(request, {
		'video_obj': video_obj,
		'comment_obj': comment_obj,
		'comment_form': comment_form,
		'user_email': user_email,
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 	