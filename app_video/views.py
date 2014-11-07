from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from kinopom.models import Entry


def video(request):
	"""
	handler for main video page
	"""		
	get_all_entries_video = Entry.get_all_entries_video()

	t = loader.get_template('video.html')
	c = RequestContext(request, {
		'get_all_entries_video': get_all_entries_video,		
	})	
	
	return HttpResponse(t.render(c)) 		
