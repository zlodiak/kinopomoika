#coding: utf-8
from __future__ import unicode_literals, absolute_import

import six
from django.forms.widgets import TextInput
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

_default_settings = {
    'allow_spaces': 'true' if getattr(settings, 'TAGGING_AUTOSUGGEST_ALLOW_SPACES', True) else 'false',
    'force_tags': getattr(settings, 'TAGGING_AUTOSUGGEST_FORCE_TAGS', None),
    'max_length': getattr(settings, 'MAX_TAG_LENGTH', 50)
}


class TagWidgetBase(TextInput):
    def __init__(self, max_tags, *args, **kwargs):
        self.max_tags = max_tags if max_tags else getattr(settings, 'TAGGING_AUTOSUGGEST_MAX_TAGS', 20)
        self.namespace = kwargs.pop('namespace', None)
        self.settings = kwargs.pop('settings', {})
        super(TagWidgetBase, self).__init__(*args, **kwargs)

    def _get_js(self):
        raise NotImplementedError

    def _get_css(self):
        raise NotImplementedError