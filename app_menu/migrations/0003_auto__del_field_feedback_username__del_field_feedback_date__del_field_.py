# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Feedback.username'
        db.delete_column(u'app_menu_feedback', 'username')

        # Deleting field 'Feedback.date'
        db.delete_column(u'app_menu_feedback', 'date')

        # Deleting field 'Feedback.message'
        db.delete_column(u'app_menu_feedback', 'message')

        # Deleting field 'Feedback.email'
        db.delete_column(u'app_menu_feedback', 'email')

        # Deleting field 'Feedback.subject'
        db.delete_column(u'app_menu_feedback', 'subject')

        # Adding field 'Feedback.username_f'
        db.add_column(u'app_menu_feedback', 'username_f',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Feedback.subject_f'
        db.add_column(u'app_menu_feedback', 'subject_f',
                      self.gf('django.db.models.fields.CharField')(default='f', max_length=100),
                      keep_default=False)

        # Adding field 'Feedback.email_f'
        db.add_column(u'app_menu_feedback', 'email_f',
                      self.gf('django.db.models.fields.EmailField')(default=None, max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Feedback.message_f'
        db.add_column(u'app_menu_feedback', 'message_f',
                      self.gf('django.db.models.fields.TextField')(default='df', max_length=50000),
                      keep_default=False)

        # Adding field 'Feedback.date_f'
        db.add_column(u'app_menu_feedback', 'date_f',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 11, 21, 0, 0), auto_now=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Feedback.username'
        db.add_column(u'app_menu_feedback', 'username',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Feedback.date'
        db.add_column(u'app_menu_feedback', 'date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 11, 20, 0, 0)),
                      keep_default=False)

        # Adding field 'Feedback.message'
        db.add_column(u'app_menu_feedback', 'message',
                      self.gf('django.db.models.fields.TextField')(default='df', max_length=50000),
                      keep_default=False)

        # Adding field 'Feedback.email'
        db.add_column(u'app_menu_feedback', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='', max_length=100, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Feedback.subject'
        raise RuntimeError("Cannot reverse this migration. 'Feedback.subject' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Feedback.subject'
        db.add_column(u'app_menu_feedback', 'subject',
                      self.gf('django.db.models.fields.CharField')(max_length=100),
                      keep_default=False)

        # Deleting field 'Feedback.username_f'
        db.delete_column(u'app_menu_feedback', 'username_f')

        # Deleting field 'Feedback.subject_f'
        db.delete_column(u'app_menu_feedback', 'subject_f')

        # Deleting field 'Feedback.email_f'
        db.delete_column(u'app_menu_feedback', 'email_f')

        # Deleting field 'Feedback.message_f'
        db.delete_column(u'app_menu_feedback', 'message_f')

        # Deleting field 'Feedback.date_f'
        db.delete_column(u'app_menu_feedback', 'date_f')


    models = {
        u'app_menu.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'date_f': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 11, 21, 0, 0)', 'auto_now': 'True', 'blank': 'True'}),
            'email_f': ('django.db.models.fields.EmailField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_f': ('django.db.models.fields.TextField', [], {'default': 'None', 'max_length': '50000'}),
            'subject_f': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100'}),
            'username_f': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['app_menu']