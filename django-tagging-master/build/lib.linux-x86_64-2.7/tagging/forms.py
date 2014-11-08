#coding: utf-8
from __future__ import unicode_literals, absolute_import
"""
Tagging components for Django's form library.
"""
from django import forms
from django.utils.translation import ugettext as _

from tagging import conf
from tagging.models import Tag
from tagging.utils import check_tag_length, get_tag_parts, parse_tag_input

class TagAdminForm(forms.ModelForm):
    class Meta:
        model = Tag

    def _clean_field(self, field_name, max_length, error_msg):
        value = self.cleaned_data[field_name]
        if '"' in value:
            raise forms.ValidationError(
                _("""The '"' character is not allowed."""))
        if max_length > 0 and len(value) > max_length:
            raise forms.ValidationError(error_msg % max_length)
        return value

    def clean(self):
        if conf.MAX_TAG_LENGTH:
            total_length = sum((
                len(self.cleaned_data.get('namespace', '')),
                len(self.cleaned_data.get('name', '')),
                len(self.cleaned_data.get('value', '')),
            ))
            if total_length > conf.MAX_TAG_LENGTH:
                raise forms.ValidationError(
                    _('A tag may be no more than %s characters long.') %
                        conf.MAX_TAG_LENGTH)
        return self.cleaned_data

    def clean_namespace(self):
        return self._clean_field('namespace', conf.MAX_TAG_NAMESPACE_LENGTH,
             _('A tag\'s namespace may be no more than %s characters long.'))

    def clean_name(self):
        return self._clean_field('name', conf.MAX_TAG_NAME_LENGTH,
            _('A tag\'s name may be no more than %s characters long.'))

    def clean_value(self):
        return self._clean_field('value', conf.MAX_TAG_VALUE_LENGTH,
            _('A tag\'s value may be no more than %s characters long.'))


class TagField(forms.CharField):
    """
    A ``CharField`` which validates that its input is a valid list of
    tag names and checks the allowed length of the tag parts.
    """
    def __init__(self, *args, **kwargs):
        if 'default_namespace' in kwargs:
            self.default_namespace = kwargs.pop('default_namespace')
        else:
            self.default_namespace = None
        super(TagField, self).__init__(*args, **kwargs)

    def clean(self, value):
        value = super(TagField, self).clean(value)
        if value == u'':
            return value
        for tag_name in parse_tag_input(value, default_namespace=self.default_namespace):
            try:
                check_tag_length(get_tag_parts(tag_name))
            except ValueError, e:
                if len(e.args) < 3:
                    raise
                part, max_len = e.args[1:3]
                if part == 'tag':
                    raise forms.ValidationError(_('Each tag may be no more than %s characters long.') % max_len)
                elif part == 'namespace':
                    raise forms.ValidationError(_('Each tag\'s namespace may be no more than %s characters long.') % max_len)
                elif part == 'name':
                    raise forms.ValidationError(_('Each tag\'s name may be no more than %s characters long.') % max_len)
                elif part == 'value':
                    raise forms.ValidationError(_('Each tag\'s value may be no more than %s characters long.') % max_len)
                else:
                    raise
        return value
