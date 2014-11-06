# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

class Entry(models.Model):
	user = models.ForeignKey(
		User, 
		verbose_name=u"пользователь", 
		blank=True, 
		null=True,
	)
	title = models.CharField(
		u"заголовок", 
		max_length=100,
	)
	description = models.TextField(
		'Описание',
		max_length=50000, 
		default=None,
		blank=True,
	)
	views = models.IntegerField(
		default=0,
		null=False,
		blank=True,
	)	
	likes = models.IntegerField(
		default=0,
		null=False,
		blank=True,
	)				
	date = models.DateTimeField(
		'Дата создания',
		default=datetime.now(),
		auto_now=True,
	)
	last_edit_date = models.DateTimeField(
		'Дата последнего редактирования',
		default=datetime.now(),
		auto_now=True,
	)		
	is_active = models.BooleanField(default=True)					
	is_delete = models.BooleanField(default=False)	

	def __unicode__(self):
		return self.title

	class Meta:
		verbose_name = u"""видео"""
		verbose_name_plural = u"""видео"""

		