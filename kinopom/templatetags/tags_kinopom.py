from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Sum

from kinopom.forms import SearchForm
from kinopom.models import Entry, Tag
from django.contrib.auth.models import User
from app_comments.models import Comment

register = template.Library()
	
	
@register.inclusion_tag("part_common_modal.html")
def part_common_modal():
	return {}


@register.inclusion_tag("part_search_form.html")
def part_search_form():
	return {
		'search_form': SearchForm,
	}


@register.inclusion_tag("part_statistic.html")
def part_statistic():
	return {
		'only_videos': Entry.objects.all().count(),
		'only_users': User.objects.all().count(),
		'only_comments': Comment.objects.all().count(),
		'only_views': Entry.objects.all().aggregate(Sum('views')),
		'only_tags': Tag.objects.all().count(),
		'only_likes': Entry.objects.all().aggregate(Sum('likes')),
	}
