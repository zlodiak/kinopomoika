# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm

from app_comments.models import Comment


class CommentForm(forms.ModelForm):	
	username = forms.CharField(
		label='Имя',
		widget=forms.TextInput(attrs={
				'class': 'username_comment',
				'placeholder': 'Ваше имя'
			}),
	)

	comment = forms.CharField(
		label='Комментарий',
		widget=forms.Textarea(attrs={
				'class': 'comment_comment',
				'placeholder': 'Ваш комментарий'
			}),
	)	

	class Meta:
		model = Comment
