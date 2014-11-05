from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse

register = template.Library()
	
	
@register.inclusion_tag("part_common_modal.html")
def part_common_modal():
	return {}

