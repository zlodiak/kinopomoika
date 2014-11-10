from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse

from kinopom.forms import SearchForm

register = template.Library()
	
	
@register.inclusion_tag("part_common_modal.html")
def part_common_modal():
	return {}

@register.inclusion_tag("part_search_form.html")
def part_search_form():
	return {
		'search_form': SearchForm,
		'qqq': 222,
	}

