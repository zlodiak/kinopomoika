from django.db import models

from tagging.fields import TagField
from tagging.managers import ModelTaggedItemManager, ModelTagManager, TagDescriptor

class Perch(models.Model):
    size = models.IntegerField()
    smelly = models.BooleanField(default=True)

class Parrot(models.Model):
    state = models.CharField(max_length=50)
    perch = models.ForeignKey(Perch, null=True)

    objects = models.Manager()

    tagged = ModelTagManager()
    tagged_items = ModelTaggedItemManager()
    tags = TagDescriptor()
    spam = TagDescriptor(namespace='spam')
    spam2 = TagDescriptor(namespace='spam')
    attrs = TagDescriptor(namespace='attr')

    def __unicode__(self):
        return self.state

    class Meta:
        ordering = ['state']

class Link(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Article(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

class FormTest(models.Model):
    tags = TagField('Test', help_text='Test')

class FormTestNull(models.Model):
    tags = TagField(null=True)

class DefaultNamespaceTest(models.Model):
    categories = TagField('Categories', namespace='category')

class DefaultNamespaceTest2(models.Model):
    tags = TagField('Tags')
    categories = TagField('Categories', namespace='category')

class DefaultNamespaceTest3(models.Model):
    foos = TagField('Foobars', namespace='foo')
    categories = TagField('Categories', namespace='category')
