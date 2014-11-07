# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm


class SearchForm(forms.Form):
	phrase = forms.CharField(
		label='Фраза для поиска',
		required=True,
	)			
