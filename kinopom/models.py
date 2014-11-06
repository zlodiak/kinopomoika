# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

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
	description = models.TextField(
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

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = u"""видео"""
		verbose_name_plural = u"""видео"""

		