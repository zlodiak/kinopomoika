from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm


class RegistrationForm(UserCreationForm):	
	class Meta:
		model = User
		fields = (  
			'username',   
			'email',    
			'password1', 
			'password2',
		)

	def clean_password1(self):
		password1 = self.cleaned_data['password1']
		q_letters = len(password1)
		if q_letters < 6:
			raise forms.ValidationError("Пароль не может быть короче 6 символов.")		
		if q_letters > 30:
			raise forms.ValidationError("Пароль не может быть длиннее 30 символов.")	

		return password1	
		
	def clean_username(self):
		username = self.cleaned_data['username']
		q_letters = len(username)
		if q_letters < 3:
			raise forms.ValidationError("Логин не может быть короче 3 символов.")		
		if q_letters > 30:
			raise forms.ValidationError("Логин не может быть длиннее 30 символов.")				

		return username		


class AuthenticationCustomForm(AuthenticationForm):
	username = forms.CharField(
		label='Логин',
		widget=forms.TextInput(),		
	)

	password = forms.CharField(
		label='Пароль', 
		widget=forms.PasswordInput(),
	)



