from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('app_comments',
	url(r'^ajax_comment_add/$', 'views.ajax_comment_add', name='ajax_comment_add'),       
)


