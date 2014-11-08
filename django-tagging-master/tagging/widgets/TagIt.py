#coding: utf-8
from __future__ import unicode_literals, absolute_import

import six
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from tagging import conf
from tagging.widgets.base import TagWidgetBase


class TagWidget(TagWidgetBase):

    def render(self, name, value, attrs=None):
        """ Render HTML code """

        case_sensitive = 'true' if conf.FORCE_TAGS is not None else 'false'
        max_tag_lentgh = conf.MAX_TAG_LENGTH
        autocomplete_min_length = conf.MIN_LENGTH
        remove_confirmation = 'true' if conf.REMOVE_CONFIRMATION else 'false'
        animate = 'true' if conf.ANIMATE else 'false'
        allow_spaces = 'true' if conf.ALLOW_SPACES else 'false'

        list_view = reverse('tagging:tagit-suggest')

        if self.namespace is not None:
            list_view = '{0}?ns={1}'.format(list_view, self.namespace)

        html = super(TagWidget, self).render(name, value, attrs)
        # Subclass this field in case you need to add some custom behaviour like custom callbacks
        js = """<script type="text/javascript">init_jQueryTagit({
                allowSpaces: %s,
                objectId: '%s',
                sourceUrl: '%s',
                fieldName: '%s',
                minLength: %s,
                removeConfirmation: %s,
                caseSensitive: %s,
                animate: %s,
                maxLength: %s,
                maxTags: %s,
                onTagAdded  : null,
                onTagRemoved: null,
                onTagClicked: null,
                onMaxTagsExceeded: null,
            })
            </script>""" % (allow_spaces, attrs['id'], list_view, name, autocomplete_min_length, remove_confirmation, case_sensitive,
                            animate, max_tag_lentgh, self.max_tags)
        return mark_safe("\n".join([html, js]))

    class Media:
        js_base_url = '{0}tagging/tagit/'.format(settings.STATIC_URL)

        js = (
            '%stagging_autosuggest.js' % js_base_url,
            conf.JQUERY_UI_FILE,
            '%sjquery.tag-it.min.js' % js_base_url,
        )

        css_list = conf.TAGIT_CSS
        if isinstance(css_list, six.string_types):
            css_list = [css_list]
        css = {
            'screen': css_list
        }
