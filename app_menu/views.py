# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.core import serializers

from app_menu.models import Feedback
from kinopom.models import Tag, Entry
from app_menu.forms import FeedbackForm


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
	tag_entries_paginated = None
	list_pages = None
	last_page = None
	first_page = None
	
	if id_tag:
		tag_entries = Entry.objects.filter(tags=id_tag)

		paginator = Paginator(tag_entries, 10)
		list_pages = paginator.page_range
		
		page = request.GET.get('page')
		try:
			tag_entries_paginated = paginator.page(page)
		except PageNotAnInteger:
			tag_entries_paginated = paginator.page(1)
		except EmptyPage:
			tag_entries_paginated = paginator.page(paginator.num_pages)	
			
		last_page = list_pages[-1]		
		first_page = list_pages[0]		

	if not id_tag:
		id_tag = 0

	all_tags_entries = Tag.objects.all()
		
	# get all tags in DB
	count_all_tags = Tag.objects.all().count()

	if request.method == 'POST':	
		count_page_tags = int(request.POST.get('countPageTags', ''))
		all_tags_entries = Tag.get_all_tags_entries(cut_begin=count_page_tags, cut_end=count_page_tags + 12)	
		result = serializers.serialize('json', all_tags_entries)

		return HttpResponse(json.dumps(result), content_type='application/json')		

	else:
		all_tags_entries = Tag.get_all_tags_entries(cut_begin=0, cut_end=12)	
        		
	t = loader.get_template('page_tags.html')
	c = RequestContext(request, {
		'all_tags_entries': all_tags_entries,
		'tag_entries_paginated': tag_entries_paginated,
		'id_tag': int(id_tag),
		'list_pages': list_pages,
		'last_page': last_page,
		'first_page': first_page,			
		'count_all_tags': count_all_tags,			
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 	



def feedback(request):	
	'''
	page for output feedback form
	'''
	feedback_form =  FeedbackForm()	

	if request.method == 'POST':	
		feedback_form =  FeedbackForm(request.POST)	

		if feedback_form.is_valid():	
			print('valid')
			username_f = request.POST.get('username_f', '')	
			subject_f = request.POST.get('subject_f', '')	
			email_f = request.POST.get('email_f', '')	
			message_f = request.POST.get('message_f', '')	
			print(username_f)

			try:
				Feedback.objects.create(
					username_f=username_f.strip(), 
					subject_f=subject_f.strip(), 
					email_f=email_f.strip(), 
					message_f=message_f.strip(), 
				)
			except:
				pass
			else:
				t = loader.get_template('page_feedback_ok.html')
				c = RequestContext(request, {		
					'feedback_form': feedback_form,
				}, [custom_proc])	
				
				return HttpResponse(t.render(c)) 	

	t = loader.get_template('page_feedback.html')
	c = RequestContext(request, {		
		'feedback_form': feedback_form,
	}, [custom_proc])	
	
	return HttpResponse(t.render(c)) 	

