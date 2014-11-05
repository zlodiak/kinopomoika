from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.contrib import auth
from django.contrib.auth.models import User
import json

from app_accounts.forms import RegistrationForm, AuthenticationCustomForm


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
			except:
				pass
			else:
				result = True

	data = {
		'result': result,		
	}
			
	return HttpResponse(json.dumps(data), content_type='application/json')	
			

def ajax_username_check(request):
	"""
	ajax check username for registration form
	return true - matched
	return false - no matched
	"""	

	if request.method == 'POST' and request.is_ajax():
		username = request.POST.get('username', '')
		result = {'result': User.objects.filter(username=username).exists()}
			
	return HttpResponse(json.dumps(result), content_type='application/json')	



