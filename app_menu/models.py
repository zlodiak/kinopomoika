# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  

from djangocms_text_ckeditor.fields import HTMLField


class Feedback(models.Model):
	username = models.CharField(
		verbose_name=u"Имя", 
		max_length=100,
		blank=True,
	)
	subject = models.CharField(
		verbose_name=u"Тема", 
		max_length=100,
		blank=False,
	)	
	email = models.EmailField(
		verbose_name=u"Email", 
		max_length=100,
		blank=True,
	)		
	message = models.TextField(
		verbose_name=u'Сообщение',
		max_length=50000, 
		blank=False,
	)			
	date = models.DateTimeField(
		verbose_name=u'Дата создания',
		default=datetime.now(),
		auto_now=True,
	)				

	class Meta:
		verbose_name = u"""Отзыв"""
		verbose_name_plural = u"""отзывы"""



