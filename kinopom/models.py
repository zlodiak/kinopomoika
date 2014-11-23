# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  
import re
from django.db.models import F

from djangocms_text_ckeditor.fields import HTMLField


class Tag(models.Model):
	title = models.CharField(
		verbose_name=u"Название", 
		max_length=100,
	)
	description = HTMLField(
		verbose_name=u'Описание',
		max_length=50000, 
		default=None,
		blank=True,
	)			
	date = models.DateTimeField(
		verbose_name=u'Дата создания',
		default=datetime.now(),
	)
	last_edit_date = models.DateTimeField(
		verbose_name=u'Дата последнего редактирования',
		default=datetime.now(),
		auto_now=True,
	)		
	is_active = models.BooleanField(
		verbose_name=u'Активно',
		default=True,
	)					

	class Meta:
		verbose_name = u"""тег"""
		verbose_name_plural = u"""теги"""

	def __unicode__(self):
		return u"{0}".format(self.title)	

	@classmethod
	def get_all_tags_entries(self, cut_begin, cut_end):
		return self.objects.filter(is_active=1).order_by('title')[cut_begin:cut_end]		


class Entry(models.Model):
	user = models.ForeignKey(
		User, 
		verbose_name=u"Пользователь", 
		blank=True, 
		null=True,
	)
	title = models.CharField(
		verbose_name=u"Название", 
		max_length=100,
	)
	video_url = models.URLField(
		verbose_name=u"Адрес видео", 
		max_length=100,
		null=True,
		blank=False,
	)	
	description = HTMLField(
		verbose_name=u'Описание',
		max_length=50000, 
		default=None,
		blank=True,
	)
	views = models.IntegerField(
		verbose_name=u'Количество просмотров',
		default=0,
		null=False,
		blank=True,
	)	
	likes = models.IntegerField(
		verbose_name=u'Количество лайков',
		default=0,
		null=False,
		blank=True,
	)			
	date = models.DateTimeField(
		verbose_name=u'Дата создания',
		default=datetime.now(),
		auto_now=True,
	)
	last_edit_date = models.DateTimeField(
		verbose_name=u'Дата последнего редактирования',
		default=datetime.now(),
		auto_now=True,
	)		
	is_active = models.BooleanField(
		verbose_name=u'Активно',
		default=True,
	)					
	is_delete = models.BooleanField(
		verbose_name=u'Удалено админом',
		default=False,
	)	
	tags = models.ManyToManyField(Tag)		

	def __unicode__(self):
		result = False

		if 'watch' in str(self.video_url):
			search = re.search(u'.*?(watch.v=)(.*)$', str(self.video_url))
			result = str(search.group(2))	
		else:
			result = 'Error link'	

		return result

	class Meta:
		verbose_name = u"""видео"""
		verbose_name_plural = u"""видео"""

	@classmethod
	def get_all_entries_video(self):
		return self.objects.filter(is_active=True, is_delete=False).order_by('-date')		

	@classmethod
	def get_last_entries_video(self):
		return self.objects.filter(is_active=True, is_delete=False).order_by('-date')[:6]		

	@classmethod
	def get_most_likes(self):
		return self.objects.filter(is_active=True, is_delete=False).order_by('-likes')[:6]	

	@classmethod
	def get_most_views(self):
		return self.objects.filter(is_active=True, is_delete=False).order_by('-views')[:6]			

	@classmethod
	def get_video(self, id):
		return self.objects.get(is_active=True, is_delete=False, id=id)					
		
	@classmethod
	def increment_views(self, video_id):
		view = self.objects.get(id=video_id)
		view.views = F('views') + 1
		view.save()
		
		return		

	@classmethod
	def decrement_like(self, video_id):
		like = self.objects.get(id=video_id)
		like.likes = F('likes') - 1
		like.save()
		
		return		

	@classmethod
	def increment_like(self, video_id):
		like = self.objects.get(id=video_id)
		like.likes = F('likes') + 1
		like.save()
		
		return							

		
class Like(models.Model):
	user = models.IntegerField(
		verbose_name=u"Пользователь", 
		blank=True, 
		null=True,
	)	
	video_id = models.IntegerField(
		verbose_name=u'Номер видео',
		default=None,
		null=True,
		blank=True,
	)					
	date_first_click = models.DateTimeField(
		verbose_name=u'Дата Начала',
		default=datetime.now(),
	)
	last_edit_date = models.DateTimeField(
		verbose_name=u'Дата последнего редактирования',
		default=datetime.now(),
		auto_now=True,
	)	

