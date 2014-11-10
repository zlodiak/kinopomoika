from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('app_video',
	url(r'^$', 'views.video', name='video'),       
	url(r'^(?P<id>[0-9]+)/$', 'views.video_detail', name='video_detail'),       
)


