from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('app_menu',
	url(r'^tags/(?P<id_tag>[0-9]*)$', 'views.tags', name='tags'),
	url(r'^feedback/$', 'views.feedback', name='feedback'),
)


