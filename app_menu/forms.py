from django import forms

from app_menu.models import Feedback


error_dict = {
	'spaces': 'Поле не может состоять только из пробелов',
}


class FeedbackForm(forms.ModelForm):
	class Meta:
		model = Feedback
		fields = (
			'username', 
			'subject', 
			'email', 
			'message', 
		)

	def clean_subject(self):
		subject = self.cleaned_data['subject'].strip()
		if len(subject) == 0:
			raise forms.ValidationError(error_dict['spaces'])		

		return subject		

	def clean_message(self):
		message = self.cleaned_data['message'].strip()
		if len(message) == 0:
			raise forms.ValidationError(error_dict['spaces'])		

		return message			
