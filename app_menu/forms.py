﻿from django import forms

from app_menu.models import Feedback

from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget


error_dict = {
	'spaces': 'Поле не может состоять только из пробелов',
}


class FeedbackForm(forms.ModelForm):
	message_f = forms.CharField(
		label='Сообщение',
		widget=SummernoteWidget({
			'width': '420px',
			#'height': '200px',     
		}),
	)  

	class Meta:
		model = Feedback
		fields = (
			'username_f', 
			'subject_f', 
			'email_f', 
			'message_f', 
		)

	def clean_subject_f(self):
		subject_f = self.cleaned_data['subject_f'].strip()
		if len(subject_f) == 0:
			raise forms.ValidationError(error_dict['spaces'])		

		return subject_f	

	def clean_message_f(self):
		message_f = self.cleaned_data['message_f'].strip()
		if len(message_f) == 0:
			raise forms.ValidationError(error_dict['spaces'])		

		return message_f			
