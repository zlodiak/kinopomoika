#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import signals, Q
from django.db.models.fields import CharField

from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from tagging import conf, forms
from tagging.models import Tag
from tagging.utils import edit_string_for_tags

WIDGET_MODULE = import_module(conf.WIDGET)
if not hasattr(WIDGET_MODULE, 'TagWidget'):
    raise ImproperlyConfigured('Wrong widget module `{}`'.format(conf.WIDGET))


class TagField(CharField):
    """
    A "special" character field that actually works as a relationship to tags
    "under the hood". This exposes a space-separated string of tags, but does
    the splitting/reordering/etc. under the hood.

    This field will only accept tags from a specific namespace if the
    ``namespace`` parameter is given. Any athor tag that is assigned will be
    thrown away.
    """

    def __init__(self, *args, **kwargs):
        self.namespace = kwargs.pop('namespace', None)
        self.max_tags = kwargs.pop('max_tags', None)
        kwargs['max_length'] = kwargs.get('max_length', 255)
        kwargs['blank'] = kwargs.get('blank', True)
        kwargs['default'] = kwargs.get('default', '')
        super(TagField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(TagField, self).contribute_to_class(cls, name)

        # Make this object the descriptor for field access.
        setattr(cls, self.name, self)

        # Save tags back to the database post-save
        signals.post_save.connect(self._save, cls, True)

        # Update tags from Tag objects post-init
        signals.post_init.connect(self._update, cls, True)

    def _get_edit_string_for_tags(self, owner=None, instance=None):
        kwargs = {'default_namespace': self.namespace}
        # if there are more than one tag field on this model,
        # skip the tags with namespaces of athor fields.
        # Thats their domain.
        if self.namespace is not None:
            kwargs['filter_namespaces'] = (self.namespace,)
        elif self._has_instance_multiple_tag_fields:
            kwargs['exclude_namespaces'] = self._foreign_namespaces

        # Handle access on the model (i.e. Link.tags)
        if instance is None:
            queryset = Tag.objects.usage_for_model(owner)
        # Handle access on the model instance
        else:
            queryset = Tag.objects.get_for_object(instance)
        return edit_string_for_tags(queryset, **kwargs)

    def __get__(self, instance, owner=None):
        """
        Tag getter. Returns an instance's tags if accessed on an instance, and
        all of a model's tags if called on a class. That is, this model::

           class Link(models.Model):
               ...
               tags = TagField()

        Lets you do both of these::

           >>> l = Link.objects.get(...)
           >>> l.tags
           'tag1 tag2 tag3'

           >>> Link.tags
           'tag1 tag2 tag3 tag4'

        """
        self._init(owner or instance)
        if instance is None:
            return self._get_edit_string_for_tags(owner=owner)
        return self._get_instance_tag_cache(instance)

    def __set__(self, instance, value):
        """
        Set an object's tags.
        """
        if instance is None:
            raise AttributeError(
                _('%s can only be set on instances.') % self.name)
        if value is None:
            value = u''
        if conf.FORCE_LOWERCASE_TAGS:
            value = value.lower()
        self._set_instance_tag_cache(instance, value)

    def _init(self, instance):
        """
        Check if the model has more than one tag field and collects the default
        namespaces of athor tag fields.
        """
        # check if already initialized
        if  hasattr(self, '_has_instance_multiple_tag_fields') and \
            hasattr(self, '_foreign_namespaces'):
                return
        # any athor tag fields of the model
        tag_fields = []
        for field in instance._meta.fields:
            if isinstance(field, self.__class__) and field is not self:
                tag_fields.append(field)
        self._foreign_namespaces = set()
        self._has_instance_multiple_tag_fields = False
        if len(tag_fields):
            self._has_instance_multiple_tag_fields = True
            for field in tag_fields:
                if  field.namespace is not None and\
                    field.namespace != self.namespace:
                    self._foreign_namespaces.add(field.namespace)

    def _save(self, **kwargs): #signal, sender, instance):
        """
        Save tags back to the database
        """
        instance = kwargs['instance']
        tags = self._get_instance_tag_cache(kwargs['instance'])
        q = Q()
        if self.namespace is not None:
            q &= Q(namespace=self.namespace)
        elif self._has_instance_multiple_tag_fields and \
                self._foreign_namespaces:
            q &= ~Q(namespace__in=self._foreign_namespaces)
        Tag.objects.update_tags(instance, tags, q=q,
            default_namespace=self.namespace)

    def _update(self, **kwargs): #signal, sender, instance):
        """
        Update tag cache from TaggedItem objects.
        """
        instance = kwargs['instance']
        self._init(instance)
        self._update_instance_tag_cache(instance)

    def __delete__(self, instance):
        """
        Clear all of an object's tags.
        """
        self._set_instance_tag_cache(instance, '')

    def _get_instance_tag_cache(self, instance):
        """
        Helper: get an instance's tag cache.
        """
        return getattr(instance, '_%s_cache' % self.attname, None)

    def _set_instance_tag_cache(self, instance, tags):
        """
        Helper: set an instance's tag cache.
        """
        self._init(instance)
        # If there is a tag field with a namespace, make sure that this field
        # only gets the tags that are allowed.
        if tags and (
                self._has_instance_multiple_tag_fields or
                self.namespace is not None
            ):
            kwargs = {'default_namespace': self.namespace}
            if  self.namespace is None:
                kwargs['exclude_namespaces'] = self._foreign_namespaces
            else:
                kwargs['filter_namespaces'] = (self.namespace,)
            tags = edit_string_for_tags(tags, **kwargs)
        setattr(instance, '_%s_cache' % self.attname, tags)

    def _update_instance_tag_cache(self, instance):
        """
        Helper: update an instance's tag cache from actual Tags.
        """
        # for an unsaved object, leave the default value alone
        if instance.pk is not None:
            tags = self._get_edit_string_for_tags(instance=instance)
            self._set_instance_tag_cache(instance, tags)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        widget_kwargs = {
            'max_tags': self.max_tags,
            'namespace': self.namespace
        }

        defaults = {
            'form_class': forms.TagField,
            'default_namespace': self.namespace,
        }
        defaults.update(kwargs)

        defaults['widget'] = WIDGET_MODULE.TagWidget(**widget_kwargs)

        return super(TagField, self).formfield(**defaults)

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)


def validate_tag_fields(sender, **kwargs):
    '''
    Validates ``TagField``s on models.
    '''
    namespaces = set()
    for field in sender._meta.fields:
        if isinstance(field, TagField):
            if field.namespace in namespaces:
                import sys
                from django.core.management.color import color_style
                style = color_style()
                e = (
                    u"You specified more than one tag field with the "
                    u"namespace '%s' on the model '%s.%s'. Please make "
                    u"sure that there are only tag fields with different "
                    u"namespaces on the same model." % (
                        field.namespace,
                        sender._meta.app_label,
                        sender._meta.object_name)
                )
                sys.stderr.write(style.ERROR(str('Error: %s\n' % e)))
                sys.exit(1)
            namespaces.add(field.namespace)

signals.class_prepared.connect(validate_tag_fields)
