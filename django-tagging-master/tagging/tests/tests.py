# -*- coding: utf-8 -*-

import sys, os
from django import forms
from django.db import models
from django.db.models import Q
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from tagging.forms import TagAdminForm, TagField
from tagging import conf
from tagging.generic import fetch_content_objects
from tagging.models import Tag, TaggedItem
from tagging.tests.models import Article, Link, Perch, Parrot, FormTest, FormTestNull, DefaultNamespaceTest, DefaultNamespaceTest2, DefaultNamespaceTest3
from tagging.utils import calculate_cloud, check_tag_length, edit_string_for_tags, get_tag_list, get_tag_parts, get_tag, parse_tag_input, split_strip
from tagging.utils import LINEAR

#############
# Utilities #
#############

class TestParseTagInput(TestCase):
    def test_with_simple_space_delimited_tags(self):
        """ Test with simple space-delimited tags. """
        
        self.assertEquals(parse_tag_input('one'), [u'one'])
        self.assertEquals(parse_tag_input('one two'), [u'one', u'two'])
        self.assertEquals(parse_tag_input('one two three'), [u'one', u'three', u'two'])
        self.assertEquals(parse_tag_input('one one two two'), [u'one', u'two'])
        self.assertEquals(parse_tag_input('first:one'), [u'first:one'])
        self.assertEquals(parse_tag_input('first:one two'), [u'first:one', u'two'])
        self.assertEquals(parse_tag_input('one= second:two :three'),
            [u'one', u'second:two', u'three'])
        self.assertEquals(parse_tag_input(':one= :two= =three:'),
            [u'one', u'three', u'two'])
        self.assertEquals(parse_tag_input('=one=two :three:four'),
            [u'"three:four"', u'one=two'])
        self.assertEquals(parse_tag_input(':=one:two=three=:'),
            [u'"one:two"="three=:"'])
        self.assertEquals(parse_tag_input('second:one first:one'),
            [u'first:one', u'second:one'])
        self.assertEquals(parse_tag_input('first:one first:two'),
            [u'first:one', u'first:two'])
        self.assertEquals(parse_tag_input('first:one first:one second:one'),
            [u'first:one', u'second:one'])
        self.assertEquals(parse_tag_input('one=two'), [u'one=two'])
        self.assertEquals(parse_tag_input('three=four one=two'),
            [u'one=two', u'three=four'])
        self.assertEquals(parse_tag_input('one=two one=three'),
            [u'one=three', u'one=two'])
        self.assertEquals(parse_tag_input('first:one=two'), [u'first:one=two'])
        self.assertEquals(parse_tag_input('second:one=three first:one=two'),
            [u'first:one=two', u'second:one=three'])
        self.assertEquals(parse_tag_input('first:one:two=three:four=five'),
            [u'first:"one:two"="three:four=five"'])
    
    def test_with_comma_delimited_multiple_words(self):
        """ Test with comma-delimited multiple words.
            An unquoted comma in the input will trigger this. """
            
        self.assertEquals(parse_tag_input(',one'), [u'one'])
        self.assertEquals(parse_tag_input(',one two'), [u'one two'])
        self.assertEquals(parse_tag_input('one two,'), [u'one two'])
        self.assertEquals(parse_tag_input(',one two three'), [u'one two three'])
        self.assertEquals(parse_tag_input('one two three,'), [u'one two three'])
        self.assertEquals(parse_tag_input('a-one, a-two and a-three'),
            [u'a-one', u'a-two and a-three'])
        self.assertEquals(parse_tag_input('a:one, a:two and a=three'),
            [u'a:one', u'a:two and a=three'])
        self.assertEquals(parse_tag_input('a:one, a:two and a:three'),
            [u'a:"two and a:three"', u'a:one'])
        self.assertEquals(parse_tag_input('a:one, a:one=two a:one=two'),
            [u'a:one', u'a:one="two a:one=two"'])
    
    def test_with_double_quoted_multiple_words(self):
        """ Test with double-quoted multiple words.
            A completed quote will trigger this.  Unclosed quotes are ignored. """
            
        self.assertEquals(parse_tag_input('"one'), [u'one'])
        self.assertEquals(parse_tag_input('one"'), [u'one'])
        self.assertEquals(parse_tag_input('"one two'), [u'one', u'two'])
        self.assertEquals(parse_tag_input('"one two three'), [u'one', u'three', u'two'])
        self.assertEquals(parse_tag_input('"one two"'), [u'one two'])
        self.assertEquals(parse_tag_input('a-one "a-two and a-three"'),
            [u'a-one', u'a-two and a-three'])
        self.assertEquals(parse_tag_input('"one""two" "three"'), [u'onetwo', u'three'])
        self.assertEquals(parse_tag_input('":one'), [u'one'])
        self.assertEquals(parse_tag_input('one="'), [u'one'])
        self.assertEquals(parse_tag_input('"one:two"'), [u'"one:two"'])
        self.assertEquals(parse_tag_input('one:"two three"'), [u'one:two three'])
        self.assertEquals(parse_tag_input('"one:"two"=three"'), [u'"one:two=three"'])
        self.assertEquals(parse_tag_input('"one:"two"=three'), [u'"one:two"=three'])
        self.assertEquals(parse_tag_input(':"=one":two=three=:'),
            [u'"=one:two"="three=:"'])
    
    def test_with_no_loose_commas(self):
        """ Test with no loose commas -- split on spaces. """
        self.assertEquals(parse_tag_input('one two "thr,ee"'), [u'one', u'thr,ee', u'two'])
        self.assertEquals(parse_tag_input('one two:"thr,ee"'), [u'one', u'two:thr,ee'])
        self.assertEquals(parse_tag_input('one:two three=four'), [u'one:two', u'three=four'])
        
    def test_with_loose_commas(self):
        """ Loose commas - split on commas """
        self.assertEquals(parse_tag_input('"one", two three'), [u'one', u'two three'])
        self.assertEquals(parse_tag_input('"one", two:three four=five'),
            [u'one', u'two:three four=five'])
        
    def test_tags_with_double_quotes_can_contain_commas(self):
        """ Double quotes can contain commas """
        self.assertEquals(parse_tag_input('a-one "a-two, and a-three"'),
            [u'a-one', u'a-two, and a-three'])
        self.assertEquals(parse_tag_input('"two", one, one, two, "one"'),
            [u'one', u'two'])
    
    def test_with_naughty_input(self):
        """ Test with naughty input. """
        
        # Bad users! Naughty users!
        self.assertEquals(parse_tag_input(None), [])
        self.assertEquals(parse_tag_input(''), [])
        self.assertEquals(parse_tag_input('"'), [])
        self.assertEquals(parse_tag_input('""'), [])
        self.assertEquals(parse_tag_input('"' * 7), [])
        self.assertEquals(parse_tag_input(',,,,,,'), [])
        self.assertEquals(parse_tag_input('",",",",",",","'), [u','])
        self.assertEquals(parse_tag_input(':'), [])
        self.assertEquals(parse_tag_input(':::::::'), [u'"::::::"'])
        self.assertEquals(parse_tag_input('='), [])
        self.assertEquals(parse_tag_input('=' * 7), [])
        self.assertEquals(parse_tag_input(':,:,=,=,:,=,:,='), [])
        self.assertEquals(parse_tag_input(':= := =: =: : = = :'), [])
        self.assertEquals(parse_tag_input('":":":":"="="=":"="'), [u'":":"::="="=:="'])
        self.assertEquals(parse_tag_input('foo: =bar'), [u'bar', u'foo'])
        self.assertEquals(parse_tag_input('a-one "a-two" and "a-three'),
            [u'a-one', u'a-three', u'a-two', u'and'])
    
    def test_with_asterisks(self):
        self.assertEquals(parse_tag_input('*:foo bar=*'), [u'*:foo', u'bar=*'])
        self.assertEquals(parse_tag_input('*'), ['*'])
        self.assertEquals(parse_tag_input('foo:*=bar'), [u'foo:*=bar'])
        self.assertEquals(parse_tag_input(':*:='), [u'"*:"'])
        self.assertEquals(parse_tag_input('"*":foo bar="*"'), [u'*:foo', u'bar=*'])
        self.assertEquals(parse_tag_input('"*"'), ['*'])
        self.assertEquals(parse_tag_input('foo:"*"=bar'), [u'foo:*=bar'])
        self.assertEquals(parse_tag_input(':"*":='), [u'"*:"'])
    
    def test_keep_quotes(self):
        self.assertEquals(parse_tag_input('*:foo bar=*', keep_quotes=['*']), [u'*:foo', u'bar=*'])
        self.assertEquals(parse_tag_input('"*":foo bar=*', keep_quotes=['*']), [u'"*":foo', u'bar=*'])
        self.assertEquals(parse_tag_input('"*":foo bar="*"', keep_quotes=['*']), [u'"*":foo', u'bar="*"'])
        self.assertEquals(parse_tag_input('"*"', keep_quotes=['*']), ['"*"'])
        self.assertEquals(parse_tag_input('*', keep_quotes=['*']), ['*'])
        self.assertEquals(parse_tag_input('foo:*=bar', keep_quotes=['*']), [u'foo:*=bar'])
        self.assertEquals(parse_tag_input('foo:"*"=bar', keep_quotes=['*']), [u'foo:"*"=bar'])
    
    def test_default_namespace(self):
        self.assertEquals(parse_tag_input('bar', default_namespace='foo'), [u'foo:bar'])
        self.assertEquals(parse_tag_input('bar :bar', default_namespace='foo'), [u'bar', u'foo:bar'])
        self.assertEquals(parse_tag_input('foo:bar bar', default_namespace='foo'), [u'foo:bar'])
        self.assertEquals(parse_tag_input('bar=baz', default_namespace='foo'), [u'foo:bar=baz'])
        self.assertEquals(parse_tag_input('bar=baz', default_namespace='col:on'), [u'"col:on":bar=baz'])
        
        self.assertEquals(parse_tag_input('bar', default_namespace='foo'), [u'foo:bar'])
        self.assertEquals(parse_tag_input('bar foo', default_namespace='foo'), [u'foo:bar', u'foo:foo'])
        self.assertEquals(parse_tag_input('bar=foo', default_namespace='foo'), [u'foo:bar=foo'])
        self.assertEquals(parse_tag_input(':bar', default_namespace='foo'), [u'bar'], [u'foo:bar'])
        self.assertEquals(parse_tag_input('"":bar', default_namespace='foo'), [u'bar'], [u'foo:bar'])
        self.assertEquals(parse_tag_input('space:bar foo=value', default_namespace='foo'), [u'foo:foo=value', u'space:bar'])
        self.assertEquals(parse_tag_input('foo: foo:foo', default_namespace='foo'), [u'foo:foo'])
        self.assertEquals(parse_tag_input('space:"bar foo"=value', default_namespace='foo'), [u'space:bar foo=value'])
        self.assertEquals(parse_tag_input('space:bar foo=value, baz ter', default_namespace='foo'), [u'foo:baz ter', u'space:bar foo=value'])
        self.assertEquals(parse_tag_input('foo bar', default_namespace='col:on'), [u'"col:on":bar', u'"col:on":foo'])
        self.assertEquals(parse_tag_input('foo bar', default_namespace='spa ce'), [u'spa ce:bar', u'spa ce:foo'])
        self.assertEquals(parse_tag_input('foo bar', default_namespace='equ=al'), [u'"equ=al":bar', u'"equ=al":foo'])
        self.assertEquals(parse_tag_input(' ', default_namespace='equ=al'), [])

class TestSplitStrip(TestCase):
    def test_with_empty_input(self):
        self.assertEquals(split_strip(' foo '), [u'foo'])
        self.assertEquals(split_strip(' foo , bar '), [u'foo', u'bar'])
        self.assertEquals(split_strip(', foo , bar ,'), [u'foo', u'bar'])
        self.assertEquals(split_strip(None), [])
    
    def test_with_different_whitespace(self):
        self.assertEquals(split_strip(' foo\t,\nbar '), [u'foo', u'bar'])

    def test_with_athor_delimiter(self):
        self.assertEquals(split_strip(' foo bar ', ' '), [u'foo', u'bar'])
    
    def test_non_empty_input(self):
        self.assertEquals(split_strip(''), [])
        self.assertEquals(split_strip(None), [])

class TestNormalisedTagListInput(TestCase):
    def setUp(self):
        self.cheese = Tag.objects.create(name='cheese')
        self.toast = Tag.objects.create(name='toast')
        self.food_cheese = Tag.objects.create(namespace='food', name='cheese')
        self.food_egg = Tag.objects.create(namespace='food', name='egg')
        self.star_cheese_none = Tag.objects.create(namespace='*', name='cheese')
        self.star_cheese_star = Tag.objects.create(namespace='*', name='cheese', value='*')
        self.none_cheese_star = Tag.objects.create(name='cheese', value='*')
        self.cheese_star_none = Tag.objects.create(namespace='cheese', name='*')
    
    def test_single_tag_object_as_input(self):
        self.assertEquals(get_tag_list(self.cheese), [self.cheese])
    
    def test_single_string_as_input(self):
        ret = get_tag_list('cheese')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.cheese in ret)
        ret = get_tag_list('food:egg')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.food_egg in ret)
    
    def test_space_delimeted_string_as_input(self):
        ret = get_tag_list('cheese toast')
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
    def test_comma_delimeted_string_as_input(self):
        ret = get_tag_list('cheese,toast')
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
    def test_namespaced_string_as_input(self):
        ret = get_tag_list('cheese food:egg')
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.food_egg in ret)
    
    def test_invalid_string_as_input(self):
        ret = get_tag_list('=')
        self.assertEquals(len(ret), 0)
        ret = get_tag_list(':')
        self.assertEquals(len(ret), 0)
        ret = get_tag_list('"":""=""')
        self.assertEquals(len(ret), 0)
    
    def test_list_of_invalid_string_as_input(self):
        ret = get_tag_list([''])
        self.assertEquals(len(ret), 0)
        ret = get_tag_list(['='])
        self.assertEquals(len(ret), 0)
        ret = get_tag_list([':'])
        self.assertEquals(len(ret), 0)
        ret = get_tag_list(['"":""=""'])
        self.assertEquals(len(ret), 0)
    
    def test_with_empty_list(self):
        self.assertEquals(get_tag_list([]), [])

    def test_with_single_tag_instance(self):
        ret = get_tag_list(self.cheese)
        self.assertEquals(len(ret), 1)
        self.failUnless(self.cheese in ret)
    
    def test_list_of_two_strings(self):
        ret = get_tag_list(['cheese', 'toast'])
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
        ret = get_tag_list(['cheese', 'food:egg'])
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.food_egg in ret)
    
    def test_list_of_tag_primary_keys(self):
        ret = get_tag_list([self.cheese.id, self.toast.id])
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
    def test_list_of_strings_with_strange_nontag_string(self):
        ret = get_tag_list(['cheese', 'toast', 'ŠĐĆŽćžšđ'])
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
    def test_list_of_tag_instances(self):
        ret = get_tag_list([self.cheese, self.toast])
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
    def test_tuple_of_instances(self):
        ret = get_tag_list((self.cheese, self.toast))
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
    
    def test_with_tag_filter(self):
        ret = get_tag_list(Tag.objects.filter(name__in=['cheese', 'toast']))
        self.assertEquals(len(ret), 6)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.toast in ret)
        self.failUnless(self.none_cheese_star in ret)
        self.failUnless(self.star_cheese_star in ret)
        self.failUnless(self.star_cheese_none in ret)
        
    def test_with_invalid_input_mix_of_string_and_instance(self):
        try:
            get_tag_list(['cheese', self.toast])
        except ValueError, ve:
            self.assertEquals(str(ve),
                'If a list or tuple of tags is provided, they must all be tag names, Tag objects or Tag ids.')
        except Exception, e:
            raise self.failureException('the wrong type of exception was raised: type [%s] value [%]' %\
                (str(type(e)), str(e)))
        else:
            raise self.failureException('a ValueError exception was supposed to be raised!')
    
    def test_with_invalid_input(self):
        try:
            get_tag_list(29)
        except ValueError, ve:
            self.assertEquals(str(ve), 'The tag input given was invalid.')
        except Exception, e:
            raise self.failureException('the wrong type of exception was raised: type [%s] value [%s]' %\
                (str(type(e)), str(e)))
        else:
            raise self.failureException('a ValueError exception was supposed to be raised!')

    def test_with_asterisks(self):
        ret = get_tag_list('*:cheese')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.star_cheese_none in ret)

        ret = get_tag_list('cheese:*')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.cheese_star_none in ret)

        ret = get_tag_list('*:cheese=*')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.star_cheese_star in ret)

        ret = get_tag_list('cheese=*')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.none_cheese_star in ret)

    def test_with_wildcards(self):
        ret = get_tag_list('*:cheese', wildcard='*')
        self.assertEquals(len(ret), 3)
        self.failUnless(self.star_cheese_none in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.cheese in ret)

        ret = get_tag_list('cheese:*', wildcard='*')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.cheese_star_none in ret)

        ret = get_tag_list('*:cheese=*', wildcard='*')
        self.assertEquals(len(ret), 5)
        self.failUnless(self.star_cheese_none in ret)
        self.failUnless(self.star_cheese_star in ret)
        self.failUnless(self.none_cheese_star in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.cheese in ret)

        # you can quote the wildcard
        ret = get_tag_list('"*":cheese="*"', wildcard='*')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.star_cheese_star in ret)

        ret = get_tag_list('cheese=*', wildcard='*')
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.none_cheese_star in ret)

        # you can use any string as wildcard
        ret = get_tag_list('cheese=*', wildcard='cheese')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.none_cheese_star in ret)

        ret = get_tag_list('*:*=*', wildcard='*')
        self.assertEquals(len(ret), 8)
        self.failUnless(self.star_cheese_none in ret)
        self.failUnless(self.star_cheese_star in ret)
        self.failUnless(self.none_cheese_star in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.toast in ret)
        self.failUnless(self.food_egg in ret)
    
    def test_with_default_namespace(self):
        ret = get_tag_list('cheese', default_namespace='food')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.food_cheese in ret)
        
        ret = get_tag_list(':cheese', default_namespace='food')
        self.assertEquals(len(ret), 1)
        self.failUnless(self.cheese in ret)
        
        ret = get_tag_list('cheese :cheese', default_namespace='food')
        self.assertEquals(len(ret), 2)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.food_cheese in ret)

    def test_with_wildcard_and_default_namespace(self):
        ret = get_tag_list('*:cheese', wildcard='*', default_namespace='food')
        self.assertEquals(len(ret), 3)
        self.failUnless(self.star_cheese_none in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.cheese in ret)
    
        ret = get_tag_list('*:cheese egg', wildcard='*', default_namespace='food')
        self.assertEquals(len(ret), 4)
        self.failUnless(self.star_cheese_none in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.food_egg in ret)
    
        ret = get_tag_list(['*:cheese', 'egg'], wildcard='*', default_namespace='food')
        self.assertEquals(len(ret), 4)
        self.failUnless(self.star_cheese_none in ret)
        self.failUnless(self.food_cheese in ret)
        self.failUnless(self.cheese in ret)
        self.failUnless(self.food_egg in ret)
    
    def test_with_tag_instance(self):
        self.assertEquals(get_tag(self.cheese), self.cheese)
        self.assertEquals(get_tag(self.cheese), self.cheese)
    
    def test_with_string(self):
        self.assertEquals(get_tag('cheese'), self.cheese)
    
    def test_with_primary_key(self):
        self.assertEquals(get_tag(self.cheese.id), self.cheese)
    
    def test_nonexistent_tag(self):
        self.assertEquals(get_tag('mouse'), None)

    def test_get_tag_with_default_namespace(self):
        self.assertEquals(get_tag('cheese', default_namespace='food'), self.food_cheese)
        self.assertEquals(get_tag(':cheese', default_namespace='food'), self.cheese)
        self.assertEquals(get_tag('*:cheese', default_namespace='food'), self.star_cheese_none)

class TestCalculateCloud(TestCase):
    def setUp(self):
        self.tags = []
        for line in open(os.path.join(os.path.dirname(__file__), 'tags.txt')).readlines():
            parts, count = line.rstrip().split()
            tag = Tag(**get_tag_parts(parts))
            tag.count = int(count)
            self.tags.append(tag)
    
    def test_default_distribution(self):
        sizes = {}
        for tag in calculate_cloud(self.tags, steps=5):
            sizes[tag.font_size] = sizes.get(tag.font_size, 0) + 1
        
        # This isn't a pre-calculated test, just making sure it's consistent
        self.assertEquals(sizes[1], 48)
        self.assertEquals(sizes[2], 30)
        self.assertEquals(sizes[3], 19)
        self.assertEquals(sizes[4], 15)
        self.assertEquals(sizes[5], 10)
    
    def test_linear_distribution(self):
        sizes = {}
        for tag in calculate_cloud(self.tags, steps=5, distribution=LINEAR):
            sizes[tag.font_size] = sizes.get(tag.font_size, 0) + 1
        
        # This isn't a pre-calculated test, just making sure it's consistent
        self.assertEquals(sizes[1], 97)
        self.assertEquals(sizes[2], 12)
        self.assertEquals(sizes[3], 7)
        self.assertEquals(sizes[4], 2)
        self.assertEquals(sizes[5], 4)
    
    def test_invalid_distribution(self):
        try:
            calculate_cloud(self.tags, steps=5, distribution='cheese')
        except ValueError, ve:
            self.assertEquals(str(ve), 'Invalid distribution algorithm specified: cheese.')
        except Exception, e:
            raise self.failureException('the wrong type of exception was raised: type [%s] value [%s]' %\
                (str(type(e)), str(e)))
        else:
            raise self.failureException('a ValueError exception was supposed to be raised!')

class TestGetTag(TestCase):
    def setUp(self):
        self.foo_tag = Tag.objects.create(name='foo')
        self.foobar_tag = Tag.objects.create(name='foo:bar')
        self.barbaz_tag = Tag.objects.create(name='bar=baz')
        self.bar_baz_tag = Tag.objects.create(name='bar', value='baz')
        self.foo_bar_tag = Tag.objects.create(name='bar', namespace='foo')
        self.foo_bar_baz_tag = Tag.objects.create(name='bar', namespace='foo', value='baz')
        self.one_tag = Tag.objects.create(name='two three', namespace='one', value='four')
        self.sign_tag = Tag.objects.create(name=':=', namespace=':=', value=':=')
        
    def test_simple_tags(self):
        self.failUnless(get_tag('foo'), self.foo_tag)
        self.failUnless(get_tag('"foo:bar"'), self.foobar_tag)
        self.failUnless(get_tag('foo:bar'), self.foo_bar_tag)
        self.failUnless(get_tag('"bar=baz"'), self.barbaz_tag)
        self.failUnless(get_tag('bar=baz'), self.bar_baz_tag)
        self.failUnless(get_tag('foo:bar=baz'), self.bar_baz_tag)
        self.failUnless(get_tag('"foo":"bar"="baz"'), self.bar_baz_tag)
        self.failUnless(get_tag('one:"two three"=four'), self.one_tag)
        self.failUnless(get_tag('":=":":="=":="'), self.sign_tag)

class TestGetTagParts(TestCase):
    def test_simple_cases(self):
        self.assertEquals(get_tag_parts('bar'),
            {'namespace': None, 'name': 'bar', 'value': None})
        self.assertEquals(get_tag_parts('foo:bar'),
            {'namespace': 'foo', 'name': 'bar', 'value': None})
        self.assertEquals(get_tag_parts('bar=baz'),
            {'namespace': None, 'name': 'bar', 'value': 'baz'})
        self.assertEquals(get_tag_parts('foo:bar=baz'),
            {'namespace': 'foo', 'name': 'bar', 'value': 'baz'})
        self.assertEquals(get_tag_parts(' foo: bar =baz '),
            {'namespace': ' foo', 'name': ' bar ', 'value': 'baz '})
        self.assertEquals(get_tag_parts(':foo'),
            {'namespace': None, 'name': 'foo', 'value': None})
        self.assertEquals(get_tag_parts('foo='),
            {'namespace': None, 'name': 'foo', 'value': None})

    def test_with_quotes(self):
        self.assertEquals(get_tag_parts('"bar="'),
            {'namespace': None, 'name': 'bar=', 'value': None})
        self.assertEquals(get_tag_parts('":="'),
            {'namespace': None, 'name': ':=', 'value': None})
        self.assertEquals(get_tag_parts('":=":":="=":="'),
            {'namespace': ':=', 'name': ':=', 'value': ':='})

    def test_keep_quotes(self):
        self.assertEquals(get_tag_parts('*', keep_quotes=['*']),
            {'namespace': None, 'name': '*', 'value': None})
        self.assertEquals(get_tag_parts('"*"', keep_quotes=['*']),
            {'namespace': None, 'name': '"*"', 'value': None})
        self.assertEquals(get_tag_parts('*:"*"=*', keep_quotes=['*']),
            {'namespace': '*', 'name': '"*"', 'value': '*'})
        self.assertEquals(get_tag_parts('"*":"*"="*"', keep_quotes=['*']),
            {'namespace': '"*"', 'name': '"*"', 'value': '"*"'})
        self.assertEquals(get_tag_parts('*:"*:"=*', keep_quotes=['*']),
            {'namespace': '*', 'name': '*:', 'value': '*'})
        self.assertEquals(get_tag_parts('*:"*:"=*', keep_quotes=['*']),
            {'namespace': '*', 'name': '*:', 'value': '*'})

    def test_default_namespace(self):
        self.assertEquals(get_tag_parts('bar', default_namespace='foo'),
            {'namespace': 'foo', 'name': 'bar', 'value': None})
        self.assertEquals(get_tag_parts(':bar', default_namespace='foo'),
            {'namespace': None, 'name': 'bar', 'value': None})
        self.assertEquals(get_tag_parts('foo:bar', default_namespace='foo'),
            {'namespace': 'foo', 'name': 'bar', 'value': None})
        self.assertEquals(get_tag_parts('baz:bar', default_namespace='foo'),
            {'namespace': 'baz', 'name': 'bar', 'value': None})


class TestCheckTagLength(TestCase):
    def setUp(self):
        self.original_max_tag_length = conf.MAX_TAG_LENGTH
        self.original_max_tag_name_length = conf.MAX_TAG_NAME_LENGTH
        self.original_max_tag_namespace_length = conf.MAX_TAG_NAMESPACE_LENGTH
        self.original_max_tag_value_length = conf.MAX_TAG_VALUE_LENGTH
    
    def tearDown(self):
        conf.MAX_TAG_LENGTH = self.original_max_tag_length
        conf.MAX_TAG_NAME_LENGTH = self.original_max_tag_name_length
        conf.MAX_TAG_NAMESPACE_LENGTH = self.original_max_tag_namespace_length
        conf.MAX_TAG_VALUE_LENGTH = self.original_max_tag_value_length
    
    def test_total_tag_length(self):
        conf.MAX_TAG_LENGTH = 50
        conf.MAX_TAG_NAME_LENGTH = 40
        conf.MAX_TAG_NAMESPACE_LENGTH = 10
        conf.MAX_TAG_VALUE_LENGTH = 10
        try:
            check_tag_length({'namespace': None, 'name': 'a' * 40, 'value': None})
        except Exception, e:
            self.fail(e)
        try:
            check_tag_length({'namespace': None, 'name': 'a' * 41, 'value': None})
            self.fail()
        except ValueError, ve:
            self.assertEquals(ve.args[1], 'name')
        try:
            check_tag_length({'namespace': 'a' * 10, 'name': 'a', 'value': None})
        except Exception, e:
            self.fail(e)
        try:
            check_tag_length({'namespace': 'a' * 11, 'name': 'a', 'value': None})
            self.fail()
        except ValueError, ve:
            self.assertEquals(ve.args[1], 'namespace')
        try:
            check_tag_length({'namespace': None, 'name': 'a', 'value': 'a' * 10})
        except Exception, e:
            self.fail(e)
        try:
            check_tag_length({'namespace': None, 'name': 'a', 'value': 'a' * 11})
            self.fail()
        except ValueError, ve:
            self.assertEquals(ve.args[1], 'value')
        try:
            check_tag_length({'namespace': 'a' * 10, 'name': 'a' * 30, 'value': 'a' * 10})
        except Exception, e:
            self.fail(e)
        try:
            check_tag_length({'namespace': 'a' * 10, 'name': 'a' * 30, 'value': 'a' * 11})
            self.fail()
        except ValueError, ve:
            self.assertEquals(ve.args[1], 'tag')

#########
# Model #
#########

class TestTagModel(TestCase):
    def test_unicode_behaviour(self):
        self.assertEqual(unicode(Tag(name='foo')), u'foo')
        self.assertEqual(unicode(Tag(namespace='foo', name='bar')), u'foo:bar')
        self.assertEqual(unicode(Tag(name='foo', value='bar')), u'foo=bar')
        self.assertEqual(unicode(Tag(namespace='foo', name='bar', value='baz')), u'foo:bar=baz')
        self.assertEqual(unicode(Tag(name='foo:bar')), u'"foo:bar"')
        self.assertEqual(unicode(Tag(name='foo:bar=baz')), u'"foo:bar=baz"')
        self.assertEqual(unicode(Tag(namespace='spam', name='foo:bar=baz')), u'spam:"foo:bar=baz"')
        self.assertEqual(unicode(Tag(namespace='spam', name='foo:bar=baz', value='egg')), u'spam:"foo:bar=baz"=egg')
        self.assertEqual(unicode(Tag(namespace='spam:egg', name='foo:bar=baz')), u'"spam:egg":"foo:bar=baz"')
        self.assertEqual(unicode(Tag(name='foo:bar=baz', value='spam:egg')), u'"foo:bar=baz"="spam:egg"')
        self.assertEqual(unicode(Tag(namespace=':', name=':=', value='=')), u'":":":="="="')

###########
# Manager #
###########

class TestModelTagManager(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'bar foo ter spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
    
    def test_manager_method_get_query_set(self):
        tags = Parrot.tagged.get_query_set()
        self.assertEquals(len(tags), 6)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('ter') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)
        self.failUnless(get_tag('spam:foo') in tags)

        tags = Parrot.tagged.all()
        self.assertEquals(len(tags), 6)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('ter') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)
        self.failUnless(get_tag('spam:foo') in tags)

    def test_manager_method_cloud(self):
        cloud_tags = Parrot.tagged.cloud()
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 6)
        self.failUnless((u'bar', 4, 4) in relevant_attribute_list)
        self.failUnless((u'ter', 3, 3) in relevant_attribute_list)
        self.failUnless((u'foo', 2, 2) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2, 2) in relevant_attribute_list)
        self.failUnless((u'baz', 1, 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1, 1) in relevant_attribute_list)

    def test_manager_method_related(self):
        related_tags = Parrot.tagged.related('bar ter', counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 4)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)

    def test_manager_method_usage(self):
        tag_usage = Parrot.tagged.usage(counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 6)
        self.failUnless((u'bar', 4) in relevant_attribute_list)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 3) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)

class TestModelTaggedItemManager(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'baz ter'),
            ('no more',               4, True,  'foo spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
        
        self.pining_for_the_fjords_parrot = Parrot.objects.get(state='pining for the fjords')
        self.passed_on_parrot = Parrot.objects.get(state='passed on')
        self.no_more_parrot = Parrot.objects.get(state='no more')
        self.late_parrot = Parrot.objects.get(state='late')
    
    def test_manager_method_related_to(self):
        related_objs = Parrot.tagged_items.related_to(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(related_objs), 2)
        self.assertEquals(related_objs, [self.no_more_parrot, self.late_parrot])

        related_objs = Parrot.tagged_items.related_to(self.late_parrot, Parrot.objects.filter(perch__smelly=False))
        self.assertEquals(len(related_objs), 1)
        self.assertEquals(related_objs, [self.passed_on_parrot])

        related_objs = Parrot.tagged_items.related_to(self.pining_for_the_fjords_parrot, num=1)
        self.assertEquals(len(related_objs), 1)
        self.assertEquals(related_objs, [self.no_more_parrot])

        related_objs = Parrot.tagged_items.related_to(self.pining_for_the_fjords_parrot, Parrot.objects.exclude(state__startswith='p'), num=1)
        self.assertEquals(len(related_objs), 1)
        self.assertEquals(related_objs, [self.no_more_parrot])

    def test_manager_method_with_all(self):
        related_objs = Parrot.tagged_items.with_all('foo spam:egg=ham')
        self.assertEquals(len(related_objs), 2)
        self.failUnless(self.pining_for_the_fjords_parrot in related_objs)
        self.failUnless(self.no_more_parrot in related_objs)

        related_objs = Parrot.tagged_items.with_all('foo spam:egg=ham', Parrot.objects.filter(state__startswith='p'))
        self.assertEquals(len(related_objs), 1)
        self.failUnless(self.pining_for_the_fjords_parrot in related_objs)

    def test_manager_method_with_any(self):
        related_objs = Parrot.tagged_items.with_any('bar ter')
        self.assertEquals(len(related_objs), 3)
        self.failUnless(self.pining_for_the_fjords_parrot in related_objs)
        self.failUnless(self.passed_on_parrot in related_objs)
        self.failUnless(self.late_parrot in related_objs)

        related_objs = Parrot.tagged_items.with_any('bar ter', Parrot.objects.filter(state__startswith='p'))
        self.assertEquals(len(related_objs), 2)
        self.failUnless(self.pining_for_the_fjords_parrot in related_objs)
        self.failUnless(self.passed_on_parrot in related_objs)

class TestTagDescriptor(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'baz ter'),
            ('no more',               4, True,  'foo spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
        
        self.pining_for_the_fjords_parrot = Parrot.objects.get(state='pining for the fjords')
        self.passed_on_parrot = Parrot.objects.get(state='passed on')
        self.no_more_parrot = Parrot.objects.get(state='no more')
        self.late_parrot = Parrot.objects.get(state='late')
        
    def test_descriptors_get_method(self):
        tags = Parrot.tags.all()
        self.assertEquals(len(tags), 6)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('ter') in tags)
        self.failUnless(get_tag('spam:foo') in tags)

        tags = self.pining_for_the_fjords_parrot.tags
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)
        
    def test_descriptors_set_method(self):
        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)

        self.pining_for_the_fjords_parrot.tags = 'foo baz spam:foo'
        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('spam:foo') in tags)

        self.pining_for_the_fjords_parrot.tags = None
        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 0)

    def test_descriptors_del_method(self):
        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)

        del self.pining_for_the_fjords_parrot.tags
        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 0)

    def test_descriptors_with_namespace(self):
        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('spam:egg=ham') in tags)

        tags = self.pining_for_the_fjords_parrot.spam2
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('spam:egg=ham') in tags)

        self.pining_for_the_fjords_parrot.spam = 'spam:egg'
        tags = self.pining_for_the_fjords_parrot.spam
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('spam:egg') in tags)
        tags = self.pining_for_the_fjords_parrot.spam2
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('spam:egg') in tags)

        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('spam:egg') in tags)

        del self.pining_for_the_fjords_parrot.spam

        tags = self.pining_for_the_fjords_parrot.spam
        self.assertEquals(len(tags), 0)
        tags = self.pining_for_the_fjords_parrot.spam2
        self.assertEquals(len(tags), 0)

        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)

        tags = self.pining_for_the_fjords_parrot.attrs
        self.assertEquals(len(tags), 0)

        self.pining_for_the_fjords_parrot.attrs = 'fly size:big'
        tags = self.pining_for_the_fjords_parrot.attrs
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('attr:fly') in tags)

        tags = Tag.objects.get_for_object(self.pining_for_the_fjords_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('attr:fly') in tags)

###########
# Tagging #
###########

class TestBasicTagging(TestCase):
    def setUp(self):
        self.dead_parrot = Parrot.objects.create(state='dead')
    
    def test_update_tags(self):
        Tag.objects.update_tags(self.dead_parrot, 'foo,bar,"ter"')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('ter') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, '"foo" bar "baz"')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, '"foo":bar "baz"')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, '"foo":bar="baz"')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('foo:bar=baz') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'bar="baz"')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('bar=baz') in tags)

    def test_update_tags_with_default_namespace(self):
        Tag.objects.update_tags(self.dead_parrot, 'bar', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('foo:bar') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'bar foo', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('foo:foo') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'bar=foo', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('foo:bar=foo') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, ':bar', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo:bar') not in tags)
        
        Tag.objects.update_tags(self.dead_parrot, '"":bar', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo:bar') not in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'space:bar foo=value', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('space:bar') in tags)
        self.failUnless(get_tag('foo:foo=value') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'foo: foo:foo', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('foo:foo') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'space:"bar foo"=value', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('space:bar foo=value') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'space:bar foo=value, baz ter', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('space:bar foo=value') in tags)
        self.failUnless(get_tag('foo:baz ter') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'foo bar', default_namespace='col:on')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('"col:on":foo') in tags)
        self.failUnless(get_tag('"col:on":bar') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'foo bar', default_namespace='spa ce')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('spa ce:foo') in tags)
        self.failUnless(get_tag('spa ce:bar') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'foo bar', default_namespace='equ=al')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('"equ=al":foo') in tags)
        self.failUnless(get_tag('"equ=al":bar') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, ' ', default_namespace='equ=al')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 0)
        
    def test_add_tag(self):
        # start off in a known, mildly interesting state
        Tag.objects.update_tags(self.dead_parrot, 'foo bar baz')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        # try to add a tag that already exists
        Tag.objects.add_tag(self.dead_parrot, 'foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        # now add a tag that doesn't already exist
        Tag.objects.add_tag(self.dead_parrot, 'zip')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 4)
        self.failUnless(get_tag('zip') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)

        # try to add a tag that has the same name of an existing but a
        # different namespace and a tag that looks the same but quoted
        Tag.objects.add_tag(self.dead_parrot, 'foo:bar')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 5)
        self.failUnless(get_tag('zip') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        
        # try to add a tag that looks like an already existent namespaced tag
        # but is quoted
        Tag.objects.add_tag(self.dead_parrot, '"foo:bar"')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 6)
        self.failUnless(get_tag('zip') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('"foo:bar"') in tags)
        
        # now add a tag with namespace that already exists
        Tag.objects.add_tag(self.dead_parrot, 'foo:bar')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 6)
        self.failUnless(get_tag('zip') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('"foo:bar"') in tags)
        
        # add a tag with namespace and value
        Tag.objects.add_tag(self.dead_parrot, 'foo:bar=baz')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 7)
        self.failUnless(get_tag('zip') in tags)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('"foo:bar"') in tags)
        self.failUnless(get_tag('"foo":"bar"="baz"') in tags)
    
    def test_add_tag_with_default_namespace(self):
        Tag.objects.add_tag(self.dead_parrot, 'bar')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.failUnless(get_tag('bar') in tags)
        
        Tag.objects.add_tag(self.dead_parrot, 'bar', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 2)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        
        Tag.objects.add_tag(self.dead_parrot, ':baz', default_namespace='foo')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        
        Tag.objects.add_tag(self.dead_parrot, 'bar', default_namespace='col:on')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 4)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('foo:bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('"col:on":bar') in tags)
        
    def test_add_tag_invalid_input_no_tags_specified(self):
        # start off in a known, mildly interesting state
        Tag.objects.update_tags(self.dead_parrot, 'foo bar baz')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        invalid_input = ['     ', ':', '=', ':=']
        for input in invalid_input:
            try:
                Tag.objects.add_tag(self.dead_parrot, input)
            except AttributeError, ae:
                self.assertEquals(str(ae), 'No tags were given: "%s".' % input)
            except Exception, e:
                raise self.failureException('the wrong type of exception was raised: type [%s] value [%s]' %\
                    (str(type(e)), str(e)))
            else:
                raise self.failureException('an AttributeError exception was supposed to be raised!')
        
        invalid_input = ['     ', ':', '=', ':=']
        for input in invalid_input:
            try:
                Tag.objects.add_tag(self.dead_parrot, input, default_namespace='foo')
            except AttributeError, ae:
                self.assertEquals(str(ae), 'No tags were given: "%s".' % input)
            except Exception, e:
                raise self.failureException('the wrong type of exception was raised: type [%s] value [%s]' %\
                    (str(type(e)), str(e)))
            else:
                raise self.failureException('an AttributeError exception was supposed to be raised!')
        
    def test_add_tag_invalid_input_multiple_tags_specified(self):
        # start off in a known, mildly interesting state
        Tag.objects.update_tags(self.dead_parrot, 'foo bar baz')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        try:
            Tag.objects.add_tag(self.dead_parrot, 'one two')
        except AttributeError, ae:
            self.assertEquals(str(ae), 'Multiple tags were given: "one two".')
        except Exception, e:
            raise self.failureException('the wrong type of exception was raised: type [%s] value [%s]' %\
                (str(type(e)), str(e)))
        else:
            raise self.failureException('an AttributeError exception was supposed to be raised!')
    
    def test_update_tags_exotic_characters(self):
        # start off in a known, mildly interesting state
        Tag.objects.update_tags(self.dead_parrot, 'foo bar baz')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, u'ŠĐĆŽćžšđ')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.assertEquals(unicode(tags[0]), u'ŠĐĆŽćžšđ')
        
        Tag.objects.update_tags(self.dead_parrot, u'你好')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.assertEquals(unicode(tags[0]), u'你好')
        
        Tag.objects.update_tags(self.dead_parrot, u'ŠĐĆŽćžšđ', default_namespace=u'你好')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 1)
        self.assertEquals(unicode(tags[0]), u'你好:ŠĐĆŽćžšđ')
    
    def test_update_tags_with_none(self):
        # start off in a known, mildly interesting state
        Tag.objects.update_tags(self.dead_parrot, 'foo bar baz')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(get_tag('bar') in tags)
        self.failUnless(get_tag('baz') in tags)
        self.failUnless(get_tag('foo') in tags)
        
        Tag.objects.update_tags(self.dead_parrot, None)
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 0)

class TestModelTagField(TestCase):
    """ Test the 'tags' field on models. """
    
    def setUp(self):
        self.original_stderr = sys.stderr
    
    def tearDown(self):
        sys.stderr = self.original_stderr
    
    def test_create_with_tags_specified(self):
        f1 = FormTest.objects.create(tags=u'test3 test2 test1 one:"two three"=four')
        tags = Tag.objects.get_for_object(f1)
        test1_tag = get_tag('test1')
        test2_tag = get_tag('test2')
        test3_tag = get_tag('test3')
        one_tag = get_tag('one:"two three"=four')
        self.failUnless(None not in (test1_tag, test2_tag, test3_tag, one_tag))
        self.assertEquals(len(tags), 4)
        self.failUnless(test1_tag in tags)
        self.failUnless(test2_tag in tags)
        self.failUnless(test3_tag in tags)
        self.failUnless(one_tag in tags)
    
    def test_update_via_tags_field(self):
        f1 = FormTest.objects.create(tags=u'test3 test2 test1')
        tags = Tag.objects.get_for_object(f1)
        test1_tag = get_tag('test1')
        test2_tag = get_tag('test2')
        test3_tag = get_tag('test3')
        self.failUnless(None not in (test1_tag, test2_tag, test3_tag))
        self.assertEquals(len(tags), 3)
        self.failUnless(test1_tag in tags)
        self.failUnless(test2_tag in tags)
        self.failUnless(test3_tag in tags)
        
        f1.tags = u'test4'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        test4_tag = get_tag('test4')
        self.assertEquals(len(tags), 1)
        self.assertEquals(tags[0], test4_tag)
        
        f1.tags = u'foo:bar'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        foo_bar_tag = get_tag('foo:bar')
        self.assertEquals(len(tags), 1)
        self.assertEquals(tags[0], foo_bar_tag)
        
        f1.tags = ''
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 0)

    def test_single_tagfield_without_namespace(self):
        f1 = FormTest.objects.create(
            tags=u'tag1 foo:tag2 :tag3 ""tag""4=value')

        tags = Tag.objects.get_for_object(f1)
        tag1 = get_tag('tag1')
        tag2 = get_tag('foo:tag2')
        tag3 = get_tag('tag3')
        tag4 = get_tag('tag4=value')
        self.failUnless(None not in (tag1, tag2, tag3, tag4))
        self.assertEquals(len(tags), 4)
        self.failUnless(tag1 in tags)
        self.failUnless(tag2 in tags)
        self.failUnless(tag3 in tags)
        self.failUnless(tag4 in tags)
        
        self.assertEquals(FormTest.tags, u'tag1 tag3 tag4=value foo:tag2')

        # Returns the exact input string. Only works if there is one tagfield
        # on the model which also must have not a namespace assigned.
        self.assertEquals(f1.tags, u'tag1 foo:tag2 :tag3 ""tag""4=value')

        f1.tags = None
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 0)
        self.assertEquals(f1.tags, u'')

        f1.tags = u'tag3 foo:tag2'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 2)
        self.failUnless(tag2 in tags)
        self.failUnless(tag3 in tags)

        f1 = FormTest.objects.get(pk=f1.pk)

        self.assertEquals(f1.tags, u'tag3 foo:tag2')
        self.assertEquals(FormTest.tags, u'tag3 foo:tag2')
    
    def test_tagfield_with_namespace(self):
        f1 = DefaultNamespaceTest.objects.create(
            categories=u'cat1 :cat2 category:cat3 foo:cat4')
        tags = Tag.objects.get_for_object(f1)
        cat1 = get_tag('category:cat1')
        cat2 = get_tag('cat2')
        cat3 = get_tag('category:cat3')
        cat4 = get_tag('foo:cat4')
        self.failUnless(None not in (cat1, cat3))
        self.failUnless(None is cat2)
        self.failUnless(None is cat4)
        self.assertEquals(len(tags), 2)
        self.failUnless(cat1 in tags)
        self.failUnless(cat3 in tags)
        
        # not all tags of this model are shown
        self.assertEquals(DefaultNamespaceTest.categories, u'cat1 cat3')

        tag1 = Tag.objects.create(name='tag1')
        Tag.objects.add_tag(f1, unicode(tag1))
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 3)
        self.failUnless(cat1 in tags)
        self.failUnless(cat3 in tags)
        self.failUnless(tag1 in tags)
        
        # not all tags of this model are shown
        self.assertEquals(DefaultNamespaceTest.categories, u'cat1 cat3')
        
        f1 = DefaultNamespaceTest.objects.get(pk=f1.pk)
        
        self.assertEquals(f1.categories, u'cat1 cat3')
        
        f1.categories = u'cat1'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 2)
        self.failUnless(cat1 in tags)
        self.failUnless(tag1 in tags)
        
        f1.categories = u':cat2'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 1)
        self.failUnless(tag1 in tags)
        
        f1.categories = None
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 1)
        self.failUnless(tag1 in tags)
        
        f2 = DefaultNamespaceTest.objects.create()
        self.assertEquals(f2.categories, u'')
        
        f2.categories = 'cat5'
        f2.save()
        tags = Tag.objects.get_for_object(f2)
        
        cat5 = get_tag('category:cat5')
        self.assertEquals(len(tags), 1)
        self.failUnless(cat5 in tags)

        f1 = DefaultNamespaceTest.objects.get(pk=f1.pk)
        f2 = DefaultNamespaceTest.objects.get(pk=f2.pk)

        self.assertEquals(f1.categories, u'')
        self.assertEquals(f2.categories, u'cat5')
        self.assertEquals(DefaultNamespaceTest.categories, u'cat5')
    
    def test_tagfield_and_tagfield_with_namespace(self):
        f1 = DefaultNamespaceTest2.objects.create(
            tags=u'tag1 :tag2 category:tag3 foo:tag4',
            categories=u'cat1 :cat2 category:cat3 foo:cat4')
        tags = Tag.objects.get_for_object(f1)
        tag1 = get_tag('tag1')
        tag2 = get_tag('tag2')
        tag3 = get_tag('category:tag3')
        tag4 = get_tag('foo:tag4')
        cat1 = get_tag('category:cat1')
        cat2 = get_tag('cat2')
        cat3 = get_tag('category:cat3')
        cat4 = get_tag('foo:cat4')
        self.failUnless(None not in (tag1, tag2, tag4, cat1, cat3))
        self.failUnless(tag3 is None)
        self.failUnless(cat2 is None)
        self.failUnless(cat4 is None)
        self.assertEquals(len(tags), 5)
        self.failUnless(tag1 in tags)
        self.failUnless(tag2 in tags)
        self.failUnless(tag4 in tags)
        self.failUnless(cat1 in tags)
        self.failUnless(cat3 in tags)
        
        self.assertEquals(DefaultNamespaceTest2.tags, u'tag1 tag2 foo:tag4')
        self.assertEquals(DefaultNamespaceTest2.categories, u'cat1 cat3')
        
        f1 = DefaultNamespaceTest2.objects.get(pk=f1.pk)
        
        self.assertEquals(f1.tags, u'foo:tag4 tag1 tag2')
        self.assertEquals(f1.categories, u'cat1 cat3')
        
        f1.tags = u'tag1'
        f1.categories = u'cat1'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 2)
        self.failUnless(tag1 in tags)
        self.failUnless(cat1 in tags)
        self.assertEquals(f1.tags, u'tag1')
        self.assertEquals(f1.categories, u'cat1')
        
        f1.tags = u'category:cat1'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 1)
        self.failUnless(cat1 in tags)
        self.assertEquals(f1.tags, u'')
        self.assertEquals(f1.categories, u'cat1')
        
        f1.tags = u'cat2'
        f1.categories = u':cat2'
        f1.save()
        cat2 = get_tag('cat2')
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 1)
        self.failUnless(cat2 in tags)
        self.assertEquals(f1.tags, u'cat2')
        self.assertEquals(f1.categories, u'')
        
        f1.tags = None
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 0)
        self.assertEquals(f1.tags, u'')
        self.assertEquals(f1.categories, u'')
        
        # Now its gone.
        f1.tags = None
        f1.categories = None
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 0)
        self.assertEquals(f1.tags, u'')
        self.assertEquals(f1.categories, u'')
        
        f2 = DefaultNamespaceTest2.objects.create()
        self.assertEquals(f2.tags, u'')
        self.assertEquals(f2.categories, u'')
        
        f2.tags = 'tag5'
        f2.categories = 'cat5'
        f2.save()
        tags = Tag.objects.get_for_object(f2)
        
        tag5 = get_tag('tag5')
        cat5 = get_tag('category:cat5')
        self.assertEquals(len(tags), 2)
        self.failUnless(tag5 in tags)
        self.failUnless(cat5 in tags)

        f1 = DefaultNamespaceTest2.objects.get(pk=f1.pk)
        f2 = DefaultNamespaceTest2.objects.get(pk=f2.pk)

        self.assertEquals(f1.tags, u'')
        self.assertEquals(f1.categories, u'')
        self.assertEquals(f2.tags, u'tag5')
        self.assertEquals(f2.categories, u'cat5')
        self.assertEquals(DefaultNamespaceTest2.tags, u'tag5')
        self.assertEquals(DefaultNamespaceTest2.categories, u'cat5')
    
    def test_multiple_tagfields_with_namespace(self):
        f1 = DefaultNamespaceTest3.objects.create(
            foos=u'foo1 :foo2 category:foo3 foo:foo4',
            categories=u'cat1 :cat2 category:cat3 foo:cat4')
        tags = Tag.objects.get_for_object(f1)
        foo1 = get_tag('foo:foo1')
        foo2 = get_tag('foo2')
        foo3 = get_tag('category:foo3')
        foo4 = get_tag('foo:foo4')
        cat1 = get_tag('category:cat1')
        cat2 = get_tag('cat2')
        cat3 = get_tag('category:cat3')
        cat4 = get_tag('foo:cat4')
        self.failUnless(None not in (foo1, foo4, cat1, cat3))
        self.failUnless(foo2 is None)
        self.failUnless(foo3 is None)
        self.failUnless(cat2 is None)
        self.failUnless(cat4 is None)
        self.assertEquals(len(tags), 4)
        self.failUnless(foo1 in tags)
        self.failUnless(foo4 in tags)
        self.failUnless(cat1 in tags)
        self.failUnless(cat3 in tags)
        
        self.assertEquals(DefaultNamespaceTest3.foos, u'foo1 foo4')
        self.assertEquals(DefaultNamespaceTest3.categories, u'cat1 cat3')
        
        f1 = DefaultNamespaceTest3.objects.get(pk=f1.pk)
        
        self.assertEquals(f1.foos, u'foo1 foo4')
        self.assertEquals(f1.categories, u'cat1 cat3')
        
        f1.foos = u'foo1'
        f1.categories = u'cat1'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 2)
        self.failUnless(foo1 in tags)
        self.failUnless(cat1 in tags)
        self.assertEquals(f1.foos, u'foo1')
        self.assertEquals(f1.categories, u'cat1')
        
        f1.foos = u'category:cat1'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 1)
        self.failUnless(cat1 in tags)
        self.assertEquals(f1.foos, u'')
        self.assertEquals(f1.categories, u'cat1')
        
        f1.foos = u'cat4'
        f1.categories = u':cat2'
        f1.save()
        cat4 = get_tag('foo:cat4')
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 1)
        self.failUnless(cat4 in tags)
        self.assertEquals(f1.foos, u'cat4')
        self.assertEquals(f1.categories, u'')
        
        f1.foos = None
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 0)
        self.assertEquals(f1.foos, u'')
        self.assertEquals(f1.categories, u'')
        
        f1.foos = None
        f1.categories = None
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        self.assertEquals(len(tags), 0)
        self.assertEquals(f1.foos, u'')
        self.assertEquals(f1.categories, u'')
        
        f2 = DefaultNamespaceTest3.objects.create()
        self.assertEquals(f2.foos, u'')
        self.assertEquals(f2.categories, u'')
        
        f2.foos = 'foo5'
        f2.categories = 'cat5'
        f2.save()
        tags = Tag.objects.get_for_object(f2)
        
        foo5 = get_tag('foo:foo5')
        cat5 = get_tag('category:cat5')
        self.assertEquals(len(tags), 2)
        self.failUnless(foo5 in tags)
        self.failUnless(cat5 in tags)

        f1 = DefaultNamespaceTest3.objects.get(pk=f1.pk)
        f2 = DefaultNamespaceTest3.objects.get(pk=f2.pk)

        self.assertEquals(f1.foos, u'')
        self.assertEquals(f1.categories, u'')
        self.assertEquals(f2.foos, u'foo5')
        self.assertEquals(f2.categories, u'cat5')
        self.assertEquals(DefaultNamespaceTest3.foos, u'foo5')
        self.assertEquals(DefaultNamespaceTest3.categories, u'cat5')

    def test_model_tag_field_definition_validation(self):
        from StringIO import StringIO
        sys.stderr = StringIO()

        from tagging.fields import TagField
        try:
            class Model(models.Model):
                tags = TagField(namespace='foo')
                foos = TagField(namespace='foo')
        except SystemExit, e:
            pass
        else:
            self.fail(
                u'Validation of model fields failed. '
                u'A namespace is only allowed once. '
            )
    
    def test_update_via_tags(self):
        f1 = FormTest.objects.create(tags=u'one two three')
        Tag.objects.get(name='three').delete()
        t2 = Tag.objects.get(name='two')
        t2.name = 'new'
        t2.save()
        f1again = FormTest.objects.get(pk=f1.pk)
        self.failIf('three' in f1again.tags)
        self.failIf('two' in f1again.tags)
        self.failUnless('new' in f1again.tags)
    
    def test_creation_without_specifying_tags(self):
        f1 = FormTest()
        self.assertEquals(f1.tags, '')
    
    def test_creation_with_nullable_tags_field(self):
        f1 = FormTestNull()
        self.assertEquals(f1.tags, '')

class TestSettings(TestCase):
    def setUp(self):
        self.original_force_lower_case_tags = conf.FORCE_LOWERCASE_TAGS
        self.dead_parrot = Parrot.objects.create(state='dead')
    
    def tearDown(self):
        conf.FORCE_LOWERCASE_TAGS = self.original_force_lower_case_tags
    
    def test_force_lowercase_tags(self):
        """ Test forcing tags to lowercase. """
        
        conf.FORCE_LOWERCASE_TAGS = True
        
        Tag.objects.update_tags(self.dead_parrot, 'foO bAr Ter')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        foo_tag = get_tag('foo')
        bar_tag = get_tag('bar')
        ter_tag = get_tag('ter')
        self.failUnless(foo_tag in tags)
        self.failUnless(bar_tag in tags)
        self.failUnless(ter_tag in tags)
        
        Tag.objects.update_tags(self.dead_parrot, 'foO bAr baZ')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        baz_tag = get_tag('baz')
        self.assertEquals(len(tags), 3)
        self.failUnless(bar_tag in tags)
        self.failUnless(baz_tag in tags)
        self.failUnless(foo_tag in tags)
        
        Tag.objects.add_tag(self.dead_parrot, 'FOO')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 3)
        self.failUnless(bar_tag in tags)
        self.failUnless(baz_tag in tags)
        self.failUnless(foo_tag in tags)
        
        Tag.objects.add_tag(self.dead_parrot, 'Zip')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 4)
        zip_tag = get_tag('zip')
        self.failUnless(bar_tag in tags)
        self.failUnless(baz_tag in tags)
        self.failUnless(foo_tag in tags)
        self.failUnless(zip_tag in tags)
        
        Tag.objects.add_tag(self.dead_parrot, 'Foo:bAr=ziP')
        tags = Tag.objects.get_for_object(self.dead_parrot)
        self.assertEquals(len(tags), 5)
        foo_bar_zip_tag = get_tag('foo:bar=zip')
        self.failUnless(bar_tag in tags)
        self.failUnless(baz_tag in tags)
        self.failUnless(foo_tag in tags)
        self.failUnless(zip_tag in tags)
        self.failUnless(foo_bar_zip_tag in tags)
        
        f1 = FormTest.objects.create()
        f1.tags = u'TEST5'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        test5_tag = get_tag('test5')
        self.assertEquals(len(tags), 1)
        self.failUnless(test5_tag in tags)
        self.assertEquals(f1.tags, u'test5')
        
        f1.tags = u'TEST5 FOO:BAR=TAR'
        f1.save()
        tags = Tag.objects.get_for_object(f1)
        foo_bar_tar_tag = get_tag('foo:bar=tar')
        self.assertEquals(len(tags), 2)
        self.failUnless(test5_tag in tags)
        self.failUnless(foo_bar_tar_tag in tags)
        self.assertEquals(f1.tags, u'test5 foo:bar=tar')

class TestTagUsageForModelBaseCase(TestCase):
    def test_tag_usage_for_model_empty(self):
        self.assertEquals(Tag.objects.usage_for_model(Parrot), [])

class TestTagUsageForModel(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar foo:bar=egg'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'foo ter foo:bar=egg'),
            ('late',                  2, False, 'bar ter foo:bar'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
    
    def test_tag_usage_for_model(self):
        tag_usage = Tag.objects.usage_for_model(Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 6)
        self.failUnless((u'bar', 3) in relevant_attribute_list)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 3) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 2) in relevant_attribute_list)
        self.failUnless((u'foo:bar', 1) in relevant_attribute_list)
    
    def test_tag_usage_for_model_with_min_count(self):
        tag_usage = Tag.objects.usage_for_model(Parrot, min_count = 2)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 4)
        self.failUnless((u'bar', 3) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 3) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 2) in relevant_attribute_list)
    
    def test_tag_usage_with_filter_on_model_objects(self):
        tag_usage = Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(state='no more'))
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(state__startswith='p'))
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(perch__size__gt=4))
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_model(Parrot, counts=True, filters=dict(perch__smelly=True))
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 4)
        self.failUnless((u'bar', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 2) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_model(Parrot, min_count=2, filters=dict(perch__smelly=True))
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 2)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', 2) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_model(Parrot, filters=dict(perch__size__gt=4))
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'counts')) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', False) in relevant_attribute_list)
        self.failUnless((u'baz', False) in relevant_attribute_list)
        self.failUnless((u'foo', False) in relevant_attribute_list)
        self.failUnless((u'ter', False) in relevant_attribute_list)
        self.failUnless((u'foo:bar=egg', False) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_model(Parrot, filters=dict(perch__size__gt=99))
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'counts')) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 0)

class TestTagsRelatedForModel(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'foo ter spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
            
    def test_related_for_model_with_tag_query_sets_as_input(self):
        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar']), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 2) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar']), Parrot, min_count=2)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 1)
        self.failUnless((u'ter', 2) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar']), Parrot, counts=False)
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'count')) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'baz', False) in relevant_attribute_list)
        self.failUnless((u'foo', False) in relevant_attribute_list)
        self.failUnless((u'ter', False) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', False) in relevant_attribute_list)
        self.failUnless((u'spam:foo', False) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar', 'ter']), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 2)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['bar', 'ter', 'baz']), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 0)
        
        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['foo']), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 0)

        related_tags = Tag.objects.related_for_model(Tag.objects.filter(name__in=['foo'], namespace=None), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'bar', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2) in relevant_attribute_list)

        related_tags = Tag.objects.related_for_model(Tag.objects.filter(namespace__in=['spam']), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 0)

        related_tags = Tag.objects.related_for_model(Tag.objects.filter(value__in=['ham']), Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'bar', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)

    def test_related_for_model_with_tag_strings_as_input(self):
        # Once again, with feeling (strings)
        related_tags = Tag.objects.related_for_model('bar', Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 2) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model('spam:egg=ham', Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'bar', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model('bar', Parrot, min_count=2)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 1)
        self.failUnless((u'ter', 2) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model('bar', Parrot, counts=False)
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'count')) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'baz', False) in relevant_attribute_list)
        self.failUnless((u'foo', False) in relevant_attribute_list)
        self.failUnless((u'ter', False) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', False) in relevant_attribute_list)
        self.failUnless((u'spam:foo', False) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model(['bar', 'ter'], Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 2)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
        related_tags = Tag.objects.related_for_model(['bar', 'ter', 'baz'], Parrot, counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in related_tags]
        self.assertEquals(len(relevant_attribute_list), 0)

class TestTagsCalculateCloud(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'bar foo ter spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
    
    def test_tag_manager_calculate_cloud_method(self):
        cloud_tags = Tag.objects.cloud_for_model(Parrot)
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 6)
        self.failUnless((u'bar', 4, 4) in relevant_attribute_list)
        self.failUnless((u'ter', 3, 3) in relevant_attribute_list)
        self.failUnless((u'foo', 2, 2) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2, 2) in relevant_attribute_list)
        self.failUnless((u'baz', 1, 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1, 1) in relevant_attribute_list)
        
        cloud_tags = Tag.objects.cloud_for_model(Parrot, steps=10)
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 6)
        self.failUnless((u'bar', 4, 10) in relevant_attribute_list)
        self.failUnless((u'ter', 3, 8) in relevant_attribute_list)
        self.failUnless((u'foo', 2, 4) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2, 4) in relevant_attribute_list)
        self.failUnless((u'baz', 1, 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1, 1) in relevant_attribute_list)
        
        cloud_tags = Tag.objects.cloud_for_model(Parrot, steps=10, distribution=LINEAR)
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 6)
        self.failUnless((u'bar', 4, 10) in relevant_attribute_list)
        self.failUnless((u'ter', 3, 7) in relevant_attribute_list)
        self.failUnless((u'foo', 2, 4) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2, 4) in relevant_attribute_list)
        self.failUnless((u'baz', 1, 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1, 1) in relevant_attribute_list)
        
        cloud_tags = Tag.objects.cloud_for_model(Parrot, min_count=2)
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 4)
        self.failUnless((u'bar', 4, 4) in relevant_attribute_list)
        self.failUnless((u'ter', 3, 3) in relevant_attribute_list)
        self.failUnless((u'foo', 2, 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2, 1) in relevant_attribute_list)
        
        cloud_tags = Tag.objects.cloud_for_model(Parrot, min_count=4)
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 1)
        self.failUnless((u'bar', 4, 1) in relevant_attribute_list)
        
        cloud_tags = Tag.objects.cloud_for_model(Parrot, filters=dict(state__startswith='p'))
        relevant_attribute_list = [(unicode(tag), tag.count, tag.font_size) for tag in cloud_tags]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2, 4) in relevant_attribute_list)
        self.failUnless((u'ter', 1, 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1, 1) in relevant_attribute_list)
        self.failUnless((u'baz', 1, 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1, 1) in relevant_attribute_list)
        
class TestGetTaggedObjectsByModel(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'foo ter spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
            
        self.foo = Tag.objects.get(namespace=None, name='foo', value=None)
        self.bar = Tag.objects.get(namespace=None, name='bar', value=None)
        self.baz = Tag.objects.get(namespace=None, name='baz', value=None)
        self.ter = Tag.objects.get(namespace=None, name='ter', value=None)
        self.spameggham = Tag.objects.get(namespace='spam', name='egg', value='ham')
        self.spamfoo = Tag.objects.get(namespace='spam', name='foo', value=None)
        self.notassigned = Tag.objects.create(name='notassigned')
        
        self.pining_for_the_fjords_parrot = Parrot.objects.get(state='pining for the fjords')
        self.passed_on_parrot = Parrot.objects.get(state='passed on')
        self.no_more_parrot = Parrot.objects.get(state='no more')
        self.late_parrot = Parrot.objects.get(state='late')
        
    def test_get_by_model_simple(self):
        parrots = TaggedItem.objects.get_by_model(Parrot, self.foo)
        self.assertEquals(len(parrots), 2)
        self.failUnless(self.no_more_parrot in parrots)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, self.bar)
        self.assertEquals(len(parrots), 3)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
    
    def test_get_by_model_intersection(self):
        parrots = TaggedItem.objects.get_by_model(Parrot, [self.foo, self.baz])
        self.assertEquals(len(parrots), 0)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, [self.foo, self.bar])
        self.assertEquals(len(parrots), 1)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, [self.bar, self.ter])
        self.assertEquals(len(parrots), 2)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        
        # Issue 114 - Intersection with non-existant tags
        parrots = TaggedItem.objects.get_intersection_by_model(Parrot, [])
        self.assertEquals(len(parrots), 0)
    
    def test_get_by_model_with_tag_querysets_as_input(self):
        parrots = TaggedItem.objects.get_by_model(Parrot, Tag.objects.filter(name__in=['foo', 'baz']))
        self.assertEquals(len(parrots), 0)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, Tag.objects.filter(name__in=['bar']))
        self.assertEquals(len(parrots), 3)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.late_parrot in parrots)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, Tag.objects.filter(name__in=['bar', 'ter']))
        self.assertEquals(len(parrots), 2)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
    
    def test_get_by_model_with_strings_as_input(self):
        parrots = TaggedItem.objects.get_by_model(Parrot, 'foo baz')
        self.assertEquals(len(parrots), 0)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, 'bar')
        self.assertEquals(len(parrots), 3)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.late_parrot in parrots)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, 'bar ter')
        self.assertEquals(len(parrots), 2)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        
    def test_get_by_model_with_lists_of_strings_as_input(self):
        parrots = TaggedItem.objects.get_by_model(Parrot, ['foo', 'baz'])
        self.assertEquals(len(parrots), 0)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, ['bar'])
        self.assertEquals(len(parrots), 3)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.late_parrot in parrots)
        
        parrots = TaggedItem.objects.get_by_model(Parrot, ['bar', 'ter'])
        self.assertEquals(len(parrots), 2)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
    
    def test_get_by_nonexistent_tag(self):
        # Issue 50 - Get by non-existent tag
        parrots = TaggedItem.objects.get_by_model(Parrot, 'argatrons')
        self.assertEquals(len(parrots), 0)
    
    def test_get_union_by_model(self):
        parrots = TaggedItem.objects.get_union_by_model(Parrot, ['foo', 'ter'])
        self.assertEquals(len(parrots), 4)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.no_more_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        
        parrots = TaggedItem.objects.get_union_by_model(Parrot, ['bar', 'baz'])
        self.assertEquals(len(parrots), 3)
        self.failUnless(self.late_parrot in parrots)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.pining_for_the_fjords_parrot in parrots)
        
        parrots = TaggedItem.objects.get_union_by_model(Parrot, ['spam:foo', 'baz'])
        self.assertEquals(len(parrots), 2)
        self.failUnless(self.passed_on_parrot in parrots)
        self.failUnless(self.late_parrot in parrots)
        
        parrots = TaggedItem.objects.get_union_by_model(Parrot, ['notassigned'])
        self.assertEquals(len(parrots), 0)
        
        # Issue 114 - Union with non-existant tags
        parrots = TaggedItem.objects.get_union_by_model(Parrot, [])
        self.assertEquals(len(parrots), 0)

class TestGetRelatedTaggedItems(TestCase):
    def setUp(self):
        self.l1 = Link.objects.create(name='link 1')
        Tag.objects.update_tags(self.l1, 'tag1 tag2 tag3 tag4 tag5')
        self.l2 = Link.objects.create(name='link 2')
        Tag.objects.update_tags(self.l2, 'tag1 tag2 tag3')
        self.l3 = Link.objects.create(name='link 3')
        Tag.objects.update_tags(self.l3, 'tag1')
        self.l4 = Link.objects.create(name='link 4')
        
        self.a1 = Article.objects.create(name='article 1')
        Tag.objects.update_tags(self.a1, 'tag1 tag2 tag3 tag4')
    
    def test_get_related_objects_of_same_model(self):
        related_objects = TaggedItem.objects.get_related(self.l1, Link)
        self.assertEquals(len(related_objects), 2)
        self.failUnless(self.l2 in related_objects)
        self.failUnless(self.l3 in related_objects)
        
        related_objects = TaggedItem.objects.get_related(self.l4, Link)
        self.assertEquals(len(related_objects), 0)
    
    def test_get_related_objects_of_same_model_limited_number_of_results(self):
        # This fails on Oracle because it has no support for a 'LIMIT' clause.
        # See http://asktom.oracle.com/pls/asktom/f?p=100:11:0::::P11_QUESTION_ID:127412348064
        
        # ask for no more than 1 result
        related_objects = TaggedItem.objects.get_related(self.l1, Link, num=1)
        self.assertEquals(len(related_objects), 1)
        self.failUnless(self.l2 in related_objects)
        
    def test_get_related_objects_of_same_model_limit_related_items(self):
        related_objects = TaggedItem.objects.get_related(self.l1, Link.objects.exclude(name='link 3'))
        self.assertEquals(len(related_objects), 1)
        self.failUnless(self.l2 in related_objects)
    
    def test_get_related_objects_of_different_model(self):
        related_objects = TaggedItem.objects.get_related(self.a1, Link)
        self.assertEquals(len(related_objects), 3)
        self.failUnless(self.l1 in related_objects)
        self.failUnless(self.l2 in related_objects)
        self.failUnless(self.l3 in related_objects)
            
        Tag.objects.update_tags(self.a1, 'tag6')
        related_objects = TaggedItem.objects.get_related(self.a1, Link)
        self.assertEquals(len(related_objects), 0)
        
class TestTagUsageForQuerySet(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'foo ter spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)
    
    def test_tag_usage_for_queryset(self):
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(state='no more'), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(state__startswith='p'), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__size__gt=4), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        self.failUnless((u'baz', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__smelly=True), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 4)
        self.failUnless((u'bar', 1) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__smelly=True), min_count=2)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 2)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__size__gt=4))
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'counts')) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', False) in relevant_attribute_list)
        self.failUnless((u'baz', False) in relevant_attribute_list)
        self.failUnless((u'foo', False) in relevant_attribute_list)
        self.failUnless((u'ter', False) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', False) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(perch__size__gt=99))
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'counts')) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 0)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(Q(perch__size__gt=6) | Q(state__startswith='l')), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(Q(perch__size__gt=6) | Q(state__startswith='l')), min_count=2)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 1)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.filter(Q(perch__size__gt=6) | Q(state__startswith='l')))
        relevant_attribute_list = [(unicode(tag), hasattr(tag, 'counts')) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', False) in relevant_attribute_list)
        self.failUnless((u'foo', False) in relevant_attribute_list)
        self.failUnless((u'ter', False) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', False) in relevant_attribute_list)
        self.failUnless((u'spam:foo', False) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.exclude(state='passed on'), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 5)
        self.failUnless((u'bar', 2) in relevant_attribute_list)
        self.failUnless((u'foo', 2) in relevant_attribute_list)
        self.failUnless((u'ter', 2) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 2) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.exclude(state__startswith='p'), min_count=2)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 1)
        self.failUnless((u'ter', 2) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.exclude(Q(perch__size__gt=6) | Q(perch__smelly=False)), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'foo', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:egg=ham', 1) in relevant_attribute_list)
        
        tag_usage = Tag.objects.usage_for_queryset(Parrot.objects.exclude(perch__smelly=True).filter(state__startswith='l'), counts=True)
        relevant_attribute_list = [(unicode(tag), tag.count) for tag in tag_usage]
        self.assertEquals(len(relevant_attribute_list), 3)
        self.failUnless((u'bar', 1) in relevant_attribute_list)
        self.failUnless((u'ter', 1) in relevant_attribute_list)
        self.failUnless((u'spam:foo', 1) in relevant_attribute_list)
        
################
# Model Fields #
################

class TestTagFieldInForms(TestCase):
    def setUp(self):
        self.original_max_tag_length = conf.MAX_TAG_LENGTH
        self.original_max_tag_name_length = conf.MAX_TAG_NAME_LENGTH
        self.original_max_tag_namespace_length = conf.MAX_TAG_NAMESPACE_LENGTH
        self.original_max_tag_value_length = conf.MAX_TAG_VALUE_LENGTH
    
    def tearDown(self):
        conf.MAX_TAG_LENGTH = self.original_max_tag_length
        conf.MAX_TAG_NAME_LENGTH = self.original_max_tag_name_length
        conf.MAX_TAG_NAMESPACE_LENGTH = self.original_max_tag_namespace_length
        conf.MAX_TAG_VALUE_LENGTH = self.original_max_tag_value_length

    def test_tag_field_in_modelform(self):
        # Ensure that automatically created forms use TagField
        class TestForm(forms.ModelForm):
            class Meta:
                model = FormTest
                
        form = TestForm()
        self.assertEquals(form.fields['tags'].__class__.__name__, 'TagField')
    
    def test_recreation_of_tag_list_string_representations(self):
        plain = Tag.objects.create(name='plain')
        spaces = Tag.objects.create(name='spa ces')
        comma = Tag.objects.create(name='com,ma')
        colon = Tag.objects.create(name='co:lon')
        equal = Tag.objects.create(name='equa=l')
        spaces_namespace = Tag.objects.create(name='foo', namespace='spa ces')
        spaces_value = Tag.objects.create(name='foo', value='spa ces')
        spaces_comma_namespace = Tag.objects.create(name='foo', namespace='spa ces,comma')
        self.assertEquals(edit_string_for_tags([plain]), u'plain')
        self.assertEquals(edit_string_for_tags([plain, spaces]), u'plain, spa ces')
        self.assertEquals(edit_string_for_tags([plain, spaces, comma]), u'plain, spa ces, "com,ma"')
        self.assertEquals(edit_string_for_tags([plain, comma]), u'plain "com,ma"')
        self.assertEquals(edit_string_for_tags([comma, spaces]), u'"com,ma", spa ces')
        self.assertEquals(edit_string_for_tags([plain, colon]), u'plain "co:lon"')
        self.assertEquals(edit_string_for_tags([equal, colon]), u'"equa=l" "co:lon"')
        self.assertEquals(edit_string_for_tags([equal, spaces, colon]), u'"equa=l", spa ces, "co:lon"')
        self.assertEquals(edit_string_for_tags([plain, spaces_namespace]), u'plain, spa ces:foo')
        self.assertEquals(edit_string_for_tags([plain, spaces_value]), u'plain, foo=spa ces')
        self.assertEquals(edit_string_for_tags([plain, spaces_comma_namespace]), u'plain "spa ces,comma":foo')
        self.assertEquals(edit_string_for_tags([plain], default_namespace='spa ces'),
            u':plain')
        self.assertEquals(edit_string_for_tags([spaces_namespace], default_namespace='spa ces'),
            u'foo')
        self.assertEquals(edit_string_for_tags([spaces_namespace, plain, spaces_comma_namespace], default_namespace='spa ces'),
            u'foo :plain "spa ces,comma":foo')
    
    def test_tag_d_validation(self):
        t = TagField()
        w50 = 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvb'
        w51 = w50 + 'n'
        w10 = w50[:10]
        w11 = w50[:11]
        conf.MAX_TAG_LENGTH = 150
        conf.MAX_TAG_NAME_LENGTH = 50
        conf.MAX_TAG_NAMESPACE_LENGTH = 50
        conf.MAX_TAG_VALUE_LENGTH = 50

        self.assertEquals(t.clean('foo'), u'foo')
        self.assertEquals(t.clean('foo bar baz'), u'foo bar baz')
        self.assertEquals(t.clean('foo,bar,baz'), u'foo,bar,baz')
        self.assertEquals(t.clean('foo, bar, baz'), u'foo, bar, baz')

        self.assertEquals(t.clean('foo %s bar' % w50),
            u'foo %s bar' % w50)
        self.assertEquals(t.clean('foo %s:%s=%s bar' % (w50, w50, w50)),
            u'foo %s:%s=%s bar' % (w50, w50, w50))
        try:
            t.clean('foo %s bar' % w51)
        except forms.ValidationError, ve:
            self.assertEquals(unicode(list(ve.messages)), u'[u"Each tag\'s name may be no more than 50 characters long."]')
        except Exception, e:
            raise e
        else:
            raise self.failureException('a ValidationError exception was supposed to have been raised.')
        try:
            t.clean('foo %s:%s bar' % (w51, w50))
        except forms.ValidationError, ve:
            self.assertEquals(unicode(list(ve.messages)), u'[u"Each tag\'s namespace may be no more than 50 characters long."]')
        except Exception, e:
            raise e
        else:
            raise self.failureException('a ValidationError exception was supposed to have been raised.')
        try:
            t.clean('foo %s=%s bar' % (w50, w51))
        except forms.ValidationError, ve:
            self.assertEquals(unicode(list(ve.messages)), u'[u"Each tag\'s value may be no more than 50 characters long."]')
        except Exception, e:
            raise e
        else:
            raise self.failureException('a ValidationError exception was supposed to have been raised.')
        conf.MAX_TAG_LENGTH = 149
        try:
            t.clean('foo %s:%s=%s bar' % (w50, w50, w50))
        except forms.ValidationError, ve:
            self.assertEquals(unicode(list(ve.messages)), u"[u'Each tag may be no more than 149 characters long.']")
        except Exception, e:
            raise e
        else:
            raise self.failureException('a ValidationError exception was supposed to have been raised.')

    def test_tag_d_validation_with_non_string_input(self):
        t = TagField()
        self.assertEquals(t.clean(Tag(name='foo')), 'foo')
        self.assertEquals(t.clean(Tag(name='foo', namespace='bar')), 'bar:foo')
        self.assertEquals(t.clean(Tag(name='foo', namespace='bar:baz')), '"bar:baz":foo')

    def test_tag_d_validation_with_empty_input(self):
        t = TagField()
        self.assertRaises(forms.ValidationError, t.clean, '')

        t = TagField(required=False)
        self.assertEquals(t.clean(''), '')
        self.assertEquals(t.clean(None), '')
    
    def test_tag_d_validation_with_default_namespace(self):
        t = TagField(default_namespace='foo')
        self.assertEquals(t.clean('bar'), 'bar')

        conf.MAX_TAG_NAMESPACE_LENGTH = 10
        t = TagField(default_namespace='qwertyuiop')
        self.assertEquals(t.clean('bar'), 'bar')

        t = TagField(default_namespace='qwertyuiopa')
        self.assertRaises(forms.ValidationError, t.clean, 'bar')

#########
# Admin #
#########

class TestTagAdminForm(TestCase):
    def setUp(self):
        self.original_max_tag_length = conf.MAX_TAG_LENGTH
        self.original_max_tag_name_length = conf.MAX_TAG_NAME_LENGTH
        self.original_max_tag_namespace_length = conf.MAX_TAG_NAMESPACE_LENGTH
        self.original_max_tag_value_length = conf.MAX_TAG_VALUE_LENGTH
    
    def tearDown(self):
        conf.MAX_TAG_LENGTH = self.original_max_tag_length
        conf.MAX_TAG_NAME_LENGTH = self.original_max_tag_name_length
        conf.MAX_TAG_NAMESPACE_LENGTH = self.original_max_tag_namespace_length
        conf.MAX_TAG_VALUE_LENGTH = self.original_max_tag_value_length
    
    def test_form_fields_validation(self):
        w50 = 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvb'
        w51 = w50 + 'n'
        w30 = w50[:30]
        w31 = w50[:31]
        conf.MAX_TAG_LENGTH = 90
        conf.MAX_TAG_NAME_LENGTH = 30
        conf.MAX_TAG_NAMESPACE_LENGTH = 30
        conf.MAX_TAG_VALUE_LENGTH = 30

        tag_parts = {'name': None, 'namespace': None, 'value': None}

        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 1)
        self.assertEquals(len(f['name'].errors), 1)

        tag_parts['name'] = w30
        f = TagAdminForm(tag_parts)
        self.failUnless(f.is_valid())

        tag_parts['namespace'] = w30
        f = TagAdminForm(tag_parts)
        self.failUnless(f.is_valid())

        tag_parts['namespace'] = w31
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 1)
        self.assertEquals(len(f['namespace'].errors), 1)

        tag_parts['name'] = None
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 2)
        self.assertEquals(len(f['name'].errors), 1)
        self.assertEquals(len(f['namespace'].errors), 1)

        tag_parts['name'] = w31
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 2)
        self.assertEquals(len(f['name'].errors), 1)
        self.assertEquals(len(f['namespace'].errors), 1)

        tag_parts['name'] = w30
        tag_parts['namespace'] = w30
        tag_parts['value'] = w30
        f = TagAdminForm(tag_parts)
        self.failUnless(f.is_valid())

        tag_parts['name'] = None
        tag_parts['namespace'] = None
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 1)
        self.assertEquals(len(f['name'].errors), 1)

        tag_parts['name'] = w31
        tag_parts['namespace'] = w31
        tag_parts['value'] = w31
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 3)
        self.assertEquals(len(f['namespace'].errors), 1)
        self.assertEquals(len(f['name'].errors), 1)
        self.assertEquals(len(f['value'].errors), 1)

        conf.MAX_TAG_LENGTH = 89

        tag_parts['name'] = w30
        tag_parts['namespace'] = w30
        tag_parts['value'] = w30
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 1)
        self.assertEquals(len(f['namespace'].errors), 0)
        self.assertEquals(len(f['name'].errors), 0)
        self.assertEquals(len(f['value'].errors), 0)
        self.assertEquals(len(f.non_field_errors()), 1)

        # more than 50 chars are not allowed because the model fields
        # cannot store longer values.
        conf.MAX_TAG_LENGTH = 180
        conf.MAX_TAG_NAMESPACE_LENGTH = 60
        conf.MAX_TAG_NAME_LENGTH = 60
        conf.MAX_TAG_VALUE_LENGTH = 60

        tag_parts['name'] = w50
        tag_parts['namespace'] = w50
        tag_parts['value'] = w50
        f = TagAdminForm(tag_parts)
        self.failUnless(f.is_valid())

        tag_parts['name'] = w51
        tag_parts['namespace'] = w51
        tag_parts['value'] = w51
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 3)
        self.assertEquals(len(f['namespace'].errors), 1)
        self.assertEquals(len(f['name'].errors), 1)
        self.assertEquals(len(f['value'].errors), 1)
        self.assertEquals(len(f.non_field_errors()), 0)

    def test_form_fields_validation_with_invalid_input(self):
        tag_parts = {'namespace': None, 'name': 'foo', 'value': None}
        f = TagAdminForm(tag_parts)
        self.failUnless(f.is_valid())

        tag_parts['name'] = '"'
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 1)
        self.assertEquals(len(f['name'].errors), 1)

        tag_parts['name'] = 'foo"bar'
        tag_parts['namespace'] = 'foo"bar'
        tag_parts['value'] = 'foo"bar'
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 3)
        self.assertEquals(len(f['namespace'].errors), 1)
        self.assertEquals(len(f['name'].errors), 1)
        self.assertEquals(len(f['value'].errors), 1)

        tag_parts['name'] = '"foo"'
        tag_parts['namespace'] = '"foo"'
        tag_parts['value'] = '"foo"'
        f = TagAdminForm(tag_parts)
        self.failIf(f.is_valid())
        self.assertEquals(len(f.errors), 3)
        self.assertEquals(len(f['namespace'].errors), 1)
        self.assertEquals(len(f['name'].errors), 1)
        self.assertEquals(len(f['value'].errors), 1)

###########
# Generic #
###########

class TestFetchContentObjects(TestCase):
    def setUp(self):
        parrot_details = (
            ('pining for the fjords', 9, True,  'foo bar spam:egg=ham'),
            ('passed on',             6, False, 'bar baz ter'),
            ('no more',               4, True,  'foo ter spam:egg=ham'),
            ('late',                  2, False, 'bar ter spam:foo'),
        )
        
        for state, perch_size, perch_smelly, tags in parrot_details:
            perch = Perch.objects.create(size=perch_size, smelly=perch_smelly)
            parrot = Parrot.objects.create(state=state, perch=perch)
            Tag.objects.update_tags(parrot, tags)

        article_details = (
            ('beatles comeback!', 'foo bar ter'),
            ('django gets a new pony', 'spam:foo spam:egg=ham'),
        )

        for name, tags in article_details:
            article = Article.objects.create(name=name)
            Tag.objects.update_tags(article, tags)

        link_details = (
            ('example.com', 'baz ter'),
            ('lolcatz', 'baz'),
        )

        for name, tags in link_details:
            link = Link.objects.create(name=name)
            Tag.objects.update_tags(link, tags)

        self.parrot_contenttype = ContentType.objects.get_for_model(Parrot)
        self.article_contenttype = ContentType.objects.get_for_model(Article)
        self.link_contenttype = ContentType.objects.get_for_model(Link)

    def test_with_one_model(self):
        queryset = TaggedItem.objects.filter(content_type=self.parrot_contenttype)
        tagged_items = queryset
        prefetched_items = queryset

        fetch_content_objects(prefetched_items)

        tagged_objects = [tagged_item.object for tagged_item in tagged_items]
        prefetched_objects = [tagged_item.object for tagged_item in prefetched_items]
        self.assertEquals(set(tagged_objects), set(prefetched_objects))

    def test_select_related_for(self):
        queryset = TaggedItem.objects.all()
        tagged_items = queryset
        prefetched_items = queryset

        fetch_content_objects(prefetched_items, select_related_for=["parrot"])

        tagged_objects = [tagged_item.object for tagged_item in tagged_items]
        prefetched_objects = [tagged_item.object for tagged_item in prefetched_items]
        self.assertEquals(set(tagged_objects), set(prefetched_objects))

    def test_with_many_models(self):
        queryset = TaggedItem.objects.all()
        tagged_items = queryset
        prefetched_items = queryset

        fetch_content_objects(prefetched_items)

        tagged_objects = [tagged_item.object for tagged_item in tagged_items]
        prefetched_objects = [tagged_item.object for tagged_item in prefetched_items]
        self.assertEquals(set(tagged_objects), set(prefetched_objects))
