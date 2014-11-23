from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse

from kinopom.models import Entry

register = template.Library()
	

@register.inclusion_tag("part_related_video.html")
def part_related_video(tags, id_basic_video):
	tags_list = [tag.id for tag in tags]

	entries_related_video = Entry.objects.filter(tags__pk__in=tags_list)[:7]

	return {
		'entries_related_video': entries_related_video,
		'tags_list': tags_list,
		'id_basic_video': id_basic_video,
		'tags_len': len(tags),
	}


@register.inclusion_tag("part_video_unit.html")
def part_video_unit(entries, id):
	return {
		'entries': entries,
		'id': id,
	}

