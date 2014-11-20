from django import forms

from app_menu.models import Feedback


class FeedbackForm(forms.ModelForm):
	class Meta:
		model = Feedback
		fields = (
			'username', 
			'subject', 
			'email', 
			'message', 
		)
