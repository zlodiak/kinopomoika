from django import template
from django.contrib.auth.models import User
from django.http import HttpResponse

from app_accounts.forms import RegistrationForm, AuthenticationCustomForm

register = template.Library()
	
	
@register.inclusion_tag("part_reg_form.html")
def part_reg_form():
	return {
		'registration_form': RegistrationForm,
	}	

@register.inclusion_tag("part_auth_form.html")
def part_auth_form():
	return {
		'auth_form': AuthenticationCustomForm,
	}	



	