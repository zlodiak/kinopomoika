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
	is_authenticated = request.user.is_authenticated()

	if request.method == 'POST':
		comment = request.POST.get('comment', '')
		video_id = request.POST.get('video_id', '')

		try:
			Comment.objects.create(
					user_id=request.user, 
					comment=comment,
					video_id=video_id,
				)
		except:
			pass
		else:
			result = True

	print(is_authenticated)
	print(result)

	data = {
		'result': result,
		'is_authenticated': is_authenticated
	}
			
	return HttpResponse(json.dumps(data), content_type='application/json')	