from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse

register = template.Library()
	
	
@register.inclusion_tag("part_modal.html")
def part_modal(modal, action):
	window_type = None
	window_type_label = None
	timeout = None
	message = None

	for entry in modal:
		if action == entry.id:
			if entry.window == 0:
				window_type = 'commonModal'
				window_type_label = 'commonModalLabel'
			elif entry.window == 1:	
				window_type = 'commonModal'
				window_type_label = 'commonModalLabel'					

			timeout = entry.timeout	
			message = entry.message

	return {
		'window_type': window_type,
		'window_type_label': window_type_label,
		'timeout': timeout,
		'message': message,
	}