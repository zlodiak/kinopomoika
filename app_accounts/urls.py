from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('app_accounts',
	url(r'^registration/$', 'views.registration', name='registration'),
	url(r'^ajax_reg_form_check/$', 'views.ajax_reg_form_check', name='ajax_reg_form_check'),
	url(r'^authentication/$', 'views.authentication', name='authentication'),  
	url(r'^logout/$', 'views.logout', name='logout'),          
)


