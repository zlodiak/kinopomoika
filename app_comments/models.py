# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

from djangocms_text_ckeditor.fields import HTMLField


class Comment(models.Model):
	user = models.ForeignKey(
		User, 
		verbose_name=u"Пользователь", 
		blank=True, 
		null=True,
	)	
	user_no_auth = models.CharField(
		verbose_name=u'Пользователь не авторизованный',
		max_length=100,
		default=None,
		null=True,
		blank=True,
	)		
	comment = HTMLField(
		verbose_name=u'Комментарий',
		max_length=50000, 
		default=None,
		blank=True,
	)	
	video_id = models.IntegerField(
		verbose_name=u'Номер видео',
		default=None,
		null=True,
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

	class Meta:
		verbose_name = u"""комментарий"""
		verbose_name_plural = u"""комментарии"""						


	@classmethod
	def get_comments_entries_video(self, video_id):
		return self.objects.filter(video_id=video_id, is_active=True).order_by('-date')

	# @classmethod
	# def get_most_comments(self):
	# 	return self.objects.filter(is_active=True).order_by('-date')		