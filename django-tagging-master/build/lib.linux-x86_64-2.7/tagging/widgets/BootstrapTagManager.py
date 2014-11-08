#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from tagging import conf
from tagging.widgets.base import TagWidgetBase


class TagWidget(TagWidgetBase):

    def render(self, name, value, attrs=None):

        if attrs is None:
            attrs = {}
        attrs.update({
            'class': 'tm-input',
            'placeholder': 'Tags',
        })

        capitalize = 'true' if conf.FORCE_TAGS == 'upper' else 'false'
        list_view = reverse('tagging:typeahead-suggest')
        prefilled = '"' + '","'.join(value.split(' ')) + '"'

        if self.namespace is not None:
            list_view = '{0}?ns={1}'.format(list_view, self.namespace)

        html = super(TagWidget, self).render(name, '', attrs)

        js = """<script type="text/javascript">
        (function($){
            $('#%(id)s').tagsManager({
                prefilled: [%(prefilled)s],
                typeahead: true,
                typeaheadAjaxSource: '%(view)s',
                typeaheadAjaxPolling: true,

                preventSubmitOnEnter: true,
                isClearInputOnEsc: true,

                CapitalizeFirstLetter: %(capitalize)s
            });
        })(jQuery || django.jQuery);
        </script>""" % {
            'prefilled': prefilled,
            'id': attrs['id'],
            'view': list_view,
            'capitalize': capitalize,
        }

        return mark_safe("\n".join([html, js]))

    class Media:
        base_url = '{0}tagging/tagmanager-2.4.2/'.format(settings.STATIC_URL)
        bootstrap_base_url = '{0}tagging/bootstrap/'.format(settings.STATIC_URL)

        js = [
            base_url + 'bootstrap-tagmanager.js',
        ]

        css_list = [
            base_url + 'bootstrap-tagmanager.css',
        ]

        if conf.INCLUDE_BOOTSTRAP:
            js.append(bootstrap_base_url + 'bootstrap-typeahead.js')
            #css_list.append(bootstrap_base_url + 'css/bootstrap.css')

        css = {
            'screen': css_list,
        }
