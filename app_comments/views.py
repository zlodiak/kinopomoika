# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.contrib import auth
from django.contrib.auth.models import User
import json

from app_comments.forms import CommentForm
from app_comments.models import Comment
from kinopom.forms import SearchForm


def custom_proc(request):
	"""
	request object for every pages
	"""	
	return{
		'request': request,
		'search_form': SearchForm,
	}
			

def ajax_comment_add(request):
	"""
	ajax procedure for add new comment about video
	"""	
	result = False
	output_username = False
	user_id = False
	date = False
	is_authenticated = False

	if request.method == 'POST':
		comment = request.POST.get('comment', '')
		video_id = request.POST.get('video_id', '')
		username = request.POST.get('username', '')
		is_authenticated = request.user.is_authenticated()
		result = True

		if is_authenticated:
			# user is auth
			user_id = request.user.pk
			username_auth = User.objects.get(id=request.user.pk).username
			entry = Comment.objects.create(
					user_id=user_id, 
					comment=comment,
					video_id=video_id,
			)		
			output_username = username_auth
		else:
			if username:
				# user no auth and with name 
				username_noauth = username
			else:
				# user no auth and without name 
				username_noauth = 'Некто неизвестный'

			output_username = username_noauth
			user_id = None
			entry = Comment.objects.create(
					user_id=user_id, 
					user_no_auth=username_noauth,
					comment=comment,
					video_id=video_id,
			)				

		date = entry.date.strftime('%Y-%m-%d %H:%M:%S')

	data = {
		'result': result,
		'user_id': user_id,
		'date': date,
		'output_username': output_username,
		'is_authenticated': is_authenticated
	}
			
	return HttpResponse(json.dumps(data), content_type='application/json')	