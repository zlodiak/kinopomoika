from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.contrib import auth
from django.contrib.auth.models import User
import json

from app_accounts.forms import RegistrationForm, AuthenticationCustomForm
from kinopom.forms import SearchForm
from kinopom.models import Like, Entry


def custom_proc(request):
	"""
	request object for every pages
	"""	
	return{
		'request': request,
	}


def registration(request):
	"""
	ajax refistration procedure
	"""	
	result = False		

	form = RegistrationForm()

	if request.method == 'POST' and request.is_ajax():
		form = RegistrationForm(request.POST)	
		if form.is_valid():
			try:
				new_user = form.save()
				new_user.groups.add(1)
			except:
				pass
			else:
				result = True

	data = {
		'result': result,		
	}
			
	return HttpResponse(json.dumps(data), content_type='application/json')	
			

def ajax_reg_form_check(request):
	"""
	ajax check username for registration form
	"""	
	result = {}

	if request.method == 'POST' and request.is_ajax():
		username = request.POST.get('username', '')
		email = request.POST.get('email', '')
		result = {
			'username': User.objects.filter(username=username).exists(),
			'email': User.objects.filter(email=email).exists()
		}
			
	return HttpResponse(json.dumps(result), content_type='application/json')	


def logout(request):
	"""
	logout
	"""		
	result = False		

	try:
		auth.logout(request)
	except:
		pass
	else:
		result = True

	data = {
		'result': result,		
	}
			
	return HttpResponse(json.dumps(data), content_type='application/json')	


def authentication(request):
	"""
	authentication procedure
	return true - auth ok
	return false - auth failed
	"""		
	result = False	

	if request.method == 'POST' and request.is_ajax():
		form = AuthenticationCustomForm(data=request.POST)		
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')

		if form.is_valid():		
			try:
				user = auth.authenticate(username=username, password=password)
			except:
				pass
			else:
				if user is not None and user.is_active:
					try:
						auth.login(request, user)	
					except:
						pass
					else:													
						result = True

	data = {
		'result': result,		
	}
			
	return HttpResponse(json.dumps(data), content_type='application/json')	


def ajax_like(request):
	"""
	ajax check auth for like process and change procedure like data
	action - value for ajax refresh counter on page
	is_authenticated - flag authentication, transmitted to js-script for output modal
	"""	
	is_authenticated = False
	action = 0
	video_id = request.POST.get('video_id', '')

	if request.method == 'POST' and request.is_ajax():
		if request.user.is_authenticated():
			is_authenticated = True

			like_exists = Like.objects.filter(video_id=video_id, user=request.user.pk).exists()
			if like_exists:
				# minus. delete record. decrement for like table
				Like.objects.filter(video_id=video_id, user=request.user.pk).delete()	# decrement for like table
				Entry.decrement_like(video_id=video_id)									# increment for entry table
				action = -1																# unit for ajax-refresh counter on page
			else:
				# plus. create record. increment for like table
 				Like.objects.create(video_id=video_id, user=request.user.pk)	
 				Entry.increment_like(video_id=video_id)
 				action = 1			

	data = {
		'is_authenticated': is_authenticated,
		'action': action
	}

	return HttpResponse(json.dumps(data), content_type='application/json')	




