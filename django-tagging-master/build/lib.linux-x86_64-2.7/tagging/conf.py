#coding: utf-8
from __future__ import unicode_literals, absolute_import
"""
Convenience module for access of custom tagging application settings,
which enforces default settings when the main settings module does not
contain the appropriate settings.
"""
from django.conf import settings

# The maximum length of a tag's name.
MAX_TAG_LENGTH = getattr(settings, 'MAX_TAG_LENGTH', 50)
MAX_TAG_NAMESPACE_LENGTH = getattr(settings, 'MAX_TAG_VALUE_LENGTH', 50)
MAX_TAG_NAME_LENGTH = getattr(settings, 'MAX_TAG_NAME_LENGTH', 50)
MAX_TAG_VALUE_LENGTH = getattr(settings, 'MAX_TAG_VALUE_LENGTH', 50)

# limit the max size attributes to 50 per field, because the model fields
# cannot store longer values.
if MAX_TAG_NAMESPACE_LENGTH is None or MAX_TAG_NAMESPACE_LENGTH > 50:
    MAX_TAG_NAMESPACE_LENGTH = 50
if MAX_TAG_NAME_LENGTH is None or MAX_TAG_NAME_LENGTH > 50:
    MAX_TAG_NAME_LENGTH = 50
if MAX_TAG_VALUE_LENGTH is None or MAX_TAG_VALUE_LENGTH > 50:
    MAX_TAG_VALUE_LENGTH = 50

# Whether to force all tags to lowercase before they are saved to the
# database.
FORCE_LOWERCASE_TAGS = getattr(settings, 'FORCE_LOWERCASE_TAGS', False)

# Доступные значения: 'lower', 'upper'
FORCE_TAGS = getattr(settings, 'TAGGING_FORCE_TAGS', None)
if FORCE_TAGS not in ['lower', 'upper']:
    FORCE_TAGS = None

WIDGET = getattr(settings, 'TAGGING_WIDGET', 'tagging.widgets.TagIt')

MIN_LENGTH = getattr(settings, 'TAGGING_MIN_LENGTH', 1)
REMOVE_CONFIRMATION = getattr(settings, 'TAGGING_REMOVE_CONFIRMATION', True)
ANIMATE = getattr(settings, 'TAGGING_ANIMATE', True)
ALLOW_SPACES = getattr(settings, 'TAGGING_ALLOW_SPACES', True)


_DEFAULT_JQUERY_UI_FILE = '//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js'
JQUERY_UI_FILE = getattr(settings, 'TAGGING_JQUERY_UI_FILE', _DEFAULT_JQUERY_UI_FILE)

_DEFAULT_TAGIT_CSS_FILE = '{0}tagging/tagit/ui-autocomplete-tag-it.css'.format(settings.STATIC_URL)
TAGIT_CSS = getattr(settings, 'TAGGING_TAGIT_CSS', _DEFAULT_TAGIT_CSS_FILE)

INCLUDE_BOOTSTRAP = getattr(settings, 'TAGGING_INCLUDE_BOOTSTRAP', True)