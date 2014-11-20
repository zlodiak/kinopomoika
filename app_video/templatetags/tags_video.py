from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse

register = template.Library()
	

@register.inclusion_tag("part_related_video.html")
def part_related_video(tags):
	return {
		'qqq': 222,
		'tags_len': len(tags),
	}

