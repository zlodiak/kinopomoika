#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import *

urlpatterns = patterns('tagging.views',
    url(r'^tagit-suggest/$', 'tag_it_suggest', name='tagit-suggest'),
    url(r'^typeahead-suggest/$', 'typeahead_suggest', name='typeahead-suggest'),
)
