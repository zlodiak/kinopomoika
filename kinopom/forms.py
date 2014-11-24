# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm


error_dict = {
	'spaces': 'Поле не может состоять только из пробелов',
}


class SearchForm(forms.Form):
	phrase = forms.CharField(
		label='Фраза для поиска',
		required=True,
	)		

	def clean_phrase(self):
		phrase = self.cleaned_data['phrase'].strip()
		if len(phrase) == 0:
			raise forms.ValidationError(error_dict['spaces'])		

		return phrase			
