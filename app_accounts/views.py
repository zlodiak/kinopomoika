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
	print(111)

	if request.method == 'POST' and request.is_ajax():
		form = RegistrationForm(request.POST)	
		print(222)
		if form.is_valid():
			try:
				new_user = form.save()
				print(3333)
			except:
				print(4444)
			else:
				result = True
				print(5555)

	data = {
		'result': result,		
	}
	print(data)
			
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
