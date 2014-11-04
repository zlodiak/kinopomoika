from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.contrib import auth

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
	data for render registration page
	"""			
	form = RegistrationForm()
	print(1111)
	print(request.method)

	if request.method == 'POST' and request.is_ajax():
		print(22222)
		form = RegistrationForm(request.POST)	
		if form.is_valid():
			print(33333)
			new_user = form.save()
			
			return HttpResponseRedirect("/")
		
		
	t = loader.get_template('page_registration.html')
	c = RequestContext(request, {
		'form': form, 
	}, [custom_proc])	
	return HttpResponse(t.render(c)) 